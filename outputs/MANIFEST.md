# Manifesto degli elaborati generati

Revisione modello P04, generati il 2026-11-23 con `python -m src.generate`. Tutte le tavole sono PRELIMINARE - NON PER CANTIERE; DXF in mm 1:1, PDF A3 da stampare al 100%.

| Codice | Contenuto | Scala di stampa | File |
| --- | --- | --- | --- |
| A01 | Pianta arredi quotata con ingombri d'uso e luce scala-cassa | 1:50 | A01_pianta_arredi_preliminare.dxf, A01_pianta_arredi_preliminare.pdf |
| E01 | Punti utenza e abaco | 1:50 | E01_punti_utenza_preliminari.dxf, E01_punti_utenza_preliminari.pdf |
| F01 | Prospetto parete di fondo cassa, esposizione e C1 | 1:20 | F01_prospetto_di_fondo.dxf, F01_prospetto_di_fondo.pdf |
| F02 | Prospetto parete smart tramezzo W_SAL_O lato scala | 1:20 | F02_prospetto_smart.dxf, F02_prospetto_smart.pdf |
| F03 | Prospetto fronte saletta C2, C3 e porta P_SAL | 1:20 | F03_prospetto_saletta.dxf, F03_prospetto_saletta.pdf |
| F04 | Prospetto parete laterale consulenza, C4 | 1:20 | F04_prospetto_laterale.dxf, F04_prospetto_laterale.pdf |
| D01 | Schema preliminare dettagli dai componenti comuni (non esecutivo, dati pending) | 1:10 | D01_dettagli_schema_preliminare.dxf, D01_dettagli_schema_preliminare.pdf |
| A01-V1 | Proposta V1: Cassa sulla parete di fondo | 1:50 | A01_V1_proposta.dxf, A01_V1_proposta.pdf |
| AB01-V1 | Abaco arredi della proposta V1 | - | AB01_V1_abaco.md |
| E01-V1 | Registro utenze della proposta V1 | - | E01_V1_registro_utenze.md |
| F01-V1 | Prospetto parete di fondo cassa, esposizione e C1 - proposta V1 | 1:20 | F01_prospetto_di_fondo_V1.dxf, F01_prospetto_di_fondo_V1.pdf |
| A01-V5 | Proposta V5: Cassa verso Smart, C1 a sinistra, scrivania parallela a VET_2 | 1:50 | A01_V5_proposta.dxf, A01_V5_proposta.pdf |
| AB01-V5 | Abaco arredi della proposta V5 | - | AB01_V5_abaco.md |
| E01-V5 | Registro utenze della proposta V5 | - | E01_V5_registro_utenze.md |
| F01-V5 | Prospetto parete di fondo cassa, esposizione e C1 - proposta V5 | 1:20 | F01_prospetto_di_fondo_V5.dxf, F01_prospetto_di_fondo_V5.pdf |
| E01-V5 | Punti utenza riallineati alla proposta V5 | 1:50 | E01_V5_proposta.dxf, E01_V5_proposta.pdf |
| A01-V5b | Proposta V5b: V5 con scrivania verso vetrina e ringhiera, cassetti ad apertura breve | 1:50 | A01_V5b_proposta.dxf, A01_V5b_proposta.pdf |
| AB01-V5b | Abaco arredi della proposta V5b | - | AB01_V5b_abaco.md |
| E01-V5b | Registro utenze della proposta V5b | - | E01_V5b_registro_utenze.md |
| F01-V5b | Prospetto parete di fondo cassa, esposizione e C1 - proposta V5b | 1:20 | F01_prospetto_di_fondo_V5b.dxf, F01_prospetto_di_fondo_V5b.pdf |
| E01-V5b | Punti utenza riallineati alla proposta V5b | 1:50 | E01_V5b_proposta.dxf, E01_V5b_proposta.pdf |
| Q01 | Registro quote aperte (100 righe) | - | Q01_quote_aperte.md |
| AB01 | Abaco arredi, distinta su misura e distinta componenti | - | AB01_abaco_arredi.md |
| E01 | Registro utenze completo | - | E01_registro_utenze.md |
| - | Proposte di layout quotate | - | proposte_layout.md |
| - | Controlli e superfici | - | criticita.md |

## Render (generati da `python -m src.render`)

| Vista | File | Presente | Revisione del modello |
| --- | --- | --- | --- |
| ingresso_verso_cassa | render/R01_ingresso_verso_cassa.png | sì | P04 |
| consulenza_verso_saletta | render/R01_consulenza_verso_saletta.png | sì | P04 |
| parete_smart | render/R01_parete_smart.png | sì | P04 |
| pianta_dall_alto | render/R01_pianta_dall_alto.png | sì | P04 |

Set di render completo e della revisione corrente.

### Render della proposta V5 (`python -m src.render --variante=V5`)

| Vista | File | Presente | Revisione del modello |
| --- | --- | --- | --- |
| ingresso_verso_cassa | render/V5/R01_ingresso_verso_cassa.png | sì | P04-V5 |
| consulenza_verso_saletta | render/V5/R01_consulenza_verso_saletta.png | sì | P04-V5 |
| parete_smart | render/V5/R01_parete_smart.png | sì | P04-V5 |
| pianta_dall_alto | render/V5/R01_pianta_dall_alto.png | sì | P04-V5 |

Set completo e della revisione corrente.

### Render della proposta V5b (`python -m src.render --variante=V5b`)

| Vista | File | Presente | Revisione del modello |
| --- | --- | --- | --- |
| ingresso_verso_cassa | render/V5b/R01_ingresso_verso_cassa.png | sì | P04-V5b |
| consulenza_verso_saletta | render/V5b/R01_consulenza_verso_saletta.png | sì | P04-V5b |
| parete_smart | render/V5b/R01_parete_smart.png | sì | P04-V5b |
| pianta_dall_alto | render/V5b/R01_pianta_dall_alto.png | sì | P04-V5b |

Set completo e della revisione corrente.
