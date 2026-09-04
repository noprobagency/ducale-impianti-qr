#!/usr/bin/env python3
"""
Genera le pagine derivate a partire da quella di Ducale Impianti.

Le tre landing sono sorelle: stessa struttura, cambiano dati e colori. Tenere
una sola sorgente evita che divergano a ogni giro di correzioni sul cliente.
Qui dentro sta tutto e solo cio' che le distingue.

Eseguire dalla radice del progetto:
    python3 _source/make-pagine.py                # tutte
    python3 _source/make-pagine.py officina       # una sola
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "card" / "index.html"

BLOB_CARD = """.bg i:nth-child(1){ width:min(620px,105vw); aspect-ratio:1; top:-230px; left:-140px; background:color-mix(in srgb, var(--brand-2) 20%, transparent); }
.bg i:nth-child(2){ width:min(520px,95vw);  aspect-ratio:1; top:-90px;  right:-180px; background:color-mix(in srgb, var(--brand) 20%, transparent); }
.bg i:nth-child(3){ width:min(560px,95vw); aspect-ratio:1; bottom:-260px; left:35%; background:color-mix(in srgb, var(--brand) 11%, transparent); }"""

MAPPA = "https://maps.google.com/?q=Via+dell%27Artigianato+{n},+33043+Cividale+del+Friuli+UD"

# Al civico 95 la ricerca per indirizzo aggancia l'azienda accanto (F.lli Bordon)
# e il segnaposto cade sul capannone sbagliato, quindi si va di coordinate.
# Queste sono quelle indicate dal cliente sul posto: il civico mappato su
# OpenStreetMap cadeva 59 m piu' a sud-est, ancora sull'ingresso sbagliato.
# Scritte per esteso e non come link accorciato goo.gl, che dipende da un
# servizio esterno che puo' smettere di risolvere.
MAPPA_95 = "https://www.google.com/maps/search/?api=1&query=46.083296,13.390925"

ICONA_MAPPA = ('<svg viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>'
               '<circle cx="12" cy="10" r="3"/></svg>')
ICONA_TEL = ('<svg viewBox="0 0 24 24"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 '
             '19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 '
             '1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 '
             '2.8.7a2 2 0 0 1 1.7 2Z"/></svg>')
ICONA_MAIL = ('<svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/>'
              '<path d="m22 7-10 6L2 7"/></svg>')


def desks(coppie):
    righe = ",\n".join(f'    ["{k}",{" " * max(1, 24 - len(k))}"{v}"]' for k, v in coppie)
    return "  const DESKS = [\n" + righe + "\n  ];"


# ── Elettrica Ducale ────────────────────────────────────────────────────────
ELETTRICA = dict(
    cartella="elettrica",
    lockup=('<img src="img/logo-lockup.png" alt="Gruppo Elettrica Ducale S.r.l. — '
            'Automazione industriale" width="960" height="371">'),
    uffici=[
        ("Informazioni generali", "info@elettricaducale.it"),
        ("Amministrazione",       "amministrazione@elettricaducale.it"),
        ("Commerciale",           "commerciale@elettricaducale.it"),
        ("Acquisti",              "acquisti@elettricaducale.it"),
        ("Fornitori",             "fornitori@elettricaducale.it"),
        ("Gare e contratti",      "contratti@elettricaducale.it"),
        ("Personale",             "personale@elettricaducale.it"),
        ("Magazzino",             "magazzino@elettricaducale.it"),
    ],
    cambi=[
        ("<title>Ducale Impianti S.r.l. — Contatti ufficiali</title>",
         "<title>Elettrica Ducale S.r.l. — Contatti ufficiali</title>"),
        ("degli uffici di Ducale Impianti S.r.l., Cividale del Friuli (UD).",
         "degli uffici di Elettrica Ducale S.r.l., Cividale del Friuli (UD)."),
        ('<meta property="og:title" content="Ducale Impianti S.r.l. — Contatti ufficiali">',
         '<meta property="og:title" content="Elettrica Ducale S.r.l. — Contatti ufficiali">'),

        ("  --brand:        #0070DC;   /* blu logo — pulsanti, morsetti, bordi */\n"
         "  --brand-ink:    #0060BE;   /* blu scurito — testi e icone su chiaro (6.2:1 su bianco) */\n"
         "  --brand-2:      #FF0000;   /* rosso logo — solo l'alone di fondo a sinistra */",
         "  --brand:        #E4402F;   /* rosso logo — riempimenti, morsetti */\n"
         "  --brand-ink:    #D6342A;   /* rosso scurito — testi e link su chiaro (4.8:1 su bianco) */\n"
         "  --brand-2:      #6E6E6E;   /* grigio logo — accento secondario */"),
        ("  background:linear-gradient(160deg,#1272D6,#00539F);\n"
         "  border-color:#004E96; color:#fff;\n"
         "  box-shadow:0 10px 26px rgba(0,83,159,.28), inset 0 1px 0 rgba(255,255,255,.34);",
         "  background:linear-gradient(160deg,#EE5140,#D6342A);\n"
         "  border-color:#C02A21; color:#fff;\n"
         "  box-shadow:0 10px 26px rgba(214,52,42,.28), inset 0 1px 0 rgba(255,255,255,.34);"),
        ("  .action--primary:hover{ border-color:#003F7A; box-shadow:0 16px 34px rgba(0,83,159,.34), "
         "inset 0 1px 0 rgba(255,255,255,.34); }",
         "  .action--primary:hover{ border-color:#A4231B; box-shadow:0 16px 34px rgba(214,52,42,.34), "
         "inset 0 1px 0 rgba(255,255,255,.34); }"),
        # aloni: rosso a sinistra e a destra, grigio in fondo
        (BLOB_CARD,
         ".bg i:nth-child(1){ width:min(620px,105vw); aspect-ratio:1; top:-230px; left:-140px; "
         "background:color-mix(in srgb, var(--brand) 20%, transparent); }\n"
         ".bg i:nth-child(2){ width:min(520px,95vw);  aspect-ratio:1; top:-90px;  right:-180px; "
         "background:color-mix(in srgb, var(--brand) 13%, transparent); }\n"
         ".bg i:nth-child(3){ width:min(560px,95vw); aspect-ratio:1; bottom:-260px; left:35%; "
         "background:color-mix(in srgb, var(--brand-2) 9%, transparent); }"),

        ('href="mailto:info@ducaleimpianti.com"', 'href="mailto:info@elettricaducale.it"'),
        ('<div class="v">02718970300</div>', '<div class="v">00481860302</div>'),
        ('data-copy="02718970300"', 'data-copy="00481860302"'),
        ('ducaleimpianti@pec.ducaleimpianti.com', 'elettricaducale@pec.elettricaducale.it'),
        ('<a href="https://www.ducaleimpianti.com" target="_blank" rel="noopener">',
         '<a href="https://www.elettricaducale.it" target="_blank" rel="noopener">'),
        ('<a href="https://www.linkedin.com/company/ducale-impianti/" target="_blank" rel="noopener">',
         '<a href="https://it.linkedin.com/company/elettrica-ducale-s.r.l." target="_blank" rel="noopener">'),
        ("      Ducale Impianti S.r.l. — Società a socio unico<br>\n"
         "      P. IVA 02718970300 · Cividale del Friuli (UD)",
         "      Elettrica Ducale S.r.l. — Società a socio unico<br>\n"
         "      P. IVA 00481860302 · Cividale del Friuli (UD)"),
    ],
)

# ── Officina di carpenteria ─────────────────────────────────────────────────
# Reparto di Elettrica Ducale: stessa societa', quindi stessi dati fiscali.
# Cambiano le sedi (ne ha due), i recapiti e il colore.
AZIONI_OFFICINA = f'''    <nav class="actions rise" style="animation-delay:.1s" aria-label="Azioni rapide">
      <a class="action action--primary" href="tel:+390432733922">
        {ICONA_TEL}
        Chiama<small>0432 733922</small>
      </a>
      <a class="action" href="tel:+393285450039">
        {ICONA_TEL}
        Cellulare<small>328 545 0039</small>
      </a>
      <a class="action" href="mailto:officinameccanica@elettricaducale.it">
        {ICONA_MAIL}
        Scrivi<small>Officina</small>
      </a>
    </nav>'''

SEDI_OFFICINA = f'''    <section class="rise" style="animation-delay:.16s">
      <h2 class="label">Sedi</h2>
      <div class="card">
        <div class="venue">
          <div class="k">Sede legale</div>
          <address>
            Via dell'Artigianato, 69
            <span>33043 Cividale del Friuli (UD) — Italia</span>
          </address>
          <a class="maplink" href="{MAPPA.format(n=69)}" target="_blank" rel="noopener">
            {ICONA_MAPPA}
            Apri in mappe
          </a>
        </div>
        <div class="venue venue--altra">
          <div class="k">Sede operativa — officina</div>
          <address>
            Via dell'Artigianato, 95
            <span>33043 Cividale del Friuli (UD) — Italia</span>
          </address>
          <a class="maplink" href="{MAPPA_95}" target="_blank" rel="noopener">
            {ICONA_MAPPA}
            Apri in mappe
          </a>
        </div>
      </div>
    </section>'''

CSS_OFFICINA = """
/* Officina: due sedi nella stessa targa, separate da un filo */
.venue .k{ font:700 10.5px/1 "Lato",sans-serif; letter-spacing:.13em; text-transform:uppercase;
           color:var(--text-faint); margin-bottom:7px; }
