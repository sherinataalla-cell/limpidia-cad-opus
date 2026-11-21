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


def test_pdf_and_reports():
    folder = generate()
    for f in ('A01_pianta_arredi_preliminare.pdf', 'E01_punti_utenza_preliminari.pdf', 'criticita.md'):
        assert (folder / f).stat().st_size > 0
    a01 = ezdxf.readfile(folder / 'A01_pianta_arredi_preliminare.dxf')
    assert 'A01' in a01.layouts.names()
    assert len(a01.modelspace().query('DIMENSION')) > 10


def test_checks_flag_known_issues():
    from src.checks import findings
    text = ' '.join(t for _, t in findings(load()))
    assert 'saletta' in text.lower()
    assert 'cassa' in text.lower()


def test_gap():
    from src.model import gap
    assert gap((0, 0, 10, 10), (20, 0, 30, 10)) == (10, 'x')
    assert gap((0, 0, 10, 10), (5, 5, 15, 15))[1] == 'overlap'
