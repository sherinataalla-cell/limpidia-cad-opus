"""Controlli sul modello: contenimento, sovrapposizioni, accostamenti, coppie
funzionali, porte, composizione smart, utenze e superfici.

Esiti possibili:
- CONFLITTO            geometria in contrasto (anche solo sotto le ipotesi dichiarate)
- NON_VERIFICABILE     manca un dato necessario: il controllo NON è superato
- COMPATIBILE_IPOTESI  nessun contrasto con le ipotesi attuali, dati non verificati
- SUPERATO             nessun contrasto e tutti i dati usati sono verificati
- AVVISO               segnalazione da valutare
- OK                   relazione dichiarata e coerente (es. accostamento approvato)

Le soglie sono parametri di screening, non requisiti normativi: fruibilità,
accessibilità e sicurezza vanno validate dal tecnico incaricato.
"""
from itertools import combinations

from shapely.geometry import LineString, Polygon, box as sbox

from .model import (bounds, rect_poly, envelope_poly, stair_poly, areas, front_band,
                    door_sweep, smart_layout, weakest, placement_status, STATUS_LABEL)

ACCOSTATO_MM = 60      # tolleranza per riconoscere un accostamento DICHIARATO
PROSSIMITA_MM = 300    # sotto questa distanza due oggetti non dichiarati vengono segnalati
ORDER = {'CONFLITTO': 0, 'NON_VERIFICABILE': 1, 'AVVISO': 2, 'COMPATIBILE_IPOTESI': 3, 'SUPERATO': 4, 'OK': 5}


def _r(id_, cat, outcome, text, value=None, status=None, items=()):
    return {'id': id_, 'cat': cat, 'outcome': outcome, 'text': text, 'mm': value,
            'status': status, 'items': list(items)}


def objects(model):
    """Geometrie con stato per ogni ID usato nei controlli."""
    obj = {}
    for f in model['furniture']:
        obj[f['id']] = {'geom': rect_poly(bounds(f)), 'status': placement_status(f), 'kind': 'mobile', 'item': f}
    for w in model.get('walls', []):
        obj[w['id']] = {'geom': rect_poly(bounds(w)), 'status': w['status'], 'kind': 'muro', 'item': w}
    for z in model['room_features']:
        if z['type'] == 'zone':
            obj[z['id']] = {'geom': rect_poly(bounds(z)), 'status': z['status'], 'kind': 'zona', 'item': z}
        else:
            obj[z['id']] = {'geom': LineString([z['start'], z['end']]), 'status': z['status'], 'kind': 'linea', 'item': z}
    for op in model.get('openings', []):
        obj[op['id']] = {'geom': sbox(op['x0'], op['y'] - 1, op['x1'], op['y'] + 101) if op['y'] > 0
                         else sbox(op['x0'], -1, op['x1'], 0), 'status': op['status'], 'kind': 'porta', 'item': op}
    env = envelope_poly(model)
    xs = [v[0] for v in model['envelope']['vertices']]
    obj['FACCIATA'] = {'geom': LineString([(min(xs), 0), (max(xs), 0)]), 'status': model['envelope']['status'], 'kind': 'facciata'}
    obj['ENVELOPE'] = {'geom': env.exterior, 'status': model['envelope']['status'], 'kind': 'involucro'}
    return obj


def containment(model):
    out = []
    env = envelope_poly(model)
    obstacles = [(w['id'], rect_poly(bounds(w))) for w in model.get('walls', [])]
    obstacles.append(('SCALE', stair_poly(model)))
    for r in model.get('rooms', []):
        obstacles.append((r['id'], Polygon(r['outer'])))
    for f in model['furniture']:
        g = rect_poly(bounds(f))
        if not env.buffer(0.5).covers(g):
            outside = g.difference(env).area / 1e6
            out.append(_r('CONT-' + f['id'], 'contenimento', 'CONFLITTO',
                          f"{f['id']} esce dal poligono del locale ({outside:.3f} m² fuori).", items=[f['id']]))
        for oid, og in obstacles:
            inter = g.intersection(og).area
            if inter > 1:
                out.append(_r(f'INV-{f["id"]}-{oid}', 'contenimento', 'CONFLITTO',
                              f"{f['id']} invade {oid} per {inter/1e6:.3f} m².", items=[f['id'], oid]))
    for p in model['electrical_points']:
        if p['x'] is None:
            continue
        from shapely.geometry import Point
        if not env.buffer(1).covers(Point(p['x'], p['y'])):
            out.append(_r('CONT-' + p['id'], 'contenimento', 'CONFLITTO', f"{p['id']} è fuori dal locale.", items=[p['id']]))
    return out


