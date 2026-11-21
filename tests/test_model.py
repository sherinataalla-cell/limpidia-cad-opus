from src.generate import load,generate
import ezdxf


def test_ids_unique():
    m=load(); ids=[x['id'] for x in m['furniture']]
    assert len(ids)==len(set(ids))
    assert len([x for x in ids if x.startswith('C') and x!='CASSA'])==4


def test_units_and_open_quotes():
    m=load();assert m['units']=='mm'
    assert all(p['z'] is None for p in m['electrical_points'])
    assert m['envelope']['status']=='assumed'


def test_generated_dxf():
    folder=generate()
    for f in ('A01_pianta_arredi_preliminare.dxf','E01_punti_utenza_preliminari.dxf'):
        d=ezdxf.readfile(folder/f)
        assert d.header['$INSUNITS']==4
        assert len(d.modelspace())>10
