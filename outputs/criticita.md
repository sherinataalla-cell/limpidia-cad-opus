# Criticità e verifiche (generato dal modello)

Revisione modello: P00. Controlli solo geometrici; da validare con il tecnico.

| Priorità | Criticità |
| --- | --- |
| Alta | Perimetro del modello = 34.7 m² netti contro 45 m² dichiarati per il piano terra. Va chiarito con il rilievo se i 45 m² sono lordi (muri compresi) o se il perimetro ipotizzato è sbagliato. |
| Alta | Porta della saletta non presente nel modello. Sul fronte saletta (4050 mm) le due cassettiere occupano 2400 mm: restano 150 mm a sinistra e 1500 mm a destra. La porta, con spallette e luce netta, deve stare in uno di questi tratti. |
| Alta | Banco cassa: tra il fronte cassa e la zona scala restano 300 mm. Se l'operatore sta davanti alla cassa non c'è spazio; va definito da che lato lavora e la dimensione reale del prodotto (oggi segnaposto 1200 × 600). |
| Media | Tra CASSA e SCALE restano 300 mm (sotto la soglia di lavoro di 900 mm). |
| Media | Tra C3 e SCRIVANIA restano 580 mm (sotto la soglia di lavoro di 900 mm). |
| Media | Tra CASSA e C1 restano 640 mm (sotto la soglia di lavoro di 900 mm). |
| Media | Tra C4 e SALETTA restano 880 mm (sotto la soglia di lavoro di 900 mm). |
| Bassa | E05 (Isola smart) cade dentro l'ingombro di ISOLA_SMART: va deciso se è un punto a pavimento o a parete e come si raggiunge per la manutenzione. |
| Bassa | E06 (Scrivania) cade dentro l'ingombro di SCRIVANIA: va deciso se è un punto a pavimento o a parete e come si raggiunge per la manutenzione. |
| Bassa | Mobili con dimensioni non verificate: CASSA, C1, C2, C3, C4, SCRIVANIA. |

## Distanze libere tra elementi vicini

| Da | A | Distanza (mm) |
| --- | --- | --- |
| C2 | C3 | 0 |
| C2 | SALETTA | 0 |
| C3 | SALETTA | 0 |
| ISOLA_SMART | SCALE | 50 |
| CASSA | SCALE | 300 |
| C3 | SCRIVANIA | 580 |
| CASSA | C1 | 640 |
| C4 | SALETTA | 880 |
| CASSA | ISOLA_SMART | 1050 |

## Stato delle quote dei mobili

| ID | L × P (mm) | Stato | Nota |
| --- | --- | --- | --- |
| CASSA | 1200 × 600 | da definire | ingombro placeholder, fianco a muro sinistro |
| C1 | 1500 × 400 | ipotesi | fondo, possibile 1200 |
| C2 | 1200 × 400 | ipotesi | fronte saletta |
| C3 | 1200 × 400 | ipotesi | fronte saletta |
| C4 | 400 × 1500 | ipotesi | laterale, 1500 lungo Y; frontale verso negozio |
| SCRIVANIA | 700 × 1600 | ipotesi | 1600 lungo Y, parallela alla parete C4 |
| ISOLA_SMART | 390 × 1600 | da catalogo | lato lungo parallelo alla ringhiera |