def _declared(model):
    return {frozenset((a['a'], a['b'])): a for a in model.get('adjacencies', [])}


def proximity(model):
    """Sovrapposizioni sempre; vicinanze strette solo se non dichiarate né funzionali."""
    out = []
    obj = objects(model)
    declared = _declared(model)
    functional = {frozenset((p['a'], p['b'])) for p in model.get('functional_pairs', [])}
    ids = [f['id'] for f in model['furniture']]
    others = ids + [w['id'] for w in model.get('walls', [])] + ['SCALE']
    seen = set()
    for a in ids:
        for b in others:
            key = frozenset((a, b))
            if a == b or key in seen:
                continue
            seen.add(key)
            ga, gb = obj[a]['geom'], obj[b]['geom']
            st = weakest(obj[a]['status'], obj[b]['status'])
            inter = ga.intersection(gb).area
            if inter > 1:
                out.append(_r(f'OVL-{a}-{b}', 'sovrapposizione', 'CONFLITTO',
                              f"{a} e {b} si sovrappongono ({inter/1e6:.3f} m²).", status=st, items=[a, b]))
                continue
            d = ga.distance(gb)
            if key in declared:
                rel = declared[key]['relation']
                if d <= ACCOSTATO_MM:
                    out.append(_r(f'ADJ-{a}-{b}', 'accostamento', 'OK',
                                  f"{a}–{b}: accostamento dichiarato ({rel}), distanza {d:.0f} mm.", d, st, [a, b]))
                else:
                    out.append(_r(f'ADJ-{a}-{b}', 'accostamento', 'AVVISO',
                                  f"{a}–{b}: accostamento dichiarato ({rel}) ma distanza {d:.0f} mm.", d, st, [a, b]))
            elif key in functional:
                continue
            elif d < PROSSIMITA_MM:
                out.append(_r(f'PRX-{a}-{b}', 'prossimità', 'AVVISO',
                              f"{a}–{b}: {d:.0f} mm, relazione non dichiarata (accostamento o passaggio da stabilire).",
                              d, st, [a, b]))
    # Accostamenti dichiarati verso l'involucro
    for key, adj in declared.items():
        if 'ENVELOPE' in key:
            a = next(iter(key - {'ENVELOPE'}))
            d = obj[a]['geom'].distance(obj['ENVELOPE']['geom'])
            outcome = 'OK' if d <= ACCOSTATO_MM else 'AVVISO'
            out.append(_r(f'ADJ-{a}-ENV', 'accostamento', outcome,
                          f"{a}: {adj['relation']}, distanza dal muro {d:.0f} mm.", d, obj[a]['status'], [a]))
    return out


