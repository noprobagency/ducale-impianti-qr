# Landing QR — Gruppo Ducale

Tre pagine statiche sorelle, ognuna raggiunta dal proprio QR code stampato.
Nessuna dipendenza: niente framework, niente build, niente npm. Si aprono anche
con un doppio clic sull'`index.html`.

| Cartella | Chi | Destinazione |
|---|---|---|
| `card/` | Ducale Impianti S.r.l. | `https://www.ducaleimpianti.com/card/` |
| `elettrica/` | Elettrica Ducale S.r.l. | `https://www.elettricaducale.it/card/` |
| `officina/` | Officina di carpenteria leggera | `https://www.elettricaducale.it/officina/` |

Ducale Impianti ed Elettrica Ducale hanno siti distinti, quindi ogni pagina va
sul dominio della propria azienda. L'officina e' un reparto di Elettrica Ducale
— stessa societa', stessa partita IVA — e sta quindi sul suo dominio, in una
cartella a parte.

In anteprima le tre convivono sullo stesso indirizzo solo perche' e' un unico
deploy Vercel. Non e' come saranno in produzione.

## Le pagine derivate non si modificano a mano

`card/index.html` e' l'unica sorgente. Le altre due si generano da quella, cosi'
non divergono a ogni giro di correzioni:

```bash
python3 _source/make-pagine.py              # elettrica + officina
python3 _source/make-pagine.py officina     # una sola
```

Tutto cio' che distingue le tre pagine — dati, colori, uffici, sedi, recapiti —
sta in `_source/make-pagine.py`. Lo script si ferma con un errore se un testo
che deve sostituire non esiste piu': se hai cambiato `card/index.html` in un
punto che lo riguarda te ne accorgi subito, invece di ritrovarti dati vecchi
nelle pagine sorelle.

**Quindi: si modifica `card/index.html`, poi si rigenera.** Una modifica fatta
a mano dentro `elettrica/` o `officina/` viene persa alla prima rigenerazione.

## Cosa caricare

Va online **solo il contenuto della cartella** (`card/`, `elettrica/` oppure
`officina/`):

```
card/
├── index.html
└── img/
    ├── logo-lockup.png     ← il marchio in testata
    ├── logo.png            ← solo marchio, di scorta
    ├── favicon.ico
    ├── favicon-16.png
    ├── favicon-32.png
    ├── favicon-192.png
    └── apple-touch-icon.png
```

Ogni cartella ha il proprio `img/`, con logo e favicon della sua azienda.

`_source/` resta in locale e non va mai caricata sull'hosting: contiene i loghi
sorgente e gli script. Nemmeno `vercel.json` va caricato: serve solo
all'anteprima.

## Destinazione sull'hosting

Copiare il contenuto della cartella in `/public_html/<nome-cartella>/`, sulla
radice del sito WordPress corrispondente.

### Perche' funziona senza toccare WordPress

L'`.htaccess` standard di WordPress contiene:

```apache
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
```

cioe' WordPress non intercetta i file e le cartelle che esistono davvero su
disco. Una cartella statica dentro `public_html` viene quindi servita
direttamente da Apache, senza passare dal CMS.

## Avvertenze

1. **Non creare in WordPress pagine con slug `card` o `officina`.** Manderebbe
   in conflitto le due cose e vincerebbe WordPress. Verificato il 14 agosto
   2026: `https://www.ducaleimpianti.com/card/` rispondeva 404, quindi lo slug
   era libero. Da riverificare su `elettricaducale.it` prima di caricare.
2. **Plugin di sicurezza** (Wordfence, iThemes Security, Sucuri) a volte
   bloccano l'esecuzione in cartelle fuori standard. Se l'indirizzo risponde
   403, la causa e' quasi sempre li'.
3. **Cache e Cloudflare.** Una cartella statica non viene toccata dai plugin di
   cache, ma se dopo un aggiornamento vedi ancora la versione vecchia, svuota
   comunque la cache del plugin e quella di Cloudflare.
