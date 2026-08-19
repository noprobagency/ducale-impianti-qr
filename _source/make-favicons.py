#!/usr/bin/env python3
"""
Genera logo e favicon delle landing QR dalle lockup del gruppo.

Eseguire dalla radice del progetto:
    python3 _source/make-favicons.py                 # tutte e due le aziende
    python3 _source/make-favicons.py elettrica       # solo una

La sorgente e' un JPEG su fondo bianco: lo sfondo viene reso trasparente,
poi si ritagliano da soli tre pezzi diversi, perche' servono a cose diverse:

  logo.png         marchio completo (GRUPPO + cerchio + dal 1973) -> riquadro in pagina
  logo-lockup.png  lockup intera con la scritta -> se un giorno serve a piena larghezza
  favicon-*        solo il cerchio: a 16px GRUPPO e dal 1973 sono macchie illeggibili
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

AZIENDE = {
    "card":      ("Logo-Gruppo-Ducale-Impianti.jpg",  "Ducale Impianti"),
    "elettrica": ("Logo-Gruppo-Elettrica-Ducale.jpg", "Elettrica Ducale"),
}

SOGLIA = 235   # sopra questo livello il pixel e' considerato sfondo


def smatta_bianco(im):
    """Toglie il fondo bianco ricavando l'alfa, conservando i bordi sfumati."""
    im = im.convert("RGB")
    out = Image.new("RGBA", im.size)
    sp, dp = im.load(), out.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b = sp[x, y]
            a = 255 - min(r, g, b)          # quanto il pixel si stacca dal bianco
            if a <= 4:
                dp[x, y] = (0, 0, 0, 0)
                continue
            f = 255 / a                      # scontorna il bianco premoltiplicato
            dp[x, y] = (
                max(0, min(255, round((r - (255 - a)) * f))),
                max(0, min(255, round((g - (255 - a)) * f))),
                max(0, min(255, round((b - (255 - a)) * f))),
                a,
            )
    return out


def colonne_piene(im):
    px, (w, h) = im.load(), im.size
    return [any(min(px[x, y][:3]) < SOGLIA for y in range(h)) for x in range(w)]


def taglio_marchio(im):
    """Trova il corridoio bianco piu' largo: separa il marchio dalla scritta."""
    piene = colonne_piene(im)
    best = (0, None)
    run = start = 0
    for x, c in enumerate(piene):
        if c:
            run = 0
        else:
            if run == 0:
                start = x
            run += 1
            if run > best[0]:
                best = (run, start)
    larghezza, inizio = best
    if inizio is None:
        raise SystemExit("Nessun corridoio bianco: la sorgente non e' una lockup.")
    return inizio + larghezza // 2


def riquadro_cerchio(marchio):
    """Ritaglia il solo cerchio.

    Non si puo' cercare la banda "piu' larga di X": in una circonferenza le
    righe si stringono proprio in cima e in fondo, e la soglia mangerebbe le
    calotte. Si sfrutta invece la geometria: la riga piu' larga e' l'equatore,
    quella larghezza e' il diametro, e il cerchio e' il quadrato che ne segue.
    """
    px, (w, h) = marchio.load(), marchio.size
    estremi = []
    for y in range(h):
        xs = [x for x in range(w) if px[x, y][3] > 24]
        estremi.append((xs[0], xs[-1]) if xs else None)
    larghezze = [(e[1] - e[0]) if e else 0 for e in estremi]
    diametro = max(larghezze)
    equatore = larghezze.index(diametro)
    sinistra, destra = estremi[equatore]
    raggio = diametro / 2
    return (sinistra,
            max(0, round(equatore - raggio)),
            destra + 1,
            min(h, round(equatore + raggio) + 1)), raggio


def fuori_dal_cerchio(img, raggio):
    """Cancella cio' che sporge oltre il bordo: la coda di dal 1973 arriva
    fin dentro il riquadro del cerchio, ma resta fuori dalla circonferenza."""
    px, (w, h) = img.load(), img.size
    cx, cy = (w - 1) / 2, (h - 1) / 2
    limite = (raggio + 1.5) ** 2
    for y in range(h):
        for x in range(w):
            if (x - cx) ** 2 + (y - cy) ** 2 > limite:
                px[x, y] = (0, 0, 0, 0)
    return img


