"""Controlli sul modello: contenimento, ingombri dei componenti, sovrapposizioni,
accostamenti strutturati, coppie funzionali a scenari, requisiti della committenza,
porte (muro ospite e apertura), composizione smart, utenze e superfici.

Esiti possibili:
- CONFLITTO            geometria in contrasto (anche solo sotto le ipotesi dichiarate)
- NON_VERIFICABILE     manca un dato o un criterio necessario: il controllo NON è superato
- COMPATIBILE_IPOTESI  nessun contrasto con le ipotesi attuali, dati non verificati
- SUPERATO             nessun contrasto e TUTTE le dipendenze usate sono verificate
- AVVISO               segnalazione da valutare
- OK                   relazione dichiarata e geometricamente coerente (non certifica l'uso)

Le soglie sono parametri di screening, non requisiti normativi: fruibilità,
accessibilità e sicurezza vanno validate dal tecnico incaricato. La logica usa
solo campi strutturati: le descrizioni libere non cambiano gli esiti.
"""
from shapely.geometry import LineString, Point, Polygon, box as sbox

from .model import (bounds, rect_poly, envelope_poly, stair_poly, areas, front_band, door_sweep, smart_layout,
                    weakest, placement_status, use_bands, guards, product_dims, envelope_edges, outward, room, rooms, STATUS_LABEL)
from .components import all_components, furniture_components, union_bounds, unexplained_overlaps

PROSSIMITA_MM = 300    # sotto questa distanza due oggetti non dichiarati vengono segnalati
ORDER = {'CONFLITTO': 0, 'NON_VERIFICABILE': 1, 'AVVISO': 2, 'COMPATIBILE_IPOTESI': 3, 'SUPERATO': 4, 'OK': 5}
_SIDE_NORMAL = {'x0': (1, 0), 'x1': (-1, 0), 'y0': (0, 1), 'y1': (0, -1)}   # normale del supporto verso il mobile
_FRONT_SIDE = {'-y': 'y0', '+y': 'y1', '-x': 'x0', '+x': 'x1'}


def _r(id_, cat, outcome, text, value=None, status=None, items=(), deps=()):
    return {'id': id_, 'cat': cat, 'outcome': outcome, 'text': text, 'mm': value,
            'status': status, 'items': list(items), 'deps': list(deps)}


def _ok_or_ipotesi(st):
    return 'SUPERATO' if st == 'verified' else 'COMPATIBILE_IPOTESI'


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
    xs = [v[0] for v in model['envelope']['vertices']]
    obj['FACCIATA'] = {'geom': LineString([(min(xs), 0), (max(xs), 0)]), 'status': model['envelope']['status'], 'kind': 'facciata'}
    obj['ENVELOPE'] = {'geom': envelope_poly(model).exterior, 'status': model['envelope']['status'], 'kind': 'involucro'}
    return obj


# --- Contenimento e ingombri ----------------------------------------------------------

def containment(model):
    out = []
    env = envelope_poly(model)
    obstacles = [(w['id'], rect_poly(bounds(w))) for w in model.get('walls', [])]
    obstacles.append(('SCALE', stair_poly(model)))
    for r in rooms(model):
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
        if not env.buffer(1).covers(Point(p['x'], p['y'])):
            out.append(_r('CONT-' + p['id'], 'contenimento', 'CONFLITTO', f"{p['id']} è fuori dal locale.", items=[p['id']]))
    return out


def components_check(model):
    """Ingombri: le parti di ogni mobile stanno nell'ingombro esterno; nessun pezzo compenetra un altro o un muro."""
    out = []
    comps = all_components(model)
    walls = [(w['id'], rect_poly(bounds(w))) for w in model.get('walls', [])]
    env = envelope_poly(model)
    for f in model['furniture']:
        ub = union_bounds(furniture_components(model, f))
        x0, y0, x1, y1 = bounds(f)
        inside = ub[0] >= x0 - 0.01 and ub[1] >= y0 - 0.01 and ub[3] <= x1 + 0.01 and ub[4] <= y1 + 0.01 \
            and ub[2] >= -0.01 and ub[5] <= f['height'] + 0.01
        if inside:
            out.append(_r('ENV-' + f['id'], 'ingombri', 'OK',
                          f"{f['id']}: tutte le parti (corpo, top, zoccolo, frontali) entro l'ingombro esterno "
                          f"{f['width']} × {f['depth']} × {f['height']} mm.", status=f['status'], items=[f['id']]))
        else:
            out.append(_r('ENV-' + f['id'], 'ingombri', 'CONFLITTO',
                          f"{f['id']}: parti fuori dall'ingombro dichiarato (unione {[round(v) for v in ub]}).", items=[f['id']]))
    for a, b in unexplained_overlaps(comps):
        out.append(_r(f'OVL3D-{a}-{b}', 'ingombri', 'CONFLITTO', f"{a} e {b} si compenetrano senza raccordo dichiarato.", items=[a, b]))
    for c in comps:
        g = sbox(c['box'][0], c['box'][1], c['box'][3], c['box'][4])
        if not env.buffer(0.5).covers(g):
            out.append(_r('CONT3D-' + c['id'], 'ingombri', 'CONFLITTO', f"{c['id']} esce dal locale.", items=[c['id']]))
        for wid, wg in walls:
            if g.intersection(wg).area > 1:
                out.append(_r(f'INV3D-{c["id"]}-{wid}', 'ingombri', 'CONFLITTO', f"{c['id']} penetra nel muro {wid}.", items=[c['id'], wid]))
    return out