.venue--altra{ border-top:1px solid var(--hairline-2); }
"""

OFFICINA = dict(
    cartella="officina",
    lockup=('<img src="img/logo-lockup.png" alt="Gruppo Elettrica Ducale S.r.l. — '
            'Officina di carpenteria leggera" width="960" height="374">'),
    uffici=[
        ("Informazioni generali",  "info@elettricaducale.it"),
        ("Officina di Carpenteria", "officinameccanica@elettricaducale.it"),
        ("Amministrazione",        "amministrazione@elettricaducale.it"),
        ("Fornitori",              "fornitori@elettricaducale.it"),
        ("Magazzino",              "magazzino@elettricaducale.it"),
        ("Gare e contratti",       "contratti@elettricaducale.it"),
        ("Personale",              "personale@elettricaducale.it"),
    ],
    css=CSS_OFFICINA,
    cambi=[
        ("<title>Ducale Impianti S.r.l. — Contatti ufficiali</title>",
         "<title>Officina di carpenteria — Elettrica Ducale S.r.l.</title>"),
        ('content="Riferimenti societari, dati fiscali e contatti diretti degli uffici di '
         'Ducale Impianti S.r.l., Cividale del Friuli (UD).">',
         'content="Sedi, dati fiscali e contatti diretti dell\'officina di carpenteria leggera '
         'di Elettrica Ducale S.r.l., Cividale del Friuli (UD).">'),
        ('<meta property="og:title" content="Ducale Impianti S.r.l. — Contatti ufficiali">',
         '<meta property="og:title" content="Officina di carpenteria — Elettrica Ducale S.r.l.">'),
        ('<meta name="theme-color" content="#F6F7FA">',
         '<meta name="theme-color" content="#F5F8F6">'),

        # verde del marchio; l'inchiostro e' scurito per stare sopra il 4.5:1
        ("  --brand:        #0070DC;   /* blu logo — pulsanti, morsetti, bordi */\n"
         "  --brand-ink:    #0060BE;   /* blu scurito — testi e icone su chiaro (6.2:1 su bianco) */\n"
         "  --brand-2:      #FF0000;   /* rosso logo — solo l'alone di fondo a sinistra */",
         "  --brand:        #307048;   /* verde logo — riempimenti, morsetti */\n"
         "  --brand-ink:    #2A6440;   /* verde scurito — testi e link su chiaro (6.5:1 su bianco) */\n"
         "  --brand-2:      #6E8F7A;   /* verde grigio — accento secondario */"),
        ("  --page:      #F6F7FA;", "  --page:      #F5F8F6;"),
        ("  background:linear-gradient(160deg,#1272D6,#00539F);\n"
         "  border-color:#004E96; color:#fff;\n"
         "  box-shadow:0 10px 26px rgba(0,83,159,.28), inset 0 1px 0 rgba(255,255,255,.34);",
         "  background:linear-gradient(160deg,#3E8A5A,#2A6440);\n"
         "  border-color:#245537; color:#fff;\n"
         "  box-shadow:0 10px 26px rgba(42,100,64,.28), inset 0 1px 0 rgba(255,255,255,.34);"),
        ("  .action--primary:hover{ border-color:#003F7A; box-shadow:0 16px 34px rgba(0,83,159,.34), "
         "inset 0 1px 0 rgba(255,255,255,.34); }",
         "  .action--primary:hover{ border-color:#1D452C; box-shadow:0 16px 34px rgba(42,100,64,.34), "
         "inset 0 1px 0 rgba(255,255,255,.34); }"),
        # aloni tutti nel verde, un po' piu' carichi
        (BLOB_CARD,
         ".bg i:nth-child(1){ width:min(620px,105vw); aspect-ratio:1; top:-230px; left:-140px; "
         "background:color-mix(in srgb, var(--brand-2) 26%, transparent); }\n"
         ".bg i:nth-child(2){ width:min(520px,95vw);  aspect-ratio:1; top:-90px;  right:-180px; "
         "background:color-mix(in srgb, var(--brand) 26%, transparent); }\n"
         ".bg i:nth-child(3){ width:min(560px,95vw); aspect-ratio:1; bottom:-260px; left:35%; "
         "background:color-mix(in srgb, var(--brand) 12%, transparent); }"),

        ('<div class="v">02718970300</div>', '<div class="v">00481860302</div>'),
        ('data-copy="02718970300"', 'data-copy="00481860302"'),
        ('ducaleimpianti@pec.ducaleimpianti.com', 'elettricaducale@pec.elettricaducale.it'),
        ('<a href="https://www.ducaleimpianti.com" target="_blank" rel="noopener">',
         '<a href="https://www.elettricaducale.it" target="_blank" rel="noopener">'),
        # l'officina un profilo LinkedIn non ce l'ha: si toglie la voce, non si
        # lascia un segnaposto che al clic dice che manca
        ('''        <a href="https://www.linkedin.com/company/ducale-impianti/" target="_blank" rel="noopener">
          <svg viewBox="0 0 24 24"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6Z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>
          LinkedIn
          <svg class="arrow" viewBox="0 0 24 24"><path d="M7 17 17 7M9 7h8v8"/></svg>
        </a>
''', ''),
        ('<h2 class="label">Rete e sito</h2>', '<h2 class="label">Sito</h2>'),
        ("      Ducale Impianti S.r.l. — Società a socio unico<br>\n"
         "      P. IVA 02718970300 · Cividale del Friuli (UD)",
         "      Elettrica Ducale S.r.l. — Officina di carpenteria leggera<br>\n"
         "      P. IVA 00481860302 · Cividale del Friuli (UD)"),
    ],
    blocchi=[("<nav ", "</nav>", AZIONI_OFFICINA), ("<section ", "</section>", SEDI_OFFICINA)],
)

PAGINE = {"elettrica": ELETTRICA, "officina": OFFICINA}


def genera(cfg):
    html = SRC.read_text(encoding="utf-8")

    # la lockup si sostituisce sempre: cambia immagine, testo alternativo e misure
    inizio = html.index('<img src="img/logo-lockup.png"')
    fine = html.index(">", inizio) + 1
    html = html[:inizio] + cfg["lockup"] + html[fine:]

    for cerca, sostituisci in cfg["cambi"]:
        if cerca not in html:
            raise SystemExit(
                "Testo non trovato nella pagina di Ducale Impianti: e' cambiata e "
                f"_source/make-pagine.py va aggiornato.\n\n{cerca[:200]}")
        html = html.replace(cerca, sostituisci)

    # blocchi interi (azioni rapide, sedi): si sostituisce dal primo tag al suo chiudere
    for apre, chiude, nuovo in cfg.get("blocchi", []):
        i = html.index(apre)
        i = html.rindex("\n", 0, i) + 1          # includi l'indentazione
        j = html.index(chiude, i) + len(chiude)
        html = html[:i] + nuovo + html[j:]

    inizio = html.index("  const DESKS = [")
    fine = html.index("];", inizio) + 2
    html = html[:inizio] + desks(cfg["uffici"]) + html[fine:]

    if cfg.get("css"):
        html = html.replace("</style>", cfg["css"].rstrip() + "\n</style>", 1)

    out = ROOT / cfg["cartella"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    residui = [t for t in ("ducaleimpianti", "Ducale Impianti", "02718970300") if t in html]
    print(f"{cfg['cartella']}/index.html — {len(cfg['uffici'])} uffici, "
          f"residui Ducale Impianti: {residui or 'nessuno'}")


scelte = sys.argv[1:] or list(PAGINE)
for chiave in scelte:
    if chiave not in PAGINE:
        raise SystemExit(f"Pagina sconosciuta: {chiave}. Valide: {', '.join(PAGINE)}")
    genera(PAGINE[chiave])
