"""Controlli geometrici sul modello: distanze libere, sovrapposizioni, coerenza fonti.

Sono controlli puramente geometrici. La soglia di passaggio è un parametro
di lavoro, non un requisito normativo: fruibilità, accessibilità e sicurezza
vanno validate dal tecnico incaricato.
"""
from itertools import combinations

from .model import bounds, gap, polygon_area, point_in_rect, STATUS_LABEL

PASSAGGIO_MM = 900       # soglia di lavoro per segnalare i passaggi stretti
VICINO_MM = 1200         # oltre questa distanza due elementi non si "fronteggiano"
ACCOSTATO_MM = 60        # sotto questa distanza gli elementi sono accostati di proposito
DICHIARATO_M2 = 45       # piano terra dichiarato nella proposta di locazione


def envelope_box(model):
    xs = [v[0] for v in model['envelope']['vertices']]
    ys = [v[1] for v in model['envelope']['vertices']]
    return min(xs), min(ys), max(xs), max(ys)


def corridor(ra, rb, axis):
    """Rettangolo dello spazio libero tra due elementi affacciati."""
    if axis == 'x':
        lo, hi = (ra, rb) if ra[2] <= rb[0] else (rb, ra)
        return lo[2], max(lo[1], hi[1]), hi[0], min(lo[3], hi[3])
    lo, hi = (ra, rb) if ra[3] <= rb[1] else (rb, ra)
    return max(lo[0], hi[0]), lo[3], min(lo[2], hi[2]), hi[1]


def _intersects(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def clearances(model):
    """Distanze libere tra mobili e verso le zone fisse (scala, saletta).

    Esclude le coppie nascoste da un terzo elemento interposto.
    """
    items = [(f['id'], bounds(f), 'mobile') for f in model['furniture']]
    items += [(z['id'], bounds(z), 'zona') for z in model['room_features'] if z['type'] == 'zone']
    rows = []
    for (ia, ra, ka), (ib, rb, kb) in combinations(items, 2):
        if ka == 'zona' and kb == 'zona':
            continue
        d, axis = gap(ra, rb)
        if axis == 'diag' or d > VICINO_MM:
            continue
        if axis in ('x', 'y') and d > 0:
            c = corridor(ra, rb, axis)
            if any(_intersects(c, r) for i, r, _ in items if i not in (ia, ib)):
                continue
        rows.append({'a': ia, 'b': ib, 'mm': round(d), 'axis': axis, 'ra': ra, 'rb': rb})
    rows.sort(key=lambda r: r['mm'])
    return rows


def findings(model):
    """Elenco ordinato di criticità (priorità, testo)."""
    out = []
    area = polygon_area(model['envelope']['vertices']) / 1e6
    if abs(area - DICHIARATO_M2) > 3:
        out.append((1, f"Perimetro del modello = {area:.1f} m² netti contro {DICHIARATO_M2} m² dichiarati per il piano terra. "
                       "Va chiarito con il rilievo se i 45 m² sono lordi (muri compresi) o se il perimetro ipotizzato è sbagliato."))

    furn = {f['id']: f for f in model['furniture']}
    zones = {z['id']: z for z in model['room_features'] if z['type'] == 'zone'}
    env = envelope_box(model)

    for r in clearances(model):
        if r['mm'] < 0:
            out.append((1, f"{r['a']} e {r['b']} si sovrappongono di {-r['mm']} mm."))
        elif r['mm'] <= ACCOSTATO_MM:
            continue  # accostati di proposito (a muro, affiancati, lungo la ringhiera)
        elif r['mm'] < PASSAGGIO_MM:
            out.append((2, f"Tra {r['a']} e {r['b']} restano {r['mm']} mm (sotto la soglia di lavoro di {PASSAGGIO_MM} mm)."))

    for f in model['furniture']:
        b = bounds(f)
        if b[0] < env[0] or b[1] < env[1] or b[2] > env[2] or b[3] > env[3]:
            out.append((1, f"{f['id']} esce dal perimetro del locale."))

    # Saletta: lato verso il negozio e posizione porta
    if 'SALETTA' in zones:
        s = bounds(zones['SALETTA'])
        front = [furn[k] for k in ('C2', 'C3') if k in furn]
        occ = sorted((bounds(f)[0], bounds(f)[2]) for f in front)
        if occ:
            free_left = occ[0][0] - s[0]
            free_right = s[2] - occ[-1][1]
            out.append((1, f"Porta della saletta non presente nel modello. Sul fronte saletta ({s[2]-s[0]:.0f} mm) "
                           f"le due cassettiere occupano {occ[-1][1]-occ[0][0]:.0f} mm: restano {free_left:.0f} mm a sinistra "
                           f"e {free_right:.0f} mm a destra. La porta, con spallette e luce netta, deve stare in uno di questi tratti."))

    if 'CASSA' in furn and 'SCALE' in zones:
        d, _ = gap(bounds(furn['CASSA']), bounds(zones['SCALE']))
        out.append((1, f"Banco cassa: tra il fronte cassa e la zona scala restano {d:.0f} mm. Se l'operatore sta davanti alla cassa "
                       "non c'è spazio; va definito da che lato lavora e la dimensione reale del prodotto (oggi segnaposto 1200 × 600)."))

    for p in model['electrical_points']:
        for f in model['furniture']:
            if point_in_rect(p['x'], p['y'], bounds(f), tol=-1):
                out.append((3, f"{p['id']} ({p['service']}) cade dentro l'ingombro di {f['id']}: va deciso se è un punto a pavimento "
                               "o a parete e come si raggiunge per la manutenzione."))
        if p['z'] is None:
            pass  # registrate in quote_da_rilevare.md

    pend = [f['id'] for f in model['furniture'] if f['status'] in ('pending', 'assumed')]
    out.append((3, "Mobili con dimensioni non verificate: " + ', '.join(pend) + "."))
    out.sort(key=lambda t: t[0])
    return out


def write_report(model, path):
    pri = {1: 'Alta', 2: 'Media', 3: 'Bassa'}
    lines = ['# Criticità e verifiche (generato dal modello)', '',
             f"Revisione modello: {model['revision']}. Controlli solo geometrici; da validare con il tecnico.", '',
             '| Priorità | Criticità |', '| --- | --- |']
    for p, t in findings(model):
        lines.append(f'| {pri[p]} | {t} |')
    lines += ['', '## Distanze libere tra elementi vicini', '', '| Da | A | Distanza (mm) |', '| --- | --- | --- |']
    for r in clearances(model):
        lines.append(f"| {r['a']} | {r['b']} | {r['mm']} |")
    lines += ['', '## Stato delle quote dei mobili', '', '| ID | L × P (mm) | Stato | Nota |', '| --- | --- | --- | --- |']
    for f in model['furniture']:
        lines.append(f"| {f['id']} | {f['width']} × {f['depth']} | {STATUS_LABEL[f['status']]} | {f.get('note','')} |")
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path
