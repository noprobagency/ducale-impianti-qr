#!/usr/bin/env python3
"""
Genera il set di favicon per la landing QR a partire dal logo sorgente.
Eseguire dalla radice del progetto:  python3 _source/make-favicons.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "_source" / "Logo-ED.webp"
OUT  = ROOT / "card" / "img"
OUT.mkdir(parents=True, exist_ok=True)

if not SRC.exists():
    raise SystemExit(f"Logo sorgente non trovato: {SRC}")

src = Image.open(SRC).convert("RGBA")
logo = src.crop(src.getbbox())          # rimuove il margine trasparente

# Logo completo, con la scritta "dal 1973": va nella pagina
logo.save(OUT / "logo.png", optimize=True)

# Solo il monogramma circolare: alle dimensioni da favicon la scritta
# diventa illeggibile, quindi si taglia via la fascia inferiore.
h_mark = int(logo.height * 0.78)
mark = logo.crop((0, 0, logo.width, h_mark))
mark = mark.crop(mark.getbbox())

def fit(img, size, pad=0.05, bg=None):
    """Inscrive l'immagine in un quadrato con margine, senza deformarla."""
    inner = int(size * (1 - pad * 2))
    w, h = img.size
    s = min(inner / w, inner / h)
    r = img.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    canvas.paste(r, ((size - r.width) // 2, (size - r.height) // 2), r)
    return canvas

for s in (16, 32, 192):
    fit(mark, s).save(OUT / f"favicon-{s}.png", optimize=True)

fit(mark, 256).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

# iOS ignora la trasparenza nelle icone della schermata home: serve fondo bianco
fit(mark, 180, pad=0.12, bg=(255, 255, 255, 255)) \
    .convert("RGB").save(OUT / "apple-touch-icon.png", optimize=True)

print(f"Monogramma ritagliato: {mark.size[0]}x{mark.size[1]} px")
for f in sorted(OUT.iterdir()):
    print(f"  {f.name:24s} {f.stat().st_size / 1024:6.1f} KB")
