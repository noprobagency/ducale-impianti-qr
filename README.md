# Landing QR — Ducale Impianti S.r.l.

Pagina statica singola raggiunta dal QR code stampato. Nessuna dipendenza:
niente framework, niente build, niente npm. Si apre anche con un doppio clic
su `card/index.html`.

## Cosa caricare

Va online **solo il contenuto della cartella `card/`**:

```
card/
├── index.html
└── img/
    ├── logo.png
    ├── favicon.ico
    ├── favicon-16.png
    ├── favicon-32.png
    ├── favicon-192.png
    └── apple-touch-icon.png
```

`_source/` resta in locale e non va mai caricata sull'hosting: contiene il logo
sorgente e lo script che rigenera le favicon.

## Destinazione

Copiare il contenuto di `card/` in `/public_html/card/`, sulla radice del sito
WordPress di `ducaleimpianti.com`.

Indirizzo risultante:

```
https://www.ducaleimpianti.com/card/
```

Verificato il 14 agosto 2026: `https://www.ducaleimpianti.com/card/` risponde
404, quindi lo slug `card` è libero e non collide con nessuna pagina esistente.

### Perché funziona senza toccare WordPress

L'`.htaccess` standard di WordPress contiene:

```apache
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
```

cioè WordPress non intercetta i file e le cartelle che esistono davvero su
disco. Una cartella statica dentro `public_html` viene quindi servita
direttamente da Apache, senza passare dal CMS.

## Avvertenze

1. **Non creare in WordPress una pagina con slug `card`.** Manderebbe in
   conflitto le due cose e vincerebbe WordPress.
2. **Plugin di sicurezza** (Wordfence, iThemes Security, Sucuri) a volte
   bloccano l'esecuzione in cartelle fuori standard. Se l'indirizzo risponde
   403, la causa è quasi sempre lì.
3. **Cache e Cloudflare.** Una cartella statica non viene toccata dai plugin di
   cache, ma se dopo un aggiornamento vedi ancora la versione vecchia, svuota
   comunque la cache del plugin e quella di Cloudflare.
4. **Permessi:** cartelle `755`, file `644`.
5. **HTTPS e www.** L'indirizzo messo nel QR deve corrispondere esattamente alla
   forma canonica del sito, per non aggiungere un redirect prima di mostrare la
   pagina. Verificato: `ducaleimpianti.com`, `www.ducaleimpianti.com` e le
   varianti in `http://` rispondono tutte `301` verso
   `https://www.ducaleimpianti.com/`. La forma canonica è quindi **con `www` e
   in `https`** — nel QR va `https://www.ducaleimpianti.com/card/`.
6. **Aggiornamenti futuri.** Si modifica solo `card/index.html`. I dati degli
   uffici stanno nell'array `DESKS` in cima allo script, in fondo al file; i
   colori nel blocco `:root`, all'inizio del CSS.

## Rigenerare le favicon

Serve Pillow (`pip install pillow`, oppure
`pip install pillow --break-system-packages` se il sistema lo richiede).
Dalla radice del progetto:

```bash
python3 _source/make-favicons.py
```

Lo script parte da `_source/Logo-ED.webp`, salva il logo completo in
`card/img/logo.png` e ricava le favicon dal solo monogramma circolare,
tagliando via la fascia inferiore con la scritta *dal 1973* — a 16 o 32 pixel
diventerebbe una macchia illeggibile. L'`apple-touch-icon` ha fondo bianco
perché iOS non gestisce la trasparenza nelle icone della schermata home.

## Tracciamento delle scansioni

Per distinguere da quale supporto stampato arriva la scansione, si aggiungono i
parametri direttamente nell'indirizzo del QR, uno diverso per ogni supporto:

```
https://www.ducaleimpianti.com/card/?utm_source=qr&utm_medium=print&utm_campaign=biglietti
https://www.ducaleimpianti.com/card/?utm_source=qr&utm_medium=print&utm_campaign=mezzi
https://www.ducaleimpianti.com/card/?utm_source=qr&utm_medium=print&utm_campaign=cantieri
```

La pagina li ignora: servono solo alla statistica lato server o ad Analytics, se
in futuro verrà aggiunto.

Usare un **QR statico, non dinamico**: i generatori dinamici gratuiti scadono e
trasformerebbero il materiale già stampato in carta straccia.

## Da completare

- **Link LinkedIn.** Oggi è un segnaposto che al clic avvisa che manca. Quando
  arriva l'indirizzo: sostituire l'`href` e togliere l'attributo
  `data-placeholder`.
- **Verifica del logo.** Il monogramma è `ED`, di Elettrica Ducale. Se Ducale
  Impianti ha un marchio proprio diverso, va sostituito `_source/Logo-ED.webp` e
  rieseguito lo script delle favicon.
