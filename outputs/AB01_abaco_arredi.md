# AB01 - Abaco arredi

Revisione P03 (2026-11-22). L × P × H = dimensioni del PRODOTTO (L lungo il fronte, P profondità, H altezza totale): ingombri esterni con top e zoccolo compresi. La posa nel locale è data da fronte/rotazione, ingombro X × Y e posizione; la rotazione cambia X × Y, non L × P × H. Le schede della variante scelta vanno archiviate prima di portare una dimensione a `verified`.

## Arredi di catalogo

| ID | Prodotto / fonte | L × P × H prodotto (mm) | Stato dimensioni | Fronte, rotazione | Ingombro X × Y | Posizione X, Y | Stato posa | Finitura |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CASSA | https://amzn.eu/d/0awMXHm3 | 1200 × 600 × 1000 | da definire (H ipotesi) | -y, 0° | 1200 × 600 | 0, 4150 | ipotesi | bianca, marchio ufficiale sul frontale |
| C1 | https://de.homary.com/lditem/lumio-59-led-6-drawer-dresser-with-charging-station-54469.html | 1500 × 400 × 800 | ipotesi (H ipotesi) | -y, 0° | 1500 × 400 | 1840, 4350 | ipotesi | noce scuro, due linee LED |
| C2 | Lumio (stessa famiglia, variante 120 da verificare) | 1200 × 400 × 800 | ipotesi (H ipotesi) | -y, 0° | 1200 × 400 | 3600, 2280 | ipotesi | noce scuro, due linee LED |
| C3 | Lumio (stessa famiglia, variante 120 da verificare) | 1200 × 400 × 800 | ipotesi (H ipotesi) | -y, 0° | 1200 × 400 | 4800, 2280 | ipotesi | noce scuro, due linee LED |
| C4 | https://de.homary.com/lditem/lumio-59-led-6-drawer-dresser-with-charging-station-54469.html | 1500 × 400 × 800 | ipotesi (H ipotesi) | -x, 90° | 400 × 1500 | 7100, 300 | ipotesi | noce scuro, due linee LED |
| SCRIVANIA | https://de.homary.com/item/modern-63-rectangular-walnut-wood-desk-with-charging-station-storage-55649.html | 1600 × 700 × 760 | ipotesi (H ipotesi) | -x, 90° | 700 × 1600 | 4950, 100 | ipotesi | noce |
| ISOLA_SMART | https://www.arredamento1.it/collezioni-di-mobili/collezione-di-mobili-monfero/madia-monfero.html | 1600 × 390 × 830 | da catalogo (H da catalogo) | +x, 270° | 390 × 1600 | 900, 1500 | ipotesi | Monfero cachemire, ante verso la vendita |

## Componenti su misura (distinta per il falegname, proposta da validare)

| Componente | Quantità | Misure proposte (mm) | Stato | Fonte |
| --- | --- | --- | --- | --- |
| Mensole bianche sfalsate (pezzi) | 20 su 5 pareti attrezzate (CASSA, C1, C2, C3, C4) | prof. 250, sp. 25, base ai livelli [1250, 1550, 1850, 2150], sfalsamento 150; interrotte sui cubotti | ipotesi | S4, proposta |
| Cubotti aperti rovere | 5 | 350 × 350 × prof. 260, pannelli 18 (5 pezzi) | ipotesi | S4, proposta |
| Colonne listelli rovere + specchio | 3 (LS1, LS2, LS3) | larghezza 320, listelli 30 × 25 passo 45, sommità soffitto - 400; specchio 250 × 1000 da quota 1300, sp. 12 su piastra 3 | ipotesi | S4, proposta |
| Profili LED (cassettiere, mensole, cubotti) | 33 tratti | cassettiere: assi a [0.38, 0.7] di H, fresata 6; mensole: sotto il piano | ipotesi | schede LED da acquisire |
| Telai smart | 4 | telaio esterno 410 × 700, immagine 380 (bordo 15), distanza libera 60, interasse 470, base a 1150, prof. 40 | ipotesi | S4/S2, proposta |
| Immagini dei pannelli | 4 | 380 × 670 | da definire | asset da fornire |
| Ripiani prodotto smart | 4 | 410 × 150 × 25, base a 1050 | ipotesi | S4, proposta |
| Cartellini smart | 4 | 300 × 110, base a 900; testi S4 | ipotesi | S4, proposta |
| Rivestimento mattoni marrone scuro | 1 parete | 2070 × soffitto, sp. 20 | ipotesi | decisioni |

