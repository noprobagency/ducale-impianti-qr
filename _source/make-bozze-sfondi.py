#!/usr/bin/env python3
"""
Genera le varianti di sfondo da confrontare, partendo da card/index.html.
Ogni variante e' la pagina identica con un blocco CSS di override in coda.
Eseguire dalla radice del progetto:  python3 _source/make-bozze-sfondi.py
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "card" / "index.html"
OUT  = ROOT / "bozze"

NOISE = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' "
         "numOctaves='3'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")

VARIANTI = {
 "1-aloni": ("Aloni sfumati", """
/* Sfondo 1 — e' gia' quello della pagina: solo aloni, nessuna trama */
"""),
 "2-blu": ("Velatura blu", f"""
/* Sfondo 2 — velatura verticale nel blu del marchio, niente trama */
.bg::after{{ display:none; }}
body{{ background:linear-gradient(180deg,#E7EFFA 0%,#F4F7FC 38%,#FDFDFE 100%); }}
.bg i:nth-child(1){{ opacity:.5; }}
.bg i:nth-child(3){{ opacity:.75; }}
"""),
 "3-grana": ("Aloni con grana", f"""
/* Sfondo 3 — aloni con grana finissima al posto del reticolo */
.bg::after{{
  content:""; position:absolute; inset:0;
  background-image:url("{NOISE}");
  background-size:170px 170px;
  opacity:.3; mix-blend-mode:multiply;
}}
"""),
}

html = SRC.read_text(encoding="utf-8")
if OUT.exists():
    shutil.rmtree(OUT)

righe = []
for slug, (nome, css) in VARIANTI.items():
    d = OUT / slug
    (d / "img").mkdir(parents=True)
    for f in (ROOT / "card" / "img").iterdir():
        shutil.copy2(f, d / "img" / f.name)
    pagina = html.replace("</style>", css.rstrip() + "\n</style>", 1)
    pagina = pagina.replace("<title>", f"<title>[{nome}] ", 1)
    (d / "index.html").write_text(pagina, encoding="utf-8")
    righe.append(f'<li><a href="/bozze/{slug}/">{nome}</a></li>')
    print(f"  bozze/{slug}/  — {nome}")

(OUT / "index.html").write_text(
 '<!DOCTYPE html><html lang="it"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<meta name="robots" content="noindex,nofollow">'
 '<title>Varianti di sfondo — Ducale Impianti</title>'
 '<style>body{font:16px/1.6 system-ui,sans-serif;max-width:34em;margin:12vh auto;padding:0 24px;color:#131A26}'
 'h1{font-size:22px;margin:0 0 4px}p{color:#55627A;margin:0 0 28px}'
 'ul{list-style:none;padding:0;display:grid;gap:10px}'
 'a{display:block;padding:16px 18px;border:1px solid #d9dfe8;border-radius:12px;'
 'text-decoration:none;color:inherit;font-weight:600}a:hover{border-color:#8fa3bd;background:#f6f8fb}'
 '</style></head><body><h1>Varianti di sfondo</h1>'
 '<p>Stessa pagina, cambia solo il fondo. Da guardare soprattutto da telefono.</p>'
 f'<ul>{"".join(righe)}</ul></body></html>', encoding="utf-8")

print(f"\nIndice: bozze/index.html")