def functional_pairs(model):
    out = []
    obj = objects(model)
    use = model.get('use_assumptions', {})
    screen = use.get('screening_passage', {}).get('value', 900)
    for fp in model.get('functional_pairs', []):
        a, b = fp['a'], fp['b']
        ga, gb = obj[a]['geom'], obj[b]['geom']
        if b == 'P_SAL':
            gb = gb.union(door_sweep(obj[b]['item']))
        st = weakest(obj[a]['status'], obj[b]['status'])
        d = ga.distance(gb)
        if ga.intersection(gb).area > 1:
            out.append(_r(fp['id'], 'uso', 'CONFLITTO', f"{a}–{b} ({fp['function']}): sovrapposizione.", 0, st, [a, b]))
            continue
        missing = [n for n in fp['needs'] if n not in use or use[n].get('value') is None or use[n]['status'] == 'pending']
        notes, used = [], []
        facing = {a: [], b: []}  # fasce d'uso rivolte verso l'altro elemento
        for n in fp['needs']:
            if n in missing:
                continue
            u = use[n]
            for oid, other in ((a, gb), (b, ga)):
                o = obj[oid]
                if o.get('kind') != 'mobile' or oid not in u.get('applies_to', []):
                    continue
                used.append(u['status'])
                item = o['item']
                if n == 'chair_zone':
                    x0, y0, x1, y1 = bounds(item)
                    v = u['value']
                    cands = [(x0 - v, y0, x0, y1), (x1, y0, x1 + v, y1)] if (y1 - y0) >= (x1 - x0) \
                        else [(x0, y0 - v, x1, y0), (x0, y1, x1, y1 + v)]
                else:
                    cands = [front_band(item, u['value'])]
                for bb in cands:
                    if sbox(*bb).distance(other) < d - 1:
                        facing[oid].append((n, u, sbox(*bb)))
        conflict = False
        for oid, other in ((a, gb), (b, ga)):
            for n, u, g in facing[oid]:
                if g.intersection(other).area > 1:
                    conflict = True
                    notes.append(f"{n} di {oid} ({u['value']} mm, {STATUS_LABEL[u['status']]}) interferisce con {b if oid == a else a}")
        for na, ua, g1 in facing[a]:
            for nb, ub, g2 in facing[b]:
                if g1.intersection(g2).area > 1:
                    conflict = True
                    notes.append(f"{na} di {a} e {nb} di {b} si sovrappongono")
        resid = d - sum(u['value'] for side in facing.values() for _, u, _ in side)
        passage = any(k in fp['function'] for k in ('percorso', 'passaggio', 'accesso'))
        if conflict or (passage and not missing and fp['needs'] and resid < screen):
            if not conflict:
                notes.append(f"luce residua stimata {max(resid, 0):.0f} mm sotto la soglia di screening {screen} mm")
            out.append(_r(fp['id'], 'uso', 'CONFLITTO', f"{a}–{b} ({fp['function']}): distanza {d:.0f} mm; " + '; '.join(notes) + '.',
                          d, weakest(st, *used), [a, b]))
        elif missing or not fp['needs']:
            why = ', '.join(missing) if missing else 'nessun criterio documentato (serramento, sporgenze, spessori da rilevare)'
            out.append(_r(fp['id'], 'uso', 'NON_VERIFICABILE', f"{a}–{b} ({fp['function']}): distanza {d:.0f} mm; manca: {why}.",
                          d, st, [a, b]))
        else:
            all_verified = weakest(st, *used) == 'verified'
            out.append(_r(fp['id'], 'uso', 'SUPERATO' if all_verified else 'COMPATIBILE_IPOTESI',
                          f"{a}–{b} ({fp['function']}): distanza {d:.0f} mm, nessuna interferenza con le ipotesi d'uso.",
                          d, weakest(st, *used), [a, b]))
    return out


