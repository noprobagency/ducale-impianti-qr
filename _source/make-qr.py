#!/usr/bin/env python3
"""
Genera i QR code da stampa per le tre landing, e li rilegge per verifica.

Eseguire dalla radice del progetto:  python3 _source/make-qr.py
Serve:  pip install segno   (per la verifica anche: pip install opencv-python-headless)

I file finiscono in qr/, cartella per la tipografia: NON va caricata sull'hosting.

Scelte, tutte deliberate perche' un QR stampato non si corregge piu':

- QR STATICO: dentro c'e' direttamente l'indirizzo della pagina, nessun servizio
  di rimbalzo che possa scadere, chiudere o chiedere un abbonamento.
- Indirizzo nella forma canonica, https + www + barra finale: chi scansiona
  arriva alla pagina senza reindirizzamenti intermedi.
- UTM minimo (sorgente e mezzo): distingue il biglietto da visita da futuri
  supporti. Va messo adesso perche' dopo la stampa non si aggiunge piu'.
- Correzione d'errore M: il biglietto e' carta piatta e pulita, e con M il
  codice resta a 45x45 moduli. Con Q salirebbe a 53x53, piu' fitto a parita'
  di dimensione. Per furgoni o cartelli di cantiere servirebbe Q, con un
  indirizzo diverso (utm_source=furgone).
- Nero pieno su bianco, margine bianco di 4 moduli come da specifica: senza
  quella cornice molti telefoni non agganciano il codice.
"""
from pathlib import Path
import segno

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "qr"

UTM = "?utm_source=biglietto&utm_medium=qr"

QR = {
    "ducale-qr":    "https://www.ducaleimpianti.com/ducale-qr/",
    "elettrica-qr": "https://www.elettricaducale.it/elettrica-qr/",
    "officina-qr":  "https://www.elettricaducale.it/officina-qr/",
}

LATO_MINIMO_MM = 20      # sotto, i moduli scendono verso il limite di lettura
BORDO = 4                # margine bianco in moduli: il minimo della specifica


def rileggi(png, url):
    """Rilegge il PNG con lettori indipendenti da quello che l'ha scritto.

    Due rilevatori OpenCV, a sei misure diverse. Un risultato vuoto e' solo un
    lettore che non ha agganciato il codice (il rilevatore classico, per esempio,
    a volte manca i codici molto grandi e nitidi); un risultato DIVERSO
    dall'indirizzo e' invece un errore vero. Si passa se nessuna lettura e'
    sbagliata e almeno una e' giusta.

    Restituisce (letture giuste, letture totali, testi sbagliati) oppure None.
    """
    try:
        import cv2
    except ImportError:
        return None
    lettori = [cv2.QRCodeDetector()]
    if hasattr(cv2, "QRCodeDetectorAruco"):
        lettori.append(cv2.QRCodeDetectorAruco())
    img = cv2.imread(str(png))
    giuste, totali, sbagliate = 0, 0, set()
    for lato in (img.shape[0], 800, 600, 400, 300, 200):
        r = cv2.resize(img, (lato, lato), interpolation=cv2.INTER_AREA)
        for l in lettori:
            testo, *_ = l.detectAndDecode(r)
            totali += 1
            if testo == url:
                giuste += 1
            elif testo:
                sbagliate.add(testo)
    return giuste, totali, sbagliate


OUT.mkdir(exist_ok=True)
tutto_ok = True
for nome, base in QR.items():
    url = base + UTM
    qr = segno.make(url, error="m", boost_error=False, micro=False)
    lato = qr.symbol_size(border=BORDO)[0]

    # vettoriali per la tipografia: si scalano a qualunque misura senza perdere nitidezza
    qr.save(OUT / f"{nome}.svg", border=BORDO, scale=10, dark="#000000", light="#ffffff")
    qr.save(OUT / f"{nome}.pdf", border=BORDO, scale=10, dark="#000000", light="#ffffff")
    qr.save(OUT / f"{nome}.eps", border=BORDO, scale=10, dark="#000000", light="#ffffff")
    # raster ad alta risoluzione per chi lo chiede: 1200 dpi a 25 mm di lato
    png = OUT / f"{nome}.png"
    qr.save(png, border=BORDO, scale=max(1, round(25 / 25.4 * 1200 / lato)),
            dark="#000000", light="#ffffff")

    verifica = rileggi(png, url)
    if verifica is None:
        esito = "non verificato (manca opencv)"
    else:
        giuste, totali, sbagliate = verifica
        ok = giuste > 0 and not sbagliate
        tutto_ok &= ok
        esito = f"{giuste}/{totali} letture esatte" if ok else \
                f"ERRORE: {giuste}/{totali} esatte, lette anche {sorted(sbagliate)}"

    print(f"{nome:13s} v{qr.version} {lato}x{lato} moduli, "
          f"{LATO_MINIMO_MM / lato:.2f} mm/modulo a {LATO_MINIMO_MM} mm  —  rilettura: {esito}")
    print(f"              {url}")

if not tutto_ok:
    raise SystemExit("\nAlmeno un QR non si rilegge come dovrebbe: NON mandarli in stampa.")
print(f"\nFile in {OUT.relative_to(ROOT)}/  —  lato minimo in stampa: {LATO_MINIMO_MM} mm")
