#!/usr/bin/env python3
"""
Verifica completa: QR in tutti i formati + pagine in produzione.

Eseguire dalla radice del progetto:  python3 _source/verifica.py
Serve:  pip install segno opencv-python-headless   (e macOS, per sips e qlmanage)

Non si fida degli script che generano: ha qui la sua lista di cosa deve essere
vero, e controlla QR e siti contro quella. Da rilanciare dopo ogni modifica.
"""
import re, subprocess, sys, tempfile, urllib.request, urllib.error, urllib.parse
from pathlib import Path
import cv2, numpy as np, segno

ROOT = Path(__file__).resolve().parent.parent
TMP = Path(tempfile.mkdtemp(prefix="verifica-qr-"))
UTM = "?utm_source=biglietto&utm_medium=qr"
UA = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) verifica-qr"}

ATTESE = {
    "impiantielettrici-qr": dict(
        url="https://www.ducaleimpianti.com/impiantielettrici-qr/",
        titolo="Ducale Impianti S.r.l. — Contatti ufficiali",
        piva="02718970300", pec="ducaleimpianti@pec.ducaleimpianti.com",
        tel=["tel:+390432733922"], dominio_mail="ducaleimpianti.com", uffici=8,
        sito="https://www.ducaleimpianti.com",
        linkedin="https://www.linkedin.com/company/ducale-impianti/"),
    "quadri-qr": dict(
        url="https://www.elettricaducale.it/quadri-qr/",
        titolo="Elettrica Ducale S.r.l. — Contatti ufficiali",
        piva="00481860302", pec="elettricaducale@pec.elettricaducale.it",
        tel=["tel:+390432733922"], dominio_mail="elettricaducale.it", uffici=8,
        sito="https://www.elettricaducale.it",
        linkedin="https://it.linkedin.com/company/elettrica-ducale-s.r.l."),
    "officinacarpenteria-qr": dict(
        url="https://www.elettricaducale.it/officinacarpenteria-qr/",
        titolo="Officina di carpenteria — Elettrica Ducale S.r.l.",
        piva="00481860302", pec="elettricaducale@pec.elettricaducale.it",
        tel=["tel:+390432733922", "tel:+393285450039"], dominio_mail="elettricaducale.it", uffici=7,
        sito="https://www.elettricaducale.it", linkedin=None,
        mappa_95="46.083296,13.390925"),
}

errori = []
def esito(ok, testo):
    print(f"   {'✓' if ok else '✗'} {testo}")
    if not ok:
        errori.append(testo)
    return ok


# ─── lettura dei QR ─────────────────────────────────────────────────────────
LETTORI = [cv2.QRCodeDetector(), cv2.QRCodeDetectorAruco()]

def decodifica(img):
    """Tutte le letture, a piu' misure e con due lettori."""
    letture = []
    for lato in (img.shape[0], 600, 400, 300, 200):
        r = cv2.resize(img, (lato, lato), interpolation=cv2.INTER_AREA)
        for l in LETTORI:
            t, *_ = l.detectAndDecode(r)
            letture.append(t)
    return letture

def matrice(img, moduli):
    """Campiona il centro di ogni modulo: 1 nero, 0 bianco."""
    g = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    passo = g.shape[0] / moduli
    return np.array([[1 if g[int((y + .5) * passo), int((x + .5) * passo)] < 128 else 0
                      for x in range(moduli)] for y in range(moduli)])

def eps_a_immagine(percorso, moduli, px=12):
    """Ridisegna l'EPS di segno: tratti orizzontali di un modulo, in coordinate
    relative, con l'origine in basso a sinistra come in PostScript."""
    testo = percorso.read_text()
    corpo = testo.split("newpath", 1)[1].split("stroke", 1)[0].split()
    img = np.full((moduli * px, moduli * px), 255, np.uint8)
    x, y = float(corpo[0]), float(corpo[1])
    i = 3                                                   # salta "x y moveto"
    while i + 2 < len(corpo):
        dx, dy, op = float(corpo[i]), float(corpo[i + 1]), corpo[i + 2]
        if op == "l":
            riga = moduli - 1 - int(y)                      # da basso-sinistra ad alto-sinistra
            img[riga * px:(riga + 1) * px, int(x) * px:int(x + dx) * px] = 0
        x, y = x + dx, y + dy
        i += 3
    return img

def raster(fmt, file):
    if fmt == "png":
        return cv2.imread(str(file))
    if fmt == "pdf":
        out = TMP / (file.stem + "-pdf.png")
        subprocess.run(["sips", "-s", "format", "png", "-Z", "1200", str(file), "--out", str(out)],
                       check=True, capture_output=True)
        return cv2.imread(str(out))
    if fmt == "svg":
        subprocess.run(["qlmanage", "-t", "-s", "1200", "-o", str(TMP), str(file)],
                       check=True, capture_output=True, timeout=60)
        return cv2.imread(str(TMP / (file.name + ".png")))
    raise ValueError(fmt)

def scatto_da_telefono(img):
    """Simula la foto di un biglietto stampato a 22 mm: pochi pixel per modulo,
    sfocatura, compressione JPEG e il codice un po' storto."""
    piccolo = cv2.resize(img, (150, 150), interpolation=cv2.INTER_AREA)   # ~3 px per modulo
    tela = np.full((260, 260, 3), 235, np.uint8)
    tela[55:205, 55:205] = piccolo
    m = cv2.getRotationMatrix2D((130, 130), 8, 1.0)
    storto = cv2.warpAffine(tela, m, (260, 260), borderValue=(235, 235, 235))
    sfocato = cv2.GaussianBlur(storto, (3, 3), 0.9)
    ok, jpg = cv2.imencode(".jpg", sfocato, [cv2.IMWRITE_JPEG_QUALITY, 55])
    return cv2.imdecode(jpg, cv2.IMREAD_COLOR)