4. **Permessi:** cartelle `755`, file `644`.
5. **HTTPS e www.** L'indirizzo nel QR deve corrispondere esattamente alla forma
   canonica del sito, per non aggiungere un redirect prima di mostrare la
   pagina. Verificato: su `ducaleimpianti.com` tutte le varianti rispondono
   `301` verso `https://www.ducaleimpianti.com/`, quindi la forma canonica e'
   **con `www` e in `https`**. Su `elettricaducale.it` vale lo stesso.

## Rigenerare logo e favicon

Serve Pillow (`pip install pillow`, oppure
`pip install pillow --break-system-packages` se il sistema lo richiede).
Dalla radice del progetto:

```bash
python3 _source/make-favicons.py            # tutte e tre
python3 _source/make-favicons.py officina   # una sola
```

Parte dalle lockup in `_source/`, che sono immagini su fondo bianco: lo sfondo
viene scontornato ricavando l'alfa, poi si ritagliano tre pezzi diversi perche'
servono a cose diverse.

- `logo-lockup.png` — la lockup intera, marchio piu' scritta: e' quella che sta
  in testata. Oltre i 960 px viene ridotta, perche' in pagina occupa 300 px.
- `logo.png` — il solo marchio (GRUPPO + cerchio + *dal 1973*). Il taglio fra
  marchio e scritta viene trovato da solo, cercando il corridoio bianco piu'
  largo. Oggi non e' usato in pagina, resta di scorta.
- `favicon-*` — il solo cerchio. GRUPPO e *dal 1973* a 16 pixel diventano
  macchie illeggibili. Il cerchio si ricava per geometria: la riga piu' larga e'
  l'equatore, quella larghezza e' il diametro. Non si puo' cercare la banda
  "piu' larga di X", perche' in una circonferenza le righe si stringono proprio
  in cima e in fondo e la soglia mangerebbe le calotte.

Tre accorgimenti che sembrano dettagli e non lo sono:

- Sotto i 32 pixel l'alfa viene alzata con una gamma < 1. I marchi di Elettrica
  Ducale e dell'officina sono disegnati a filo, non pieni: senza quel ritocco,
  alla dimensione della linguetta del browser sbiancavano fino a sparire.
- Le immagini grandi passano a tavolozza di 64 colori. Sono marchi a tinte
  piatte, ma il PNG a colore pieno li salva come fotografie: la lockup di
  Elettrica Ducale scendeva da 313 a 39 KB senza differenze visibili.
- L'`apple-touch-icon` ha fondo bianco, perche' iOS non gestisce la trasparenza
  nelle icone della schermata home.

## Il segnaposto della sede operativa

Il link "Apri in mappe" della sede operativa dell'officina non usa l'indirizzo
scritto, ma le coordinate `46.0827983,13.3911910`. Cercando "Via
dell'Artigianato 95" Google agganciava l'azienda accanto e il segnaposto cadeva
sul capannone sbagliato: l'ingresso giusto e' quello di fianco.

Le coordinate vengono da OpenStreetMap, che ha il civico mappato, e sono state
ricontrollate in senso inverso — quel punto risponde "95, Via dell'Artigianato".
Gli altri link mappa restano a ricerca testuale sul civico 69, dove Google
aggancia correttamente le aziende del gruppo.

## Tracciamento delle scansioni

Per distinguere da quale supporto stampato arriva la scansione, si aggiungono i
parametri direttamente nell'indirizzo del QR, uno diverso per ogni supporto:

```
https://www.ducaleimpianti.com/card/?utm_source=qr&utm_medium=print&utm_campaign=biglietti
https://www.ducaleimpianti.com/card/?utm_source=qr&utm_medium=print&utm_campaign=mezzi
https://www.ducaleimpianti.com/card/?utm_source=qr&utm_medium=print&utm_campaign=cantieri
```

La pagina li ignora: servono solo alla statistica lato server o ad Analytics, se
in futuro verra' aggiunto.

Usare un **QR statico, non dinamico**: i generatori dinamici gratuiti scadono e
trasformerebbero il materiale gia' stampato in carta straccia.

## Da completare

- **Risoluzione dei loghi.** Le lockup arrivate sono immagini raster: 740x268 px
  per Ducale Impianti, 1401x542 per Elettrica Ducale, 1204x468 per l'officina.
  Se si recupera la versione vettoriale (SVG, EPS o PDF) vale la pena
  rigenerare tutto da quella.
