#!/usr/bin/env python3
"""
Genera la pagina di Elettrica Ducale da quella di Ducale Impianti.

Le due landing sono gemelle: stessa struttura, cambiano dati e colori. Tenere
una sola sorgente evita che divergano a ogni giro di correzioni sul cliente.

Eseguire dalla radice del progetto:  python3 _source/make-elettrica.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "card" / "index.html"
OUT  = ROOT / "elettrica" / "index.html"

UFFICI = """  const DESKS = [
    ["Informazioni generali", "info@elettricaducale.it"],
    ["Amministrazione",       "amministrazione@elettricaducale.it"],
    ["Commerciale",           "commerciale@elettricaducale.it"],
    ["Acquisti",              "acquisti@elettricaducale.it"],
    ["Fornitori",             "fornitori@elettricaducale.it"],
    ["Gare e contratti",      "contratti@elettricaducale.it"],
    ["Personale",             "personale@elettricaducale.it"],
    ["Magazzino",             "magazzino@elettricaducale.it"],
    ["Officina e carpenteria","officinameccanica@elettricaducale.it"]
  ];"""

# (cerca, sostituisci) — ognuna deve trovare riscontro, altrimenti si ferma
CAMBI = [
    # --- intestazione del documento ---
    ("<title>Ducale Impianti S.r.l. — Contatti ufficiali</title>",
     "<title>Elettrica Ducale S.r.l. — Contatti ufficiali</title>"),
    ("contatti diretti degli uffici di Ducale Impianti S.r.l., Cividale del Friuli (UD).",
     "contatti diretti degli uffici di Elettrica Ducale S.r.l., Cividale del Friuli (UD)."),
    ('<meta property="og:title" content="Ducale Impianti S.r.l. — Contatti ufficiali">',
     '<meta property="og:title" content="Elettrica Ducale S.r.l. — Contatti ufficiali">'),

    # --- colori: rosso del marchio Elettrica Ducale, grigio come secondario ---
    ("  --brand:        #FF0000;   /* rosso logo — riempimenti, morsetti */\n"
     "  --brand-ink:    #D6000A;   /* rosso scurito — testi e link su chiaro */\n"
     "  --brand-2:      #0070DC;   /* blu logo — accento secondario */",
     "  --brand:        #E4402F;   /* rosso logo — riempimenti, morsetti */\n"
     "  --brand-ink:    #D6342A;   /* rosso scurito — testi e link su chiaro (4.8:1 su bianco) */\n"
     "  --brand-2:      #6E6E6E;   /* grigio logo — accento secondario */"),
    ("  background:linear-gradient(160deg,#FF2020,#DD000C);\n"
     "  border-color:#C8000A; color:#fff;\n"
     "  box-shadow:0 10px 26px rgba(214,0,10,.28), inset 0 1px 0 rgba(255,255,255,.34);",
     "  background:linear-gradient(160deg,#EE5140,#D6342A);\n"
     "  border-color:#C02A21; color:#fff;\n"
     "  box-shadow:0 10px 26px rgba(214,52,42,.28), inset 0 1px 0 rgba(255,255,255,.34);"),
    ("  .action--primary:hover{ border-color:#A80008; box-shadow:0 16px 34px rgba(214,0,10,.34), "
     "inset 0 1px 0 rgba(255,255,255,.34); }",
     "  .action--primary:hover{ border-color:#A4231B; box-shadow:0 16px 34px rgba(214,52,42,.34), "
     "inset 0 1px 0 rgba(255,255,255,.34); }"),
    # il grigio come alone di fondo resterebbe smorto: si tiene solo il rosso
    (".bg i:nth-child(2){ width:min(520px,95vw);  aspect-ratio:1; top:-90px;  right:-180px; "
     "background:color-mix(in srgb, var(--brand-2) 20%, transparent); }",
     ".bg i:nth-child(2){ width:min(520px,95vw);  aspect-ratio:1; top:-90px;  right:-180px; "
     "background:color-mix(in srgb, var(--brand) 13%, transparent); }"),
    (".bg i:nth-child(3){ width:min(560px,95vw); aspect-ratio:1; bottom:-260px; left:35%; "
     "background:color-mix(in srgb, var(--brand-2) 11%, transparent); }",
     ".bg i:nth-child(3){ width:min(560px,95vw); aspect-ratio:1; bottom:-260px; left:35%; "
     "background:color-mix(in srgb, var(--brand-2) 9%, transparent); }"),

    # --- marchio e testata ---
    ('<img src="img/logo-lockup.png" alt="Gruppo Ducale Impianti S.r.l. — Costruzioni Tecnologiche" width="734" height="268">',
     '<img src="img/logo-lockup.png" alt="Gruppo Elettrica Ducale S.r.l. — Automazione industriale" width="960" height="371">'),

    # --- contatti ---
    ('href="mailto:info@ducaleimpianti.com"', 'href="mailto:info@elettricaducale.it"'),

    # --- dati fiscali (SDI e sede coincidono: stesso gruppo, stessa sede) ---
    ('<div class="v">02718970300</div>', '<div class="v">00481860302</div>'),
    ('data-copy="02718970300"', 'data-copy="00481860302"'),
    ('<div class="v" style="font-size:13.5px">ducaleimpianti@pec.ducaleimpianti.com</div>',
     '<div class="v" style="font-size:13.5px">elettricaducale@pec.elettricaducale.it</div>'),
    ('data-copy="ducaleimpianti@pec.ducaleimpianti.com"',
     'data-copy="elettricaducale@pec.elettricaducale.it"'),

    # --- rete ---
    ('<a href="https://www.ducaleimpianti.com" target="_blank" rel="noopener">',
     '<a href="https://www.elettricaducale.it" target="_blank" rel="noopener">'),

    # --- pie' di pagina ---
    ("      Ducale Impianti S.r.l. — Società a socio unico<br>\n"
     "      P. IVA 02718970300 · Cividale del Friuli (UD)",
     "      Elettrica Ducale S.r.l. — Società a socio unico<br>\n"
     "      P. IVA 00481860302 · Cividale del Friuli (UD)"),
]

html = SRC.read_text(encoding="utf-8")

for cerca, sostituisci in CAMBI:
    if cerca not in html:
        raise SystemExit(
            "Testo non trovato nella pagina di Ducale Impianti — e' cambiata "
            f"e questo script va aggiornato:\n\n{cerca[:160]}")
    html = html.replace(cerca, sostituisci)

# gli uffici sono nove invece di otto: si sostituisce l'array intero
inizio = html.index("  const DESKS = [")
fine   = html.index("];", inizio) + 2
html = html[:inizio] + UFFICI + html[fine:]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")

rimasti = [t for t in ("ducaleimpianti", "Ducale Impianti", "02718970300") if t in html]
print(f"Scritto {OUT.relative_to(ROOT)}")
print("Riferimenti a Ducale Impianti rimasti:", rimasti or "nessuno")