def doors(model):
    out = []
    obj = objects(model)
    room_walls = {r['id']: [w['id'] for w in model.get('walls', []) if w['id'].startswith('W_' + r['id'][:3])]
                  for r in model.get('rooms', [])}
    for rid, wids in room_walls.items():
        ops = [o for o in model.get('openings', []) if any(w.startswith(o['wall']) for w in wids)]
        if not ops:
            out.append(_r('DOOR-' + rid, 'porte', 'AVVISO', f"{rid}: nessuna porta nel modello.", items=[rid]))
    for op in model.get('openings', []):
        sweep = door_sweep(op)
        hits = []
        for k, o in obj.items():
            if o['kind'] in ('mobile', 'zona') and sweep.intersection(o['geom']).area > 1:
                hits.append(k)
        for w in model.get('walls', []):
            g = rect_poly(bounds(w))
            if sweep.intersection(g).area > 1:
                hits.append(w['id'])
        if hits:
            out.append(_r('SWING-' + op['id'], 'porte', 'CONFLITTO',
                          f"{op['id']}: l'anta in apertura interferisce con {', '.join(hits)}.", status=op['status'], items=[op['id']] + hits))
        else:
            out.append(_r('SWING-' + op['id'], 'porte', 'COMPATIBILE_IPOTESI' if op['status'] != 'verified' else 'SUPERATO',
                          f"{op['id']}: vano {op['opening_width']} mm, anta {op['leaf']} mm ({op['swing']}): nessuna interferenza.",
                          op['opening_width'], op['status'], [op['id']]))
        # Zona di accesso davanti al vano, dal lato opposto all'apertura (profondità di screening)
        depth = model.get('use_assumptions', {}).get('screening_passage', {}).get('value', 900)
        sy = -op['swing_quadrant'][1]
        y0, y1 = sorted((op['y'] + (0 if sy < 0 else 100), op['y'] + (0 if sy < 0 else 100) + sy * depth))
        if op['y'] == 0:
            y0, y1 = -depth, 0  # ingresso: lato strada, fuori dal modello
        appr = sbox(op['x0'], y0, op['x1'], y1)
        blocked = [k for k, o in obj.items() if o['kind'] == 'mobile' and appr.intersection(o['geom']).area > 1]
        if op['y'] > 0:
            if blocked:
                det = []
                for k in blocked:
                    ib = appr.intersection(obj[k]['geom']).bounds
                    det.append(f"{k} ({ib[2]-ib[0]:.0f} × {ib[3]-ib[1]:.0f} mm dentro la zona)")
                out.append(_r('APPR-' + op['id'], 'porte', 'CONFLITTO',
                              f"{op['id']}: nella zona di accesso di {depth} mm davanti al vano: {', '.join(det)}.",
                              status=op['status'], items=[op['id']] + blocked))
            else:
                out.append(_r('APPR-' + op['id'], 'porte', 'COMPATIBILE_IPOTESI',
                              f"{op['id']}: zona di accesso di {depth} mm davanti al vano libera da mobili.", depth, op['status'], [op['id']]))
        if op.get('clear_width') is None:
            out.append(_r('CLEAR-' + op['id'], 'porte', 'NON_VERIFICABILE', f"{op['id']}: luce netta di passaggio non documentata.",
                          status='pending', items=[op['id']]))
    return out


def smart(model):
    if 'smart_wall' not in model:
        return []
    L = smart_layout(model)
    sw = model['smart_wall']
    out = []
    if not L['fits']:
        out.append(_r('SMART-FIT', 'smart', 'CONFLITTO',
                      f"Composizione smart {L['total']} mm + margine {sw['margin_start']} mm non entra nella parete ({L['available']} mm).",
                      L['total'], 'assumed', ['SMART']))
    else:
        out.append(_r('SMART-FIT', 'smart', 'COMPATIBILE_IPOTESI',
                      f"Parete smart {L['available']} mm: composizione {L['total']} mm (4 × {sw['panels']['width']} + 3 × {sw['panels']['gap']}), "
                      f"margini {sw['margin_start']} / {L['available'] - sw['margin_start'] - L['total']} mm.", L['total'], 'assumed', ['SMART']))
    if not L['matches_band']:
        out.append(_r('SMART-BAND', 'smart', 'AVVISO', f"Sviluppo {L['total']} mm diverso dalla fascia S2 di {L['band']} mm.",
                      L['total'], 'assumed', ['SMART']))
    return out


def electrical(model):
    out = []
    furn = {f['id']: f for f in model['furniture']}
    for p in model['electrical_points']:
        if p['x'] is None:
            out.append(_r('EL-' + p['id'], 'utenze', 'NON_VERIFICABILE', f"{p['id']} ({p['service']}): posizione da definire.",
                          status='pending', items=[p['id']]))
            continue
        for fid, f in furn.items():
            x0, y0, x1, y1 = bounds(f)
            if x0 < p['x'] < x1 and y0 < p['y'] < y1:
                out.append(_r('EL-IN-' + p['id'], 'utenze', 'AVVISO',
                              f"{p['id']} cade dentro l'ingombro di {fid}: {p['access']}.", status=p['xy_status'], items=[p['id'], fid]))
        if p['z'] is None:
            out.append(_r('EL-Z-' + p['id'], 'utenze', 'NON_VERIFICABILE', f"{p['id']}: quota Z da rilevare.", status=p['z_status'],
                          items=[p['id']]))
    return out