def rinforza(img, gamma=0.45):
    """Ravviva i tratti sottili dopo la riduzione.

    Il marchio Elettrica Ducale e' disegnato a filo, non pieno: a 16 o 32 px
    l'interpolazione spalma ogni tratto su meno di un pixel e il risultato
    sbianca fino a sparire. Alzare l'alfa con una gamma < 1 restituisce corpo
    al segno senza toccarne il colore.
    """
    px, (w, h) = img.load(), img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (r, g, b, round(255 * (a / 255) ** gamma))
    return img


def alleggerisci(img, colori=64):
    """Riduce a tavolozza: il marchio ha pochi colori piatti, ma il PNG a
    colore pieno li salva come una fotografia e pesa cinque volte tanto."""
    return img.quantize(colors=colori, method=Image.FASTOCTREE)


def inscrivi(img, lato, margine=0.05, fondo=None):
    """Inscrive l'immagine in un quadrato con margine, senza deformarla."""
    interno = int(lato * (1 - margine * 2))
    w, h = img.size
    s = min(interno / w, interno / h)
    r = img.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    tela = Image.new("RGBA", (lato, lato), fondo or (0, 0, 0, 0))
    tela.paste(r, ((lato - r.width) // 2, (lato - r.height) // 2), r)
    return tela


def genera(cartella, file_logo, nome):
    src = ROOT / "_source" / file_logo
    if not src.exists():
        raise SystemExit(f"Logo sorgente non trovato: {src}")
    out = ROOT / cartella / "img"
    out.mkdir(parents=True, exist_ok=True)

    sorgente = smatta_bianco(Image.open(src))
    lockup = sorgente.crop(sorgente.getbbox())
    # in pagina la lockup sta in circa 320 px: oltre i 960 si pagherebbero
    # centinaia di KB che nessuno schermo, nemmeno a 3x, arriva a mostrare
    if lockup.width > 960:
        lockup = lockup.resize(
            (960, round(lockup.height * 960 / lockup.width)), Image.LANCZOS)
    alleggerisci(lockup).save(out / "logo-lockup.png", optimize=True)

    x = taglio_marchio(Image.open(src).convert("RGB"))
    marchio = sorgente.crop((0, 0, x, sorgente.height))
    marchio = marchio.crop(marchio.getbbox())
    alleggerisci(marchio).save(out / "logo.png", optimize=True)

    riquadro, raggio = riquadro_cerchio(marchio)
    cerchio = fuori_dal_cerchio(marchio.crop(riquadro), raggio)

    for s in (16, 32, 192):
        icona = inscrivi(cerchio, s)
        if s <= 32:                       # piu' si rimpicciolisce, piu' serve corpo
            icona = rinforza(icona, 0.28 if s <= 16 else 0.45)
        (alleggerisci(icona) if s >= 192 else icona).save(
            out / f"favicon-{s}.png", optimize=True)

    rinforza(inscrivi(cerchio, 256), 0.75).save(
        out / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    # iOS ignora la trasparenza nelle icone della schermata home: serve fondo bianco
    inscrivi(cerchio, 180, margine=0.12, fondo=(255, 255, 255, 255)) \
        .convert("RGB").save(out / "apple-touch-icon.png", optimize=True)

    print(f"\n{nome}  ->  {cartella}/img/")
    print(f"  marchio {marchio.width}x{marchio.height} px, "
          f"cerchio {cerchio.width}x{cerchio.height} px")
    for f in sorted(out.iterdir()):
        print(f"    {f.name:24s} {f.stat().st_size / 1024:6.1f} KB")
    return marchio.size


scelte = sys.argv[1:] or list(AZIENDE)
for chiave in scelte:
    if chiave not in AZIENDE:
        raise SystemExit(f"Azienda sconosciuta: {chiave}. Valide: {', '.join(AZIENDE)}")
    genera(chiave, *AZIENDE[chiave])
