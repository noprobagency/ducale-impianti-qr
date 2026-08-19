# Landing QR — Gruppo Ducale

Due pagine statiche gemelle, raggiunte dai rispettivi QR code stampati, una per
azienda del gruppo. Nessuna dipendenza: niente framework, niente build, niente
npm. Si aprono anche con un doppio clic sull'`index.html`.

| Cartella | Azienda | Destinazione |
|---|---|---|
| `card/` | Ducale Impianti S.r.l. | `https://www.ducaleimpianti.com/card/` |
| `elettrica/` | Elettrica Ducale S.r.l. | `https://www.elettricaducale.it/card/` |

Le due aziende hanno siti distinti, quindi ogni pagina va sul dominio della
propria azienda, in entrambi i casi nella cartella `card/`. In anteprima
convivono sullo stesso indirizzo solo perche' e' un unico deploy.

**La pagina di Elettrica Ducale non si modifica a mano:** si genera da quella di
Ducale Impianti, cosi' le due non divergono a ogni giro di correzioni.

```bash
python3 _source/make-elettrica.py
```

Lo script si ferma con un errore se un testo che deve sostituire non esiste
piu': se hai cambiato la pagina di Ducale Impianti in un punto che lo riguarda,
te ne accorgi subito invece di ritrovarti dati vecchi nella pagina gemella.

## Cosa caricare

Va online **solo il contenuto della cartella dell'azienda** (`card/` oppure
`elettrica/`):

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

Ogni cartella ha il proprio `img/`, con logo e favicon della sua azienda.

`_source/` resta in locale e non va mai caricata sull'hosting: contiene i loghi
sorgente e gli script che generano immagini e pagina gemella.

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
6. **Aggiornamenti futuri.** Si modifica solo `card/index.html`, poi si rigenera
   la pagina gemella. I dati degli uffici stanno nell'array `DESKS` in cima allo
   script, in fondo al file; i colori nel blocco `:root`, all'inizio del CSS.
   Quello che e' specifico di Elettrica Ducale — dati, colori, nono ufficio —
   sta tutto in `_source/make-elettrica.py`.

## Rigenerare logo e favicon

Serve Pillow (`pip install pillow`, oppure
`pip install pillow --break-system-packages` se il sistema lo richiede).
Dalla radice del progetto:

```bash
python3 _source/make-favicons.py
```

Senza argomenti fa entrambe le aziende; `python3 _source/make-favicons.py
elettrica` ne fa una sola.

Parte dalle lockup in `_source/`, che sono JPEG su fondo bianco: lo sfondo viene
scontornato ricavando l'alfa, poi si ritagliano tre pezzi diversi perche'
servono a cose diverse.

- `logo.png` — il solo marchio (GRUPPO + cerchio + *dal 1973*), per il riquadro
  in cima alla pagina. Il taglio fra marchio e scritta viene trovato da solo,
  cercando il corridoio bianco piu' largo.
- `logo-lockup.png` — la lockup intera, se un giorno servisse a piena larghezza.
- `favicon-*` — il solo cerchio. GRUPPO e *dal 1973* a 16 pixel diventano
  macchie illeggibili. Il cerchio si ricava per geometria: la riga piu' larga e'
  l'equatore, quella larghezza e' il diametro. Non si puo' cercare la banda
  "piu' larga di X", perche' in una circonferenza le righe si stringono proprio
  in cima e in fondo e la soglia mangerebbe le calotte.

Due accorgimenti che sembrano dettagli e non lo sono:

- Sotto i 32 pixel l'alfa viene alzata con una gamma < 1. Il marchio di
  Elettrica Ducale e' disegnato a filo, non pieno: senza quel ritocco alla
  dimensione della linguetta del browser sbiancava fino a sparire.
- L'`apple-touch-icon` ha fondo bianco, perche' iOS non gestisce la trasparenza
  nelle icone della schermata home.

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
- **Risoluzione dei loghi.** Le lockup arrivate sono JPEG: 740x268 px per Ducale
  Impianti, 1401x542 per Elettrica Ducale. Il marchio ritagliato di Ducale
  Impianti resta 179x268 px, appena sufficiente per il riquadro su schermi 2x e
  tirato su schermi 3x. Se si recupera la versione vettoriale (SVG, EPS o PDF)
  vale la pena rigenerare tutto da quella.

## Bozze di sfondo (temporanee)

`bozze/` contiene tre copie della pagina che differiscono solo per il fondo,
usate per far scegliere la variante al cliente:

| Cartella | Variante |
|---|---|
| `bozze/1-aloni/` | Aloni sfumati — è quella attualmente in `card/` |
| `bozze/2-blu/`   | Velatura verticale nel blu del marchio |
| `bozze/3-grana/` | Aloni con grana finissima |

Si rigenerano da `card/index.html` con:

```bash
python3 _source/make-bozze-sfondi.py
```

Quando la variante è scelta, si riporta il suo blocco CSS dentro
`card/index.html` e **si cancella la cartella `bozze/`**: non va mai caricata
sull'hosting, come `_source/` e `vercel.json`.