# ─── rete ───────────────────────────────────────────────────────────────────
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None
SENZA_REDIRECT = urllib.request.build_opener(NoRedirect)

def get(url, segui=True):
    req = urllib.request.Request(url, headers=UA)
    try:
        r = (urllib.request.urlopen if segui else SENZA_REDIRECT.open)(req, timeout=20)
        return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, url, b""


# ─── il test ────────────────────────────────────────────────────────────────
for nome, a in ATTESE.items():
    print(f"\n━━ {nome} ━━")
    atteso = a["url"] + UTM
    riferimento = segno.make(atteso, error="m", boost_error=False, micro=False)
    moduli = riferimento.symbol_size(border=4)[0]
    matrice_attesa = np.array([[1 if v else 0 for v in riga]
                               for riga in riferimento.matrix_iter(border=4)])

    print(" QR, formato per formato:")
    for fmt in ("pdf", "svg", "eps", "png"):
        file = ROOT / "qr" / f"{nome}.{fmt}"
        img = eps_a_immagine(file, moduli) if fmt == "eps" else raster(fmt, file)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img
        letture = decodifica(img)
        esatte = sum(t == atteso for t in letture)
        sbagliate = {t for t in letture if t and t != atteso}
        identica = np.array_equal(matrice(img, moduli), matrice_attesa)
        esito(esatte > 0 and not sbagliate and identica,
              f"{fmt.upper():3s}  {esatte}/{len(letture)} letture esatte, nessuna sbagliata, "
              f"{'disegno identico' if identica else 'DISEGNO DIVERSO'} modulo per modulo "
              f"({moduli}x{moduli})" + (f"  LETTE: {sbagliate}" if sbagliate else ""))
        if fmt == "png":
            foto = scatto_da_telefono(img)
            letto = next((t for l in LETTORI for t in [l.detectAndDecode(foto)[0]] if t), "")
            esito(letto == atteso, "foto simulata del biglietto a 22 mm (3 px/modulo, storta, "
                                   "sfocata, JPEG): " + ("letta esatta" if letto == atteso else f"letto {letto!r}"))

    print(" Pagina in produzione, raggiunta dal QR:")
    stato, finale, _ = get(atteso, segui=False)
    esito(stato == 200, f"l'indirizzo del QR risponde {stato} al primo colpo, senza reindirizzamenti")
    stato, finale, corpo = get(atteso)
    html = corpo.decode("utf-8", errors="replace")
    esito(corpo == (ROOT / nome / "index.html").read_bytes(),
          "pagina online identica al byte a quella approvata")
    titolo = re.search(r"<title>(.*?)</title>", html)
    esito(titolo and titolo.group(1) == a["titolo"], f"titolo: {titolo.group(1) if titolo else '?'}")

    risorse = sorted(set(re.findall(r'(?:src|href)="(img/[^"]+)"', html)))
    rotte = []
    for r in risorse:
        s, _, b = get(urllib.parse.urljoin(a["url"], r))
        if s != 200 or b != (ROOT / nome / r).read_bytes():
            rotte.append(f"{r} ({s})")
    esito(not rotte, f"{len(risorse)} immagini e icone online, tutte identiche" if not rotte
          else f"immagini con problemi: {rotte}")

    print(" Contenuti:")
    tel = re.findall(r'href="(tel:[^"]+)"', html)
    esito(tel == a["tel"], f"telefoni: {', '.join(t[4:] for t in tel)}")
    esito(f'data-copy="{a["piva"]}"' in html and f">{a['piva']}<" in html, f"P. IVA {a['piva']}")
    esito('data-copy="MJ1OYNU"' in html, "codice SDI MJ1OYNU, con la lettera O")
    esito(f'data-copy="{a["pec"]}"' in html, f"PEC {a['pec']}")
    uffici = re.findall(r'\["[^"]+",\s*"([^"]+@[^"]+)"\]', html)
    esito(len(uffici) == a["uffici"] and all(u.endswith("@" + a["dominio_mail"]) for u in uffici),
          f"{len(uffici)} uffici, tutti @{a['dominio_mail']}")
    # mailto:${v} e' il modello JavaScript da cui nascono i pulsanti degli uffici,
    # non un indirizzo: gli uffici veri sono gia' controllati sopra, dall'array DESKS
    for mail in set(re.findall(r'href="mailto:([^"$]+)"', html)):
        esito(mail.endswith("@" + a["dominio_mail"]), f"pulsante Scrivi → {mail}")

    print(" Collegamenti esterni:")
    esterni = [h for h in re.findall(r'href="(https?://[^"]+)"', html)
               if "fonts.g" not in h]
    esito(a["sito"] in esterni, f"sito {a['sito']}")
    li = [h for h in esterni if "linkedin" in h]
    if a["linkedin"]:
        esito(li == [a["linkedin"]], f"LinkedIn {a['linkedin']}")
    else:
        esito(not li, "nessun LinkedIn, come richiesto")
    if a.get("mappa_95"):
        esito(any(a["mappa_95"] in h for h in esterni), f"mappa sede operativa sulle coordinate {a['mappa_95']}")
    for h in sorted(set(esterni)):
        s, dove, _ = get(h)
        # LinkedIn e Google a volte rispondono in modo strano ai programmi: 999 e' il
        # blocco anti-robot di LinkedIn, non una pagina inesistente
        ok = s == 200 or (s == 999 and "linkedin" in h)
        esito(ok, f"{s}  {h[:88]}")

print("\n" + ("TUTTO OK" if not errori else f"{len(errori)} PROBLEMI:\n  - " + "\n  - ".join(errori)))
sys.exit(1 if errori else 0)