## Distinta componenti (geometria comune a prospetti e render)

Stessi solidi usati da F01–F04 e dalla scena 3D. Coordinate in mm; z0–z1 = base e sommità.

| Componente | Tipo | Parete | x0–x1 | y0–y1 | z0–z1 | Stato | Raccordo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CASSA_zoccolo | plinth | FONDO | 30–1170 | 4180–4720 | 0–60 | da definire |  |
| CASSA_corpo | body | FONDO | 0–1200 | 4151–4750 | 60–975 | da definire |  |
| CASSA_top | top | FONDO | 0–1200 | 4150–4750 | 975–1000 | da definire |  |
| CASSA_marchio | logo | FONDO | 270–930 | 4150–4151 | 516–726 | da catalogo | inlay |
| C1_zoccolo | plinth | FONDO | 1860–3320 | 4380–4750 | 0–80 | ipotesi |  |
| C1_corpo | body | FONDO | 1840–3340 | 4350–4750 | 80–800 | ipotesi |  |
| C1_led_1 | led | FONDO | 1870–3310 | 4350–4356 | 298–310 | ipotesi | inlay |
| C1_led_2 | led | FONDO | 1870–3310 | 4350–4356 | 554–566 | ipotesi | inlay |
| C2_zoccolo | plinth | SALETTA:-y | 3620–4780 | 2310–2680 | 0–80 | ipotesi |  |
| C2_corpo | body | SALETTA:-y | 3600–4800 | 2280–2680 | 80–800 | ipotesi |  |
| C2_led_1 | led | SALETTA:-y | 3630–4770 | 2280–2286 | 298–310 | ipotesi | inlay |
| C2_led_2 | led | SALETTA:-y | 3630–4770 | 2280–2286 | 554–566 | ipotesi | inlay |
| C3_zoccolo | plinth | SALETTA:-y | 4820–5980 | 2310–2680 | 0–80 | ipotesi |  |
| C3_corpo | body | SALETTA:-y | 4800–6000 | 2280–2680 | 80–800 | ipotesi |  |
| C3_led_1 | led | SALETTA:-y | 4830–5970 | 2280–2286 | 298–310 | ipotesi | inlay |
| C3_led_2 | led | SALETTA:-y | 4830–5970 | 2280–2286 | 554–566 | ipotesi | inlay |
| C4_zoccolo | plinth | PARETE_DESTRA | 7130–7500 | 320–1780 | 0–80 | ipotesi |  |
| C4_corpo | body | PARETE_DESTRA | 7100–7500 | 300–1800 | 80–800 | ipotesi |  |
| C4_led_1 | led | PARETE_DESTRA | 7100–7106 | 330–1770 | 298–310 | ipotesi | inlay |
| C4_led_2 | led | PARETE_DESTRA | 7100–7106 | 330–1770 | 554–566 | ipotesi | inlay |
| SCRIVANIA_piano | top | - | 4950–5650 | 100–1700 | 720–760 | ipotesi |  |
| SCRIVANIA_cassettiera | body | - | 4990–5610 | 140–590 | 0–720 | ipotesi |  |
| SCRIVANIA_fianco | body | - | 4990–5610 | 1620–1660 | 0–720 | ipotesi |  |
| ISOLA_SMART_corpo | body | - | 900–1290 | 1500–3100 | 0–800 | da catalogo |  |
| ISOLA_SMART_top | top | - | 900–1290 | 1500–3100 | 800–830 | da catalogo |  |
| CASSA_mensola_1 | shelf | FONDO | 0–1050 | 4500–4750 | 1250–1275 | ipotesi |  |
| CASSA_mensola_1_led | led | FONDO | 20–1030 | 4520–4730 | 1244–1250 | ipotesi |  |
| CASSA_mensola_2 | shelf | FONDO | 150–1200 | 4500–4750 | 1550–1575 | ipotesi |  |
| CASSA_mensola_2_led | led | FONDO | 170–1180 | 4520–4730 | 1544–1550 | ipotesi |  |
| CASSA_mensola_3a | shelf | FONDO | 0–801 | 4500–4750 | 1850–1875 | ipotesi | interrotta sul cubotto |
| CASSA_mensola_3a_led | led | FONDO | 20–781 | 4520–4730 | 1844–1850 | ipotesi |  |
| CASSA_mensola_4 | shelf | FONDO | 150–1200 | 4500–4750 | 2150–2175 | ipotesi |  |
| CASSA_mensola_4_led | led | FONDO | 170–1180 | 4520–4730 | 2144–2150 | ipotesi |  |
| CASSA_cubotto_fianco_sx | cubby | FONDO | 801–819 | 4490–4750 | 1575–1925 | ipotesi |  |
| CASSA_cubotto_fianco_dx | cubby | FONDO | 1133–1151 | 4490–4750 | 1575–1925 | ipotesi |  |
| CASSA_cubotto_fondo | cubby | FONDO | 819–1133 | 4732–4750 | 1575–1925 | ipotesi |  |
| CASSA_cubotto_base | cubby | FONDO | 819–1133 | 4490–4732 | 1575–1593 | ipotesi |  |
| CASSA_cubotto_cielo | cubby | FONDO | 819–1133 | 4490–4732 | 1907–1925 | ipotesi |  |
| CASSA_cubotto_led | led | FONDO | 819–1133 | 4510–4732 | 1901–1907 | ipotesi |  |
| C1_mensola_1 | shelf | FONDO | 1840–3190 | 4500–4750 | 1250–1275 | ipotesi |  |
| C1_mensola_1_led | led | FONDO | 1860–3170 | 4520–4730 | 1244–1250 | ipotesi |  |
| C1_mensola_2 | shelf | FONDO | 1990–3190 | 4500–4750 | 1550–1575 | ipotesi |  |
| C1_mensola_2_led | led | FONDO | 2010–3170 | 4520–4730 | 1544–1550 | ipotesi |  |
| C1_mensola_3a | shelf | FONDO | 1840–2827 | 4500–4750 | 1850–1875 | ipotesi | interrotta sul cubotto |
| C1_mensola_3a_led | led | FONDO | 1860–2807 | 4520–4730 | 1844–1850 | ipotesi |  |
| C1_mensola_4 | shelf | FONDO | 1990–3190 | 4500–4750 | 2150–2175 | ipotesi |  |
| C1_mensola_4_led | led | FONDO | 2010–3170 | 4520–4730 | 2144–2150 | ipotesi |  |
| C1_cubotto_fianco_sx | cubby | FONDO | 2827–2845 | 4490–4750 | 1575–1925 | ipotesi |  |
| C1_cubotto_fianco_dx | cubby | FONDO | 3159–3177 | 4490–4750 | 1575–1925 | ipotesi |  |
| C1_cubotto_fondo | cubby | FONDO | 2845–3159 | 4732–4750 | 1575–1925 | ipotesi |  |
| C1_cubotto_base | cubby | FONDO | 2845–3159 | 4490–4732 | 1575–1593 | ipotesi |  |
| C1_cubotto_cielo | cubby | FONDO | 2845–3159 | 4490–4732 | 1907–1925 | ipotesi |  |
| C1_cubotto_led | led | FONDO | 2845–3159 | 4510–4732 | 1901–1907 | ipotesi |  |
| C2_mensola_1 | shelf | SALETTA:-y | 3600–4650 | 2430–2680 | 1250–1275 | ipotesi |  |
| C2_mensola_1_led | led | SALETTA:-y | 3620–4630 | 2450–2660 | 1244–1250 | ipotesi |  |
| C2_mensola_2 | shelf | SALETTA:-y | 3750–4800 | 2430–2680 | 1550–1575 | ipotesi |  |
| C2_mensola_2_led | led | SALETTA:-y | 3770–4780 | 2450–2660 | 1544–1550 | ipotesi |  |
| C2_mensola_3a | shelf | SALETTA:-y | 3600–4401 | 2430–2680 | 1850–1875 | ipotesi | interrotta sul cubotto |
| C2_mensola_3a_led | led | SALETTA:-y | 3620–4381 | 2450–2660 | 1844–1850 | ipotesi |  |
| C2_mensola_4 | shelf | SALETTA:-y | 3750–4800 | 2430–2680 | 2150–2175 | ipotesi |  |
| C2_mensola_4_led | led | SALETTA:-y | 3770–4780 | 2450–2660 | 2144–2150 | ipotesi |  |
| C2_cubotto_fianco_sx | cubby | SALETTA:-y | 4401–4419 | 2420–2680 | 1575–1925 | ipotesi |  |
| C2_cubotto_fianco_dx | cubby | SALETTA:-y | 4733–4751 | 2420–2680 | 1575–1925 | ipotesi |  |
| C2_cubotto_fondo | cubby | SALETTA:-y | 4419–4733 | 2662–2680 | 1575–1925 | ipotesi |  |
| C2_cubotto_base | cubby | SALETTA:-y | 4419–4733 | 2420–2662 | 1575–1593 | ipotesi |  |
| C2_cubotto_cielo | cubby | SALETTA:-y | 4419–4733 | 2420–2662 | 1907–1925 | ipotesi |  |
| C2_cubotto_led | led | SALETTA:-y | 4419–4733 | 2440–2662 | 1901–1907 | ipotesi |  |
| C3_mensola_1 | shelf | SALETTA:-y | 4800–5850 | 2430–2680 | 1250–1275 | ipotesi |  |
| C3_mensola_1_led | led | SALETTA:-y | 4820–5830 | 2450–2660 | 1244–1250 | ipotesi |  |
| C3_mensola_2 | shelf | SALETTA:-y | 4950–6000 | 2430–2680 | 1550–1575 | ipotesi |  |
| C3_mensola_2_led | led | SALETTA:-y | 4970–5980 | 2450–2660 | 1544–1550 | ipotesi |  |
| C3_mensola_3a | shelf | SALETTA:-y | 4800–5601 | 2430–2680 | 1850–1875 | ipotesi | interrotta sul cubotto |
| C3_mensola_3a_led | led | SALETTA:-y | 4820–5581 | 2450–2660 | 1844–1850 | ipotesi |  |
| C3_mensola_4 | shelf | SALETTA:-y | 4950–6000 | 2430–2680 | 2150–2175 | ipotesi |  |
| C3_mensola_4_led | led | SALETTA:-y | 4970–5980 | 2450–2660 | 2144–2150 | ipotesi |  |
| C3_cubotto_fianco_sx | cubby | SALETTA:-y | 5601–5619 | 2420–2680 | 1575–1925 | ipotesi |  |
| C3_cubotto_fianco_dx | cubby | SALETTA:-y | 5933–5951 | 2420–2680 | 1575–1925 | ipotesi |  |
| C3_cubotto_fondo | cubby | SALETTA:-y | 5619–5933 | 2662–2680 | 1575–1925 | ipotesi |  |
| C3_cubotto_base | cubby | SALETTA:-y | 5619–5933 | 2420–2662 | 1575–1593 | ipotesi |  |
| C3_cubotto_cielo | cubby | SALETTA:-y | 5619–5933 | 2420–2662 | 1907–1925 | ipotesi |  |
| C3_cubotto_led | led | SALETTA:-y | 5619–5933 | 2440–2662 | 1901–1907 | ipotesi |  |
| C4_mensola_1 | shelf | PARETE_DESTRA | 7250–7500 | 450–1800 | 1250–1275 | ipotesi |  |
| C4_mensola_1_led | led | PARETE_DESTRA | 7270–7480 | 470–1780 | 1244–1250 | ipotesi |  |
| C4_mensola_2 | shelf | PARETE_DESTRA | 7250–7500 | 300–1650 | 1550–1575 | ipotesi |  |
| C4_mensola_2_led | led | PARETE_DESTRA | 7270–7480 | 320–1630 | 1544–1550 | ipotesi |  |
| C4_mensola_3b | shelf | PARETE_DESTRA | 7250–7500 | 813–1800 | 1850–1875 | ipotesi | interrotta sul cubotto |
| C4_mensola_3b_led | led | PARETE_DESTRA | 7270–7480 | 833–1780 | 1844–1850 | ipotesi |  |
| C4_mensola_4 | shelf | PARETE_DESTRA | 7250–7500 | 300–1650 | 2150–2175 | ipotesi |  |
| C4_mensola_4_led | led | PARETE_DESTRA | 7270–7480 | 320–1630 | 2144–2150 | ipotesi |  |
| C4_cubotto_fianco_sx | cubby | PARETE_DESTRA | 7240–7500 | 463–481 | 1575–1925 | ipotesi |  |
| C4_cubotto_fianco_dx | cubby | PARETE_DESTRA | 7240–7500 | 795–813 | 1575–1925 | ipotesi |  |
| C4_cubotto_fondo | cubby | PARETE_DESTRA | 7482–7500 | 481–795 | 1575–1925 | ipotesi |  |
| C4_cubotto_base | cubby | PARETE_DESTRA | 7240–7482 | 481–795 | 1575–1593 | ipotesi |  |
| C4_cubotto_cielo | cubby | PARETE_DESTRA | 7240–7482 | 481–795 | 1907–1925 | ipotesi |  |
| C4_cubotto_led | led | PARETE_DESTRA | 7260–7482 | 481–795 | 1901–1907 | ipotesi |  |
| LS1_listello_1 | slat | SALETTA:-y | 6060–6090 | 2655–2680 | 0–3750 | ipotesi |  |
| LS1_listello_2 | slat | SALETTA:-y | 6105–6135 | 2655–2680 | 0–3750 | ipotesi |  |
| LS1_listello_3 | slat | SALETTA:-y | 6150–6180 | 2655–2680 | 0–3750 | ipotesi |  |
| LS1_listello_4 | slat | SALETTA:-y | 6195–6225 | 2655–2680 | 0–3750 | ipotesi |  |
| LS1_listello_5 | slat | SALETTA:-y | 6240–6270 | 2655–2680 | 0–3750 | ipotesi |  |
| LS1_listello_6 | slat | SALETTA:-y | 6285–6315 | 2655–2680 | 0–3750 | ipotesi |  |
| LS1_listello_7 | slat | SALETTA:-y | 6330–6360 | 2655–2680 | 0–3750 | ipotesi |  |
| LS1_piastra | frame | SALETTA:-y | 6070–6350 | 2652–2655 | 1285–2315 | ipotesi |  |
| LS1_specchio | mirror | SALETTA:-y | 6085–6335 | 2640–2652 | 1300–2300 | ipotesi |  |
| LS2_listello_1 | slat | PARETE_DESTRA | 7475–7500 | 1860–1890 | 0–3750 | ipotesi |  |
| LS2_listello_2 | slat | PARETE_DESTRA | 7475–7500 | 1905–1935 | 0–3750 | ipotesi |  |
| LS2_listello_3 | slat | PARETE_DESTRA | 7475–7500 | 1950–1980 | 0–3750 | ipotesi |  |
| LS2_listello_4 | slat | PARETE_DESTRA | 7475–7500 | 1995–2025 | 0–3750 | ipotesi |  |
| LS2_listello_5 | slat | PARETE_DESTRA | 7475–7500 | 2040–2070 | 0–3750 | ipotesi |  |
| LS2_listello_6 | slat | PARETE_DESTRA | 7475–7500 | 2085–2115 | 0–3750 | ipotesi |  |
| LS2_listello_7 | slat | PARETE_DESTRA | 7475–7500 | 2130–2160 | 0–3750 | ipotesi |  |
| LS2_piastra | frame | PARETE_DESTRA | 7472–7475 | 1870–2150 | 1285–2315 | ipotesi |  |
| LS2_specchio | mirror | PARETE_DESTRA | 7460–7472 | 1885–2135 | 1300–2300 | ipotesi |  |
| LS3_listello_1 | slat | FONDO | 1370–1400 | 4725–4750 | 0–3750 | ipotesi |  |
| LS3_listello_2 | slat | FONDO | 1415–1445 | 4725–4750 | 0–3750 | ipotesi |  |
| LS3_listello_3 | slat | FONDO | 1460–1490 | 4725–4750 | 0–3750 | ipotesi |  |
| LS3_listello_4 | slat | FONDO | 1505–1535 | 4725–4750 | 0–3750 | ipotesi |  |
| LS3_listello_5 | slat | FONDO | 1550–1580 | 4725–4750 | 0–3750 | ipotesi |  |
| LS3_listello_6 | slat | FONDO | 1595–1625 | 4725–4750 | 0–3750 | ipotesi |  |
| LS3_listello_7 | slat | FONDO | 1640–1670 | 4725–4750 | 0–3750 | ipotesi |  |
| LS3_piastra | frame | FONDO | 1380–1660 | 4722–4725 | 1285–2315 | ipotesi |  |
| LS3_specchio | mirror | FONDO | 1395–1645 | 4710–4722 | 1300–2300 | ipotesi |  |
| SMART_rivestimento | cladding | SALETTA:-x | 3370–3390 | 2680–4750 | 0–4150 | ipotesi |  |
| SMART_telaio_1 | frame | SALETTA:-x | 3330–3370 | 4215–4625 | 1150–1850 | ipotesi |  |
| SMART_immagine_1 | image | SALETTA:-x | 3330–3331 | 4230–4610 | 1165–1835 | da definire | inlay |
| SMART_ripiano_1 | shelf | SALETTA:-x | 3220–3370 | 4215–4625 | 1050–1075 | ipotesi |  |
| SMART_cartellino_1 | label | SALETTA:-x | 3362–3370 | 4270–4570 | 900–1010 | ipotesi |  |
| SMART_telaio_2 | frame | SALETTA:-x | 3330–3370 | 3745–4155 | 1150–1850 | ipotesi |  |
| SMART_immagine_2 | image | SALETTA:-x | 3330–3331 | 3760–4140 | 1165–1835 | da definire | inlay |
| SMART_ripiano_2 | shelf | SALETTA:-x | 3220–3370 | 3745–4155 | 1050–1075 | ipotesi |  |
| SMART_cartellino_2 | label | SALETTA:-x | 3362–3370 | 3800–4100 | 900–1010 | ipotesi |  |
| SMART_telaio_3 | frame | SALETTA:-x | 3330–3370 | 3275–3685 | 1150–1850 | ipotesi |  |
| SMART_immagine_3 | image | SALETTA:-x | 3330–3331 | 3290–3670 | 1165–1835 | da definire | inlay |
| SMART_ripiano_3 | shelf | SALETTA:-x | 3220–3370 | 3275–3685 | 1050–1075 | ipotesi |  |
| SMART_cartellino_3 | label | SALETTA:-x | 3362–3370 | 3330–3630 | 900–1010 | ipotesi |  |
| SMART_telaio_4 | frame | SALETTA:-x | 3330–3370 | 2805–3215 | 1150–1850 | ipotesi |  |
| SMART_immagine_4 | image | SALETTA:-x | 3330–3331 | 2820–3200 | 1165–1835 | da definire | inlay |
| SMART_ripiano_4 | shelf | SALETTA:-x | 3220–3370 | 2805–3215 | 1050–1075 | ipotesi |  |
| SMART_cartellino_4 | label | SALETTA:-x | 3362–3370 | 2860–3160 | 900–1010 | ipotesi |  |

Fissaggi, carichi, profili LED, vani driver e passacavi: schema preliminare D01; dati reali pending.
