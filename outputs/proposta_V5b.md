# Proposta V5b: scrivania verso vetrina e ringhiera, cassetti ad apertura breve

Modello **P04** (2026-11-23). Risponde al documento «Limpidia — integrazione V5b per Claude» del 23/11/2026. V5b parte dalla V5 e cambia solo la posizione della scrivania e il modo in cui si valutano sedute e cassetti. P03 e V5 restano come confronto, con origine, orientamento e muri invariati. Tutto è PRELIMINARE - NON PER CANTIERE.

Elaborati V5b: `A01_V5b_proposta.pdf/.dxf`, `E01_V5b_proposta.pdf/.dxf`, `E01_V5b_registro_utenze.md`, `AB01_V5b_abaco.md`, `F01_prospetto_di_fondo_V5b.pdf/.dxf`, `render/V5b/` (4 viste), sezione V5b di `proposte_layout.md`.

## 1. Posizione

| | V5 | V5b |
| --- | --- | --- |
| Scrivania 1600 × 700, parallela a VET_2 | x 4250–5850, y 750–1450 | **x 3950–5550, y 600–1300** (300 mm verso la ringhiera, 150 mm verso la vetrina) |
| Operatore / cliente | non assegnati | operatore lato vetrina, cliente lato interno: **ipotesi della prova**, da confermare |
| E06 (riferimento grafico) | 5050, 1100 | 4750, 950 |

Catena lungo Y, dalla vetrina al muro della saletta: **600 + 700 + 980 + 400 = 2680 mm**. I 2680 mm vanno dalla facciata al muro della saletta, non dai fronti delle cassettiere: i fronti di C2/C3 sono a 2280 mm dalla facciata.

## 2. Come si valutano sedute e cassetti in V5b

Le indicazioni del 23/11 prevalgono sulle ipotesi precedenti:

- **Niente fascia fissa da 750 mm.** Ogni seduta è dichiarata per lato e ruolo e usa l'ingombro della **sedia reale** (`seat_operator`, `seat_client`). Quel dato manca, quindi i controlli che lo usano restano «da verificare»: non è stato sostituito con un altro numero.
- **Cassetti normalmente chiusi.** L'apertura è breve e non richiede un passaggio contemporaneo nella stessa fascia.
- **Tre scenari separati** su FP02 (C3), FP09 (C2) e FP05 (C4):
  - **A. Uso ordinario:** cassetti chiusi e sedute occupate. È lo scenario del percorso.
  - **B. Movimento occasionale della seduta:** dato da rilevare con la sedia reale.
  - **C. Apertura breve dei cassetti:** solo, oppure con il cliente seduto.
- **Collisioni fisiche e azioni alternative sono distinte.** Un cassetto o una seduta che urta un mobile resta un conflitto. Se due azioni non richieste insieme si sovrappongono (es. cassetto aperto e sedia occupata), l'esito è un avviso: «possibile breve spostamento da verificare». Non è un'incompatibilità. Due sonde nei test lo dimostrano.
- **C1 non cambia.** La rarità d'uso non dimostra niente: con i cassetti aperti restano 100 mm dall'asse della testata, non verificabile finché manca il rilievo della protezione.

Le tavole V5 e P03 mantengono i loro scenari storici, compresa la fascia 750, per restare confrontabili.

## 3. Distanze (dagli stessi ingombri della pianta)

| Misura | V5b (y 600) | Alternativa y 550 | Nota |
| --- | --- | --- | --- |
| Scrivania – facciata (lato operatore) | 600 | 550 | distanza proposta, non un minimo ergonomico; serramento non rilevato |
| Scrivania – fronti C2/C3 chiusi (lato cliente) | 980 | 1030 | uso ordinario A |
| Scrivania – C2/C3 aperti (350) | 630 | 680 | apertura breve, sedute e persona escluse |
| Scrivania – C4 chiusa / aperta | 1550 / 1200 | 1550 / 1200 | percorso ordinario verso la saletta |
| Scrivania – muro destro | 1950 | 1950 | per il percorso cavi E06 |
| Sedia operatore / cliente | da rilevare | da rilevare | sedia reale |

Non ci sono collisioni statiche con gli altri mobili. La scrivania non invade l'ingresso, l'isola o il foro scala.

## 4. Esiti principali rispetto a V5

| Controllo | V5 | V5b |
| --- | --- | --- |
| FP02 / FP09 (C3, C2 e scrivania) | conflitto (fascia 750 + cassetti) | da verificare: sedute reali mancanti. Mobili chiusi 980, cassetti aperti 630 |
| FP02-PERCORSO | conflitto 480 (cassetti aperti) | da verificare: percorso ordinario con le sedute reali |
| FP05-PERCORSO (lato C4) | da verificare, 900 | **compatibile nelle ipotesi, 1550** |
| FP06 scrivania–vetrina | da verificare, 750 | da verificare, 600 (serramento) |
| Porta saletta (APPR-P_SAL) | conflitto | conflitto invariato (vedi V2) |
| Scala–cassa, C1–testata | da verificare | invariati |

## 5. Problemi fisici residui

1. **Sedie reali** di operatore e cliente: senza la scheda non si può chiudere né il percorso ordinario lato C2/C3 né il lato vetrina.
2. **Lato vetrina 600 mm:** l'operatore siede fra scrivania e vetrina. Servono serramento, sporgenze e la sedia (anche la parte sotto il piano). Va coordinato con il lato contenitore della scrivania.
3. **C1 vicino alla ringhiera di testata:** 100 mm a cassetti aperti, senza spessore della protezione.
4. **C4 e porta saletta:** 220 × 20 mm, invariato.
5. **Scala–cassa:** 1031 mm solo in diagonale dal foro.

## 6. Impianti

E06 segue la scrivania (4750, 950). È solo un riferimento di coordinamento, non un punto di allaccio. Il supporto distingue il fronte di C4 (1550 mm) dal muro destro (1950 mm). Percorso cavi, quota Z e quantità restano da definire con l'elettricista. Il registro completo della variante è `E01_V5b_registro_utenze.md`.

## 7. Altri punti della verifica P04

Ho fatto quelli che si possono ricavare dal testo:
- registro utenze, abaco e prospetto F01 per ogni variante con tavola;
- note dell'abaco E01 a capo invece che troncate;
- protezioni della scala calcolate tutte, non solo la prima linea (già in P04).

«Qualità degli stati» e gli altri rilievi della verifica P04 non sono descritti nel documento V5b. Per sistemarli mi serve il testo di quella verifica.

## 8. Verifiche

```
pytest -q                           -> 85 passed, 0 failed, 0 skipped (compresi i set di render base, V5 e V5b)
python -m src.generate
python -m src.render                (base P04)
python -m src.render --variante=V5  (V5)
python -m src.render --variante=V5b (V5b)
```

## Decisioni da prendere

- Ruoli: operatore lato vetrina e cliente lato interno vanno bene?
- Le sedie reali (scheda o misure) di operatore e cliente.
- Y 600 oppure y 550.