def area_checks(model):
    a = areas(model)
    out = []
    env = a['involucro (poligono delle facce interne, foro scala incluso)']
    for d in model.get('declared_areas', []):
        out.append(_r('AREA-' + d['id'], 'superfici', 'NON_VERIFICABILE',
                      f"Dato {d['value_m2']} m² ({d['source']}, {d['definition']}) contro {env:.2f} m² del poligono interno: "
                      "è una questione di fonti da riconciliare con il rilievo, la pianta non va riscalata.", status=d['status']))
    sal = a['saletta netta (facce interne dei tramezzi)']
    out.append(_r('AREA-SAL', 'superfici', 'COMPATIBILE_IPOTESI',
                  f"Saletta netta {sal:.2f} m² sulle facce interne dei tramezzi (S1/S3 dichiarano 7,00 m² netti di progetto).",
                  status='assumed'))
    return out


def run_all(model):
    res = containment(model) + proximity(model) + functional_pairs(model) + doors(model) + smart(model) + electrical(model) + area_checks(model)
    res.sort(key=lambda r: (ORDER[r['outcome']], r['cat'], r['id']))
    return res


def findings(model):
    """Compatibilità: elenco (priorità, testo) dei risultati da guardare."""
    pri = {'CONFLITTO': 1, 'NON_VERIFICABILE': 2, 'AVVISO': 2}
    return [(pri[r['outcome']], r['text']) for r in run_all(model) if r['outcome'] in pri]


def clearances(model):
    """Distanze da quotare in pianta: coppie funzionali e accostamenti segnalati."""
    obj = objects(model)
    rows = []
    for r in functional_pairs(model):
        a, b = r['items'][:2]
        ga, gb = obj[a]['geom'], obj[b]['geom']
        if hasattr(ga, 'bounds') and hasattr(gb, 'bounds'):
            rows.append({'id': r['id'], 'a': a, 'b': b, 'mm': r['mm'], 'status': r['status'], 'outcome': r['outcome'],
                         'ra': ga.bounds, 'rb': gb.bounds})
    return rows


LABEL = {'CONFLITTO': 'Conflitto', 'NON_VERIFICABILE': 'Non verificabile (dato mancante)', 'AVVISO': 'Avviso',
         'COMPATIBILE_IPOTESI': 'Compatibile nelle ipotesi attuali', 'SUPERATO': 'Superato su dati verificati', 'OK': 'Coerente con decisione'}


def write_report(model, path):
    res = run_all(model)
    lines = ['# Criticità e verifiche (generato dal modello)', '',
             f"Revisione modello: {model['revision']}. Controlli geometrici e di uso sotto ipotesi dichiarate; "
             "da validare con il tecnico. Un controllo «non verificabile» non è superato.", '',
             '## Riepilogo', '', '| Esito | Numero |', '| --- | ---: |']
    for k in ORDER:
        n = sum(1 for r in res if r['outcome'] == k)
        if n:
            lines.append(f'| {LABEL[k]} | {n} |')
    for cat, title in [('contenimento', 'Contenimento nel locale'), ('sovrapposizione', 'Sovrapposizioni'),
                       ('uso', "Ingombri d'uso e coppie funzionali"), ('porte', 'Porte'), ('accostamento', 'Accostamenti dichiarati'),
                       ('prossimità', 'Prossimità non dichiarate'), ('smart', 'Parete smart'), ('utenze', 'Utenze'), ('superfici', 'Superfici')]:
        rows = [r for r in res if r['cat'] == cat]
        if not rows:
            continue
        lines += ['', f'## {title}', '', '| ID | Esito | Dettaglio | Stato dei dati |', '| --- | --- | --- | --- |']
        for r in rows:
            st = STATUS_LABEL.get(r['status'], '') if r['status'] else ''
            lines.append(f"| {r['id']} | {LABEL[r['outcome']]} | {r['text']} | {st} |")
    lines += ['', '## Superfici', '', '| Definizione | m² |', '| --- | ---: |']
    for k, v in areas(model).items():
        lines.append(f'| {k} | {v:.3f} |')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path
