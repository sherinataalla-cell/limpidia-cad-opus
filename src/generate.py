"""Genera due tavole DXF preliminari dal modello parametrico unico."""
import json
from pathlib import Path
import ezdxf

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'config' / 'geometry.json'
OUT = ROOT / 'outputs'


def load():
    return json.loads(DATA.read_text(encoding='utf-8'))


def new_doc():
    d = ezdxf.new('R2010', setup=True)
    d.header['$INSUNITS'] = 4  # millimetri
    for name, color in [('WALLS',7),('ROOMS_ASSUMED',8),('FURNITURE_ASSUMED',30),('FURNITURE_PENDING',1),('FURNITURE_CATALOG',3),('ELECTRICAL',5),('TEXT',7),('WARNING',1)]:
        d.layers.new(name, dxfattribs={'color': color})
    return d


def rectangle(m, x, y, w, h, layer):
    m.add_lwpolyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],close=True,dxfattribs={'layer':layer})


def label(m, s, x, y, layer='TEXT', height=90):
    m.add_text(s, dxfattribs={'layer':layer,'height':height,'insert':(x,y)})


def draw_base(m, model):
    m.add_lwpolyline(model['envelope']['vertices'],close=True,dxfattribs={'layer':'WALLS'})
    for f in model['room_features']:
        if f['type']=='zone':
            rectangle(m,f['x'],f['y'],f['width'],f['depth'],'ROOMS_ASSUMED')
        else:
            m.add_line(f['start'],f['end'],dxfattribs={'layer':'ROOMS_ASSUMED'})
        label(m,f['id'],f.get('x',f.get('start',[0,0])[0])+60,f.get('y',f.get('start',[0,0])[1])+120)


def generate():
    OUT.mkdir(exist_ok=True)
    model=load()
    d=new_doc();m=d.modelspace();draw_base(m,model)
    for f in model['furniture']:
        status=f['status']
        layer={'assumed':'FURNITURE_ASSUMED','pending':'FURNITURE_PENDING','catalog':'FURNITURE_CATALOG','verified':'FURNITURE_CATALOG'}[status]
        rectangle(m,f['x'],f['y'],f['width'],f['depth'],layer)
        label(m,f['id'],f['x']+40,f['y']+max(95,f['depth']/2),layer,height=75)
    label(m,'PRELIMINARE - NON PER CANTIERE',100,-300,'WARNING',180)
    d.saveas(OUT/'A01_pianta_arredi_preliminare.dxf')

    e=new_doc();em=e.modelspace();draw_base(em,model)
    for f in model['furniture']:
        rectangle(em,f['x'],f['y'],f['width'],f['depth'],'FURNITURE_ASSUMED')
    for p in model['electrical_points']:
        em.add_circle((p['x'],p['y']),75,dxfattribs={'layer':'ELECTRICAL'})
        label(em,p['id'],p['x']+110,p['y']+100,'ELECTRICAL',85)
    label(em,'SIMBOLI UTENZE: NON SONO CIRCUITI O PRESE DEFINITIVE',100,-300,'WARNING',140)
    e.saveas(OUT/'E01_punti_utenza_preliminari.dxf')

    unresolved=[f"- {f['id']}: {f['status']} - {f.get('note','')}" for f in model['furniture'] if f['status']!='verified']
    unresolved += [f"- {p['id']}: Z non verificata; utenza {p['service']}" for p in model['electrical_points'] if p['z'] is None]
    (OUT/'quote_da_rilevare.md').write_text('# Quote aperte e verifiche\n\n'+'\n'.join(unresolved)+'\n',encoding='utf-8')
    return OUT


if __name__=='__main__':
    print(generate())