def decisions_check(model):
    """Vincoli dimensionali di docs/decisioni.md verificabili sul modello."""
    out = []
    isola = next((f for f in model['furniture'] if f['id'] == 'ISOLA_SMART'), None)
    if isola:
        P = product_dims(isola)['P']
        ub = union_bounds(furniture_components(model, isola))
        outer = (ub[3] - ub[0]) if isola['front'] in ('-x', '+x') else (ub[4] - ub[1])
        outcome = 'CONFLITTO' if max(P, outer) > 400 else _ok_or_ipotesi(isola['status'])
        out.append(_r('DEC-ISOLA-P', 'decisioni', outcome,
                      f"Isola: profondità esterna {outer:.0f} mm (prodotto P {P} mm), limite approvato 400 mm.",
                      outer, isola['status'], ['ISOLA_SMART']))
    return out


# --- Accostamenti -----------------------------------------------------------------------

def _side_coord(item, side):
    x0, y0, x1, y1 = bounds(item)
    return {'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1}[side], ((y0, y1) if side[0] == 'x' else (x0, x1))


def _target(model, to, furn):
    """(nome, asse lungo cui corre, coordinata, intervallo, normale verso il mobile o None, stato)."""
    if 'envelope' in to:
        verts = model['envelope']['vertices']
        names = model['envelope']['edge_names']
        a, b = envelope_edges(verts)[names.index(to['envelope'])]
        ox, oy = outward(a, b, verts)
        axis = 'x' if a[1] == b[1] else 'y'
        fixed = a[1] if axis == 'x' else a[0]
        rng = tuple(sorted((a[0], b[0]) if axis == 'x' else (a[1], b[1])))
        return to['envelope'], axis, fixed, rng, (-ox, -oy), model['envelope']['status']
    if 'wall' in to or 'furniture' in to:
        key = 'wall' if 'wall' in to else 'furniture'
        item = next(w for w in model['walls'] if w['id'] == to['wall']) if key == 'wall' else furn[to['furniture']]
        c, rng = _side_coord(item, to['side'])
        axis = 'x' if to['side'][0] == 'y' else 'y'
        n = {'x0': (-1, 0), 'x1': (1, 0), 'y0': (0, -1), 'y1': (0, 1)}[to['side']]
        st = item['status'] if key == 'wall' else placement_status(item)
        return f"{to[key]} lato {to['side']}", axis, c, rng, n, st
    if 'line' in to:
        z = next(z for z in model['room_features'] if z['id'] == to['line'])
        (ax_, ay), (bx, by) = z['start'], z['end']
        axis = 'x' if ay == by else 'y'
        fixed = ay if axis == 'x' else ax_
        rng = tuple(sorted((ax_, bx) if axis == 'x' else (ay, by)))
        return to['line'] + ' (asse)', axis, fixed, rng, None, z['status']
    raise KeyError(to)


def adjacency(model):
    """Accostamento al supporto e al lato dichiarati: lato, parallelismo, verso, distanza, tratto di affaccio."""
    out = []
    furn = {f['id']: f for f in model['furniture']}
    for adj in model.get('adjacencies', []):
        f = furn[adj['a']]
        side = adj['side']
        name, axis, fixed, rng, n, tst = _target(model, adj['to'], furn)
        c, frng = _side_coord(f, side)
        st = weakest(placement_status(f), tst)
        why = []
        if _FRONT_SIDE[f['front']] == side:
            why.append(f"il lato {side} è il fronte del mobile")
        if (side[0] == 'y') != (axis == 'x'):
            why.append(f"lato {side} non parallelo a {name}")
        if n is not None and n != _SIDE_NORMAL[side]:
            why.append(f"il supporto {name} non sta dal lato {side} del mobile")
        d = abs(c - fixed)
        if d > adj['tolerance']:
            why.append(f"distanza {d:.0f} mm oltre la tolleranza della relazione ({adj['tolerance']} mm)")
        ov = min(frng[1], rng[1]) - max(frng[0], rng[0])
        if ov <= 0:
            why.append(f"nessun tratto di affaccio su {name}")
        txt = f"{adj['a']} lato {side} → {name} ({adj['relation']}): distanza {d:.0f} mm, tratto di affaccio {max(ov, 0):.0f} mm"
        if why:
            out.append(_r(adj['id'], 'accostamento', 'CONFLITTO', txt + '; ' + '; '.join(why) + '.', d, st, [adj['a']]))
        else:
            out.append(_r(adj['id'], 'accostamento', 'OK', txt + '. Solo vincolo geometrico: posto operatore e uso a parte.',
                          d, st, [adj['a']]))
    return out


def proximity(model):
    """Sovrapposizioni sempre; vicinanze strette solo se non dichiarate né funzionali."""
    out = []
    obj = objects(model)
    declared = set()
    for a in model.get('adjacencies', []):
        t = a['to'].get('furniture') or a['to'].get('wall')
        if t:
            declared.add(frozenset((a['a'], t)))
        if a.get('also_declares'):   # es. isola lungo la ringhiera: copre anche la zona scala
            declared.add(frozenset((a['a'], a['also_declares'])))
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
            if key in declared or key in functional:
                continue
            d = ga.distance(gb)
            if d < PROSSIMITA_MM:
                out.append(_r(f'PRX-{a}-{b}', 'prossimità', 'AVVISO',
                              f"{a}–{b}: {d:.0f} mm, relazione non dichiarata (accostamento o passaggio da stabilire).",
                              d, st, [a, b]))
    return out


# --- Coppie funzionali a scenari ---------------------------------------------------------

def _bands(model, obj, oid, n, u, other, d):
    """Fasce d'uso di oid rivolte verso l'altro elemento (riducono la distanza)."""
    o = obj[oid]
    if o.get('kind') != 'mobile' or oid not in u.get('applies_to', []):
        return []
    cands = use_bands(o['item'], n, u['value'], model.get('use_assumptions', {}))
    return [(n, u, sbox(*bb)) for bb in cands if sbox(*bb).distance(other) < d - 1]


def _scenario(model, obj, a, b, ga, gb, d, sc):
    use = model.get('use_assumptions', {})
    missing = [n for n in sc['uses'] if n not in use or use[n].get('value') is None or use[n]['status'] == 'pending']
    if missing:
        return {'name': sc['name'], 'missing': missing, 'collision': False, 'alt': False, 'resid': None, 'notes': [], 'used': []}
    facing = {a: [], b: []}
    for n in sc['uses']:
        u = use[n]
        facing[a] += _bands(model, obj, a, n, u, gb, d)
        facing[b] += _bands(model, obj, b, n, u, ga, d)
    notes, coll = [], False
    for oid, other, oname in ((a, gb, b), (b, ga, a)):
        for n, u, g in facing[oid]:
            if g.intersection(other).area > 1:
                coll = True
                notes.append(f"{n} di {oid} ({u['value']} mm) interferisce con {oname}")
    alt = False
    occasional = sc.get('mode') == 'occasionale'
    for na, ua, g1 in facing[a]:
        for nb, ub, g2 in facing[b]:
            if g1.intersection(g2).area > 1:
                if occasional:
                    # azioni alternative, non richieste insieme: non e' una collisione fisica
                    alt = True
                    notes.append(f"{na} di {a} e {nb} di {b} si sovrappongono: azioni alternative, "
                                 "possibile breve spostamento da verificare con la seduta reale")
                else:
                    coll = True
                    notes.append(f"{na} di {a} e {nb} di {b} si sovrappongono")
    used = [u['status'] for side in facing.values() for _, u, _ in side]
    # residuo geometrico fra ingombri statici più fasce d'uso (vale anche per coppie in diagonale)
    from shapely.ops import unary_union
    ea = unary_union([ga] + [g for _, _, g in facing[a]])
    eb = unary_union([gb] + [g for _, _, g in facing[b]])
    resid = 0.0 if (coll or alt) else ea.distance(eb)
    return {'name': sc['name'], 'missing': [], 'collision': coll, 'alt': alt, 'resid': resid, 'notes': notes, 'used': used}


def functional_pairs(model):
    out = []
    obj = objects(model)
    use = model.get('use_assumptions', {})
    for fp in model.get('functional_pairs', []):
        a, b = fp['a'], fp['b']
        ga, gb = obj[a]['geom'], obj[b]['geom']
        if obj[b].get('kind') == 'porta':
            gb = gb.union(door_sweep(obj[b]['item']))
        st = weakest(obj[a]['status'], obj[b]['status'])
        d = ga.distance(gb)
        if ga.intersection(gb).area > 1:
            out.append(_r(fp['id'], 'uso', 'CONFLITTO', f"{a}–{b} ({fp['function']}): sovrapposizione.", 0, st, [a, b]))
            continue
        res = [_scenario(model, obj, a, b, ga, gb, d, sc) for sc in fp.get('scenarios', [])]
        desc = '; '.join(f"{r['name']}: " + (f"manca {', '.join(r['missing'])}" if r['missing'] else
                                              f"residuo {r['resid']:.0f} mm" + (' — ' + ', '.join(r['notes']) if r['notes'] else ''))
                         for r in res)
        used = [s for r in res for s in r['used']]
        stt = weakest(st, *used)
        head = f"{a}–{b} ({fp['function']}): distanza statica {d:.0f} mm"
        if any(r['collision'] for r in res):
            out.append(_r(fp['id'], 'uso', 'CONFLITTO', f"{head}; {desc}.", d, stt, [a, b]))
        elif not res:
            out.append(_r(fp['id'], 'uso', 'NON_VERIFICABILE',
                          f"{head}; manca il criterio: {fp.get('criterion_missing', 'da definire')}.", d, st, [a, b]))
        elif any(r['missing'] for r in res):
            out.append(_r(fp['id'], 'uso', 'NON_VERIFICABILE', f"{head}; {desc}.", d, stt, [a, b]))
        elif any(r.get('alt') for r in res):
            out.append(_r(fp['id'], 'uso', 'AVVISO', f"{head}; {desc}. Nessuna collisione fisica: sovrapposizione fra "
                          "azioni alternative da verificare con seduta e cassetto reali.", d, stt, [a, b]))
        else:
            out.append(_r(fp['id'], 'uso', _ok_or_ipotesi(stt),
                          f"{head}; {desc}. Esito limitato alla non sovrapposizione degli ingombri d'uso.", d, stt, [a, b]))
        path = fp.get('path', {})
        if path.get('required'):
            sc = next((r for r in res if r['name'] == path.get('scenario')), None)
            pid = fp['id'] + '-PERCORSO'
            crit = path.get('criterion')
            if sc is None or sc['missing']:
                out.append(_r(pid, 'uso', 'NON_VERIFICABILE', f"{a}–{b}: percorso/accesso, scenario «{path.get('scenario')}» senza dati.",
                              None, stt, [a, b]))
            elif crit is None or use.get(crit, {}).get('value') is None:
                out.append(_r(pid, 'uso', 'NON_VERIFICABILE',
                              f"{a}–{b}: percorso/accesso nello scenario «{sc['name']}»: residuo {sc['resid']:.0f} mm; "
                              f"criterio di passaggio e simultaneità degli usi non stabiliti ({path.get('note', '')}).",
                              sc['resid'], stt, [a, b]))
            else:
                thr = use[crit]['value']
                ok = sc['resid'] >= thr
                out.append(_r(pid, 'uso', _ok_or_ipotesi(weakest(stt, use[crit]['status'])) if ok else 'CONFLITTO',
                              f"{a}–{b}: percorso/accesso nello scenario «{sc['name']}»: residuo {sc['resid']:.0f} mm "
                              f"{'≥' if ok else '<'} soglia di screening {thr} mm (parametro di progetto, non requisito normativo).",
                              sc['resid'], weakest(stt, use[crit]['status']), [a, b]))
    return out


def use_open(model):
    """Ingombri d'uso dichiarati ma ancora da definire: la verifica va eseguita, non omessa."""
    out = []
    for k, u in model.get('use_assumptions', {}).items():
        if isinstance(u, dict) and u.get('applies_to') and (u.get('value') is None or u['status'] == 'pending'):
            out.append(_r('USE-' + k, 'uso', 'NON_VERIFICABILE',
                          f"{k} per {', '.join(u['applies_to'])}: {u.get('note', '')}; verifica da eseguire con il dato.",
                          status='pending', items=u['applies_to']))
    return out


# --- Requisiti della committenza ------------------------------------------------------------

def requirements(model):
    out = []
    comps = all_components(model)
    furn = {f['id']: f for f in model['furniture']}
    for req in model.get('requirements', []):
        if req['type'] != 'clear_distance':
            continue
        stair = next(z for z in model['room_features'] if z['id'] == req['a'])
        rails = guards(model, req['a'])   # tutte le protezioni, non solo la prima linea
        ga = rect_poly(bounds(stair))
        cs = [c for c in comps if c['owner'] == req['b']]
        ub = union_bounds(cs)
        gb = sbox(ub[0], ub[1], ub[3], ub[4])   # ingombro completo della cassa (top compreso)
        d_hole = ga.distance(gb)
        f = furn[req['b']]
        st = weakest(stair['status'], placement_status(f), f['status'])
        th_def = model.get('use_assumptions', {}).get('railing_thickness', {}).get('value')
        ths = {r['id']: (r.get('thickness') if r.get('thickness') is not None else th_def) for r in rails}
        unknown = [rid for rid, t in ths.items() if t is None]
        target = req['target']
        info = (f"luce netta {d_hole:.0f} mm fra {req['a']} (bordo del foro) e ingombro completo di {req['b']}; "
                f"richiesta committenza ≥ {req['min']} mm, obiettivo {target[0]}–{target[1]} mm")
        if d_hole < req['min']:
            extra = ''
            if gb.bounds[1] >= ga.bounds[3]:
                avail = envelope_poly(model).bounds[3] - ga.bounds[3]
                P = gb.bounds[3] - gb.bounds[1]
                extra = (f". Fascia fra fine scala e fondo {avail:.0f} mm; servono {P + req['min']:.0f}–{P + target[1]:.0f} mm "
                         f"con questo banco: mancano {P + req['min'] - avail:.0f}–{P + target[1] - avail:.0f} mm")
            out.append(_r('REQ-' + req['id'], 'requisiti', 'CONFLITTO', f"{info}: insufficiente{extra}.", d_hole, st,
                          [req['a'], req['b']]))
            continue
        if not rails or unknown:
            what = ('protezioni non modellate' if not rails else
                    f"spessore e sporgenze non rilevati per {', '.join(unknown)}")
            out.append(_r('REQ-' + req['id'], 'requisiti', 'NON_VERIFICABILE',
                          f"{info}: criterio numerico soddisfatto sul solo foro, ma sagoma, estremità e spessore di "
                          f"parapetto/corrimano da rilevare ({what}): la luce reale può essere minore. È una distanza minima fra "
                          "ingombri, non la larghezza di un percorso.", d_hole, st, [req['a'], req['b']] + [r['id'] for r in rails]))
            continue
        # ingombro fisico: foro scala + ogni protezione lungo la sua linea reale, estremità comprese
        from shapely.ops import unary_union
        phys = unary_union([ga] + [LineString([tuple(r['start']), tuple(r['end'])]).buffer(ths[r['id']] / 2, cap_style='square')
                                   for r in rails])
        d = phys.distance(gb)
        st = weakest(st, *[r['status'] for r in rails])
        rail = {'id': '+'.join(r['id'] for r in rails)}
        if d < req['min']:
            out.append(_r('REQ-' + req['id'], 'requisiti', 'CONFLITTO',
                          f"{info}; dall'ingombro fisico di scala e ringhiera (estremità comprese) {d:.0f} mm: insufficiente.",
                          d, st, [req['a'], req['b'], rail['id']]))
        else:
            out.append(_r('REQ-' + req['id'], 'requisiti', _ok_or_ipotesi(st),
                          f"{info}; dall'ingombro fisico di scala e ringhiera {d:.0f} mm"
                          + (f"; oltre {target[1]} mm: da motivare nel layout" if d > target[1] else '')
                          + '. Solo distanza minima a banco chiuso: percorso, operatore e usi adiacenti a parte.',
                          d, st, [req['a'], req['b'], rail['id']]))
    return out


def stair_access(model):
    """Accesso alla scala dal lato dichiarato: fascia libera davanti all'imbocco (ipotesi di screening)."""
    out = []
    use = model.get('use_assumptions', {})
    sp = use.get('screening_passage', {})
    for z in model['room_features']:
        side = z.get('access_side')
        if z['type'] != 'zone' or not side:
            continue
        x0, y0, x1, y1 = bounds(z)
        v = sp.get('value')
        st = weakest(z['status'], z.get('access_status', 'assumed'), sp.get('status'))
        if v is None:
            out.append(_r('ACC-' + z['id'], 'uso', 'NON_VERIFICABILE', f"Accesso a {z['id']}: profondità di sbarco non definita.",
                          status='pending', items=[z['id']]))
            continue
        zone = sbox(*{'-y': (x0, y0 - v, x1, y0), '+y': (x0, y1, x1, y1 + v),
                      '-x': (x0 - v, y0, x0, y1), '+x': (x1, y0, x1 + v, y1)}[side])
        hits = []
        for f in model['furniture']:
            bands = [sbox(*bounds(f))] + [sbox(*b) for k, u in use.items()
                                          if isinstance(u, dict) and f['id'] in u.get('applies_to', []) and u.get('value') is not None
                     and u.get('status') != 'pending'
                                          for b in use_bands(f, k, u['value'], use)]
            if any(g.intersection(zone).area > 1 for g in bands):
                hits.append(f['id'])
        if hits:
            out.append(_r('ACC-' + z['id'], 'uso', 'CONFLITTO',
                          f"Accesso a {z['id']} dal lato {side} ({z.get('access_source', '')}): la fascia di sbarco di {v} mm "
                          f"(soglia di screening) è occupata da {', '.join(hits)}.", 0, st, [z['id']] + hits))
        else:
            out.append(_r('ACC-' + z['id'], 'uso', _ok_or_ipotesi(st),
                          f"Accesso a {z['id']} dal lato {side} ({z.get('access_source', '')}): fascia di sbarco {v} mm × "
                          f"{x1 - x0 if side in ('-y', '+y') else y1 - y0} mm libera da mobili e fasce d'uso nelle ipotesi. "
                          "Soglia di screening, non verifica normativa; gradini, alzate e corrimano da rilevare.", v, st, [z['id']]))
    return out


def guard_clearance(model):
    """Mobili e fasce d'uso vicino a TUTTE le protezioni della scala (non solo la prima linea)."""
    out = []
    use = model.get('use_assumptions', {})
    th_def = use.get('railing_thickness', {}).get('value')
    for g in [z for z in model['room_features'] if z['type'] == 'line']:
        axis = LineString([tuple(g['start']), tuple(g['end'])])
        th = g.get('thickness') if g.get('thickness') is not None else th_def
        for f in model['furniture']:
            body = sbox(*bounds(f))
            bands = [(k, u, sbox(*b)) for k, u in use.items()
                     if isinstance(u, dict) and f['id'] in u.get('applies_to', []) and u.get('value') is not None
                     and u.get('status') != 'pending'
                     for b in use_bands(f, k, u['value'], use)]
            d_body = body.distance(axis)
            d_use = min([d_body] + [b.distance(axis) for _, _, b in bands])
            if d_use >= PROSSIMITA_MM:
                continue
            if any(fr.get('a') == f['id'] and fr.get('to', {}).get('line') == g['id'] for fr in model.get('adjacencies', [])):
                continue   # accostamento dichiarato (es. isola lungo la ringhiera): verificato in ADJ/FP07
            st = weakest(g['status'], placement_status(f), *[u['status'] for _, u, _ in bands])
            rid = f"PROT-{f['id']}-{g['id']}"
            txt = (f"{f['id']} verso la protezione {g['id']}: {d_body:.0f} mm a mobile chiuso, {d_use:.0f} mm con le fasce d'uso, "
                   "misurati dall'asse della protezione")
            if d_use <= 0:
                out.append(_r(rid, 'uso', 'CONFLITTO', txt + ': interferenza.', d_use, st, [f['id'], g['id']]))
            elif th is None:
                out.append(_r(rid, 'uso', 'NON_VERIFICABILE', txt + '; spessore, sporgenze e tracciato della protezione da '
                              'rilevare: la distanza reale è minore. Non dimostra l\'uso del mobile.', d_use, st, [f['id'], g['id']]))
            else:
                net = d_use - th / 2
                out.append(_r(rid, 'uso', 'CONFLITTO' if net <= 0 else _ok_or_ipotesi(st),
                              txt + f'; dal filo della protezione {net:.0f} mm.', net, st, [f['id'], g['id']]))
    return out


# --- Porte -------------------------------------------------------------------------------------

def _door_host(model, op):
    """Problemi di collocazione: muro ospite, vano, cerniera, anta e verso documentato."""
    why, deps = [], [op['status']]
    w = op['x1'] - op['x0']
    if op.get('opening_width') is not None and abs(w - op['opening_width']) > 1:
        why.append(f"vano {op['x0']}–{op['x1']} = {w} mm diverso dalla larghezza nominale {op['opening_width']} mm")
    host = op.get('host', {})
    thick = 0
    if 'facade' in host:
        deps.append(model['envelope']['status'])
        el = next((e for e in model.get('facade', []) if e['id'] == host['facade']), None)
        xs = [v[0] for v in model['envelope']['vertices']]
        if op['y'] != 0 or op['x0'] < min(xs) or op['x1'] > max(xs):
            why.append(f"vano fuori dalla facciata (0–{max(xs)} mm a y=0)")
        if el is None or el['type'] != 'door' or (el['x0'], el['x1']) != (op['x0'], op['x1']):
            why.append(f"vano non coincidente con l'elemento di facciata {host['facade']}")
    elif 'walls_prefix' in host:
        ws = [w_ for w_ in model.get('walls', []) if w_['id'].startswith(host['walls_prefix'])]
        deps += [w_['status'] for w_ in ws]
        if not ws:
            why.append(f"nessun muro ospite {host['walls_prefix']}*")
        else:
            thick = ws[0]['depth']
            if any(w_['y'] != op['y'] for w_ in ws):
                why.append(f"il vano non è sulla linea del muro ospite (y {op['y']})")
            left = any(abs(w_['x'] + w_['width'] - op['x0']) <= 1 for w_ in ws)
            right = any(abs(w_['x'] - op['x1']) <= 1 for w_ in ws)
            if not (left and right):
                why.append("il vano non è delimitato dai tratti del muro ospite")
            r = room(model, host['room'])
            rx = [p[0] for p in r['outer']]
            if op['x0'] < min(rx) or op['x1'] > max(rx):
                why.append("vano fuori dal fronte della stanza")
            deps.append(r['status'])
    else:
        why.append('muro ospite non dichiarato')
    if op.get('hinge') is None or op.get('leaf') is None or op.get('swing_quadrant') is None:
        return why, deps, True
    hx, hy = op['hinge']
    if not (op['x0'] - 1 <= hx <= op['x1'] + 1) or min(abs(hx - op['x0']), abs(hx - op['x1'])) > 60:
        why.append(f"cerniera x {hx} non su una spalla del vano")
    if not any(abs(hy - yy) <= 1 for yy in (op['y'], op['y'] + thick)):
        why.append(f"cerniera y {hy} non su una faccia del muro")
    if op['leaf'] > w + 1:
        why.append(f"anta {op['leaf']} mm più larga del vano {w} mm")
    if op.get('clear_width') is not None and op['clear_width'] > w:
        why.append(f"luce utile {op['clear_width']} mm maggiore del vano")
    c = door_sweep(op).centroid
    into = op.get('swing_into')
    if into == 'NEGOZIO' and not envelope_poly(model).contains(c):
        why.append("l'anta non apre verso l'interno del negozio come documentato")
    elif into and into != 'NEGOZIO' and not Polygon(room(model, into)['net']).contains(c):
        why.append(f"l'anta non apre verso {into} come documentato")
    return why, deps, False


def doors(model):
    out = []
    obj = objects(model)
    for r in rooms(model):
        if not any(o.get('host', {}).get('room') == r['id'] for o in model.get('openings', [])):
            out.append(_r('DOOR-' + r['id'], 'porte', 'AVVISO', f"{r['id']}: nessuna porta nel modello.", items=[r['id']]))
    use = model.get('use_assumptions', {})
    for op in model.get('openings', []):
        why, deps, missing = _door_host(model, op)
        if why:
            out.append(_r('HOST-' + op['id'], 'porte', 'CONFLITTO',
                          f"{op['id']}: collocazione incoerente: {'; '.join(why)}. Apertura non valutata.", status=weakest(*deps),
                          items=[op['id']], deps=deps))
            continue
        checked = 'vano e muro ospite coerenti' + ('' if missing else '; cerniera, anta e verso coerenti')
        out.append(_r('HOST-' + op['id'], 'porte', 'OK',
                      f"{op['id']}: {checked}" + ('; cerniera/anta/verso non documentati, non valutati.' if missing else '.'),
                      status=weakest(*deps), items=[op['id']], deps=deps))
        if missing:
            out.append(_r('SWING-' + op['id'], 'porte', 'NON_VERIFICABILE', f"{op['id']}: anta o cerniera non documentate.",
                          status='pending', items=[op['id']]))
            continue
        sweep = door_sweep(op)
        zone = sweep.buffer(300)
        hits, sdeps = [], list(deps)
        for k, o in obj.items():
            if o['kind'] in ('mobile', 'zona', 'muro') and o['geom'].intersects(zone):
                sdeps.append(o['status'])
                if sweep.intersection(o['geom']).area > 1:
                    hits.append(k)
        stt = weakest(*sdeps)
        if hits:
            out.append(_r('SWING-' + op['id'], 'porte', 'CONFLITTO',
                          f"{op['id']}: l'anta in apertura interferisce con {', '.join(hits)} (dati: {STATUS_LABEL[stt]}).",
                          status=stt, items=[op['id']] + hits, deps=sdeps))
        else:
            out.append(_r('SWING-' + op['id'], 'porte', _ok_or_ipotesi(stt),
                          f"{op['id']}: vano {op['opening_width']} mm, anta {op['leaf']} mm ({op['swing']}): nessuna interferenza; "
                          f"stato delle dipendenze (porta, muro, ostacoli vicini): {STATUS_LABEL[stt]}.",
                          op['opening_width'], stt, [op['id']], sdeps))
        # zona di accesso davanti al vano, dal lato opposto all'apertura
        if op['y'] > 0:
            sp = use.get('screening_passage', {})
            depth = sp.get('value')
            if depth is None:
                out.append(_r('APPR-' + op['id'], 'porte', 'NON_VERIFICABILE', f"{op['id']}: criterio di accesso non definito.",
                              items=[op['id']]))
            else:
                sy = -op['swing_quadrant'][1]
                base = op['y'] + (0 if sy < 0 else 100)
                y0, y1 = sorted((base, base + sy * depth))
                appr = sbox(op['x0'], y0, op['x1'], y1)
                blocked = [k for k, o in obj.items() if o['kind'] == 'mobile' and appr.intersection(o['geom']).area > 1]
                # dipendenze: anche i mobili vicini che determinano l'esito (posa e stato), non solo quelli che interferiscono
                near = [k for k, o in obj.items() if o['kind'] == 'mobile' and o['geom'].distance(appr) <= 300]
                adeps = list(deps) + [sp['status']] + [obj[k]['status'] for k in near]
                if blocked:
                    det = []
                    for k in blocked:
                        ib = appr.intersection(obj[k]['geom']).bounds
                        det.append(f"{k} ({ib[2]-ib[0]:.0f} × {ib[3]-ib[1]:.0f} mm dentro la zona)")
                    out.append(_r('APPR-' + op['id'], 'porte', 'CONFLITTO',
                                  f"{op['id']}: nella zona di accesso di {depth} mm davanti al vano (screening): {', '.join(det)}.",
                                  status=weakest(*adeps), items=[op['id']] + blocked, deps=adeps))
                else:
                    out.append(_r('APPR-' + op['id'], 'porte', _ok_or_ipotesi(weakest(*adeps)),
                                  f"{op['id']}: zona di accesso di {depth} mm davanti al vano libera da mobili"
                                  + (f" (vicini: {', '.join(near)})" if near else '') + '.', depth,
                                  weakest(*adeps), [op['id']], adeps))
        if op.get('clear_width') is None:
            out.append(_r('CLEAR-' + op['id'], 'porte', 'NON_VERIFICABILE', f"{op['id']}: luce netta di passaggio non documentata.",
                          status='pending', items=[op['id']]))
    return out


# --- Smart, utenze, superfici -------------------------------------------------------------------

def smart(model):
    if 'smart_wall' not in model:
        return []
    L = smart_layout(model)
    sw = model['smart_wall']
    p = sw['panels']
    out = []
    txt = (f"Parete smart {L['available']} mm: {p['count']} telai esterni da {L['frame']} mm (immagine {L['image']} mm), "
           f"distanza libera fra telai {L['clear_gap']} mm, interasse {L['interaxis']} mm; sviluppo dei telai {L['total']} mm; "
           f"margini {sw['margin_start']} / {L['margin_end']} mm.")
    if not L['fits']:
        out.append(_r('SMART-FIT', 'smart', 'CONFLITTO', 'Composizione oltre la parete: ' + txt, L['total'], 'assumed', ['SMART']))
    else:
        out.append(_r('SMART-FIT', 'smart', 'COMPATIBILE_IPOTESI', txt, L['total'], 'assumed', ['SMART']))
    if not L['matches_band']:
        out.append(_r('SMART-BAND', 'smart', 'AVVISO', f"Sviluppo dei telai {L['total']} mm diverso dalla fascia S2 di {L['band']} mm.",
                      L['total'], 'assumed', ['SMART']))
    if sw.get('images', {}).get('status') != 'verified':
        out.append(_r('SMART-IMG', 'smart', 'NON_VERIFICABILE', f"Immagini dei pannelli: {sw['images']['note']}.", status='pending',
                      items=['SMART']))
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
                opts = ' / '.join(p.get('connection_options', [])) or p['access']
                out.append(_r('EL-IN-' + p['id'], 'utenze', 'AVVISO',
                              f"{p['id']} cade dentro l'ingombro di {fid}: alternative {opts}. {p.get('decision', '')}",
                              status=p['xy_status'], items=[p['id'], fid]))
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
    res = (containment(model) + components_check(model) + decisions_check(model) + adjacency(model) + proximity(model)
           + functional_pairs(model) + use_open(model) + requirements(model) + stair_access(model) + guard_clearance(model) + doors(model) + smart(model)
           + electrical(model) + area_checks(model))
    res.sort(key=lambda r: (ORDER[r['outcome']], r['cat'], r['id']))
    return res


def findings(model):
    """Compatibilità: elenco (priorità, testo) dei risultati da guardare."""
    pri = {'CONFLITTO': 1, 'NON_VERIFICABILE': 2, 'AVVISO': 2}
    return [(pri[r['outcome']], r['text']) for r in run_all(model) if r['outcome'] in pri]


def clearances(model):
    """Distanze da quotare in pianta: coppie funzionali."""
    obj = objects(model)
    rows = []
    for r in functional_pairs(model):
        if r['id'].endswith('-PERCORSO'):
            continue
        a, b = r['items'][:2]
        ga, gb = obj[a]['geom'], obj[b]['geom']
        rows.append({'id': r['id'], 'a': a, 'b': b, 'mm': r['mm'], 'status': r['status'], 'outcome': r['outcome'],
                     'ra': ga.bounds, 'rb': gb.bounds})
    return rows


LABEL = {'CONFLITTO': 'Conflitto', 'NON_VERIFICABILE': 'Non verificabile (dato mancante)', 'AVVISO': 'Avviso',
         'COMPATIBILE_IPOTESI': 'Compatibile nelle ipotesi attuali', 'SUPERATO': 'Superato su dati verificati',
         'OK': 'Coerente (solo geometria)'}

SECTIONS = [('requisiti', 'Requisiti della committenza'), ('contenimento', 'Contenimento nel locale'),
            ('ingombri', 'Ingombri dei componenti (pianta = abaco = render)'), ('decisioni', 'Vincoli approvati'),
            ('sovrapposizione', 'Sovrapposizioni'), ('uso', "Ingombri d'uso, scenari e percorsi"), ('porte', 'Porte'),
            ('accostamento', 'Accostamenti dichiarati (muro e lato)'), ('prossimità', 'Prossimità non dichiarate'),
            ('smart', 'Parete smart'), ('utenze', 'Utenze'), ('superfici', 'Superfici')]


def write_report(model, path):
    res = run_all(model)
    lines = ['# Criticità e verifiche (generato dal modello)', '',
             f"Revisione modello: {model['revision']}. Controlli geometrici e di uso sotto ipotesi dichiarate; "
             "da validare con il tecnico. Un controllo «non verificabile» non è superato; «coerente» riguarda solo la geometria.", '',
             '## Riepilogo', '', '| Esito | Numero |', '| --- | ---: |']
    for k in ORDER:
        n = sum(1 for r in res if r['outcome'] == k)
        if n:
            lines.append(f'| {LABEL[k]} | {n} |')
    for cat, title in SECTIONS:
        rows = [r for r in res if r['cat'] == cat]
        if not rows:
            continue
        if cat == 'ingombri':
            bad = [r for r in rows if r['outcome'] != 'OK']
            lines += ['', f'## {title}', '', f"{len(rows) - len(bad)} controlli coerenti su {len(rows)}."]
            rows = bad
            if not rows:
                continue
        lines += ['', f'## {title}', '', '| ID | Esito | Dettaglio | Stato dei dati |', '| --- | --- | --- | --- |'] if cat != 'ingombri' \
            else ['', '| ID | Esito | Dettaglio | Stato dei dati |', '| --- | --- | --- | --- |']
        for r in rows:
            st = STATUS_LABEL.get(r['status'], '') if r['status'] else ''
            lines.append(f"| {r['id']} | {LABEL[r['outcome']]} | {r['text']} | {st} |")
    lines += ['', '## Superfici', '', '| Definizione | m² |', '| --- | ---: |']
    for k, v in areas(model).items():
        lines.append(f'| {k} | {v:.3f} |')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path
