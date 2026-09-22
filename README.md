# Landing QR — Gruppo Ducale

Tre pagine statiche sorelle, ognuna raggiunta dal proprio QR code stampato.
Nessuna dipendenza: niente framework, niente build, niente npm. Si aprono anche
con un doppio clic sull'`index.html`.

| Cartella | Chi | Indirizzo nel QR |
|---|---|---|
| `impiantielettrici-qr/` | Ducale Impianti S.r.l. | `https://www.ducaleimpianti.com/impiantielettrici-qr/` |
| `quadri-qr/` | Elettrica Ducale S.r.l. | `https://www.elettricaducale.it/quadri-qr/` |
| `officinacarpenteria-qr/` | Officina di carpenteria leggera | `https://www.elettricaducale.it/officinacarpenteria-qr/` |

**Il nome della cartella e' lo slug in produzione.** Si carica `impiantielettrici-qr/` e
l'indirizzo diventa `.../impiantielettrici-qr/`: nessuna traduzione fra i due, nessuna
occasione di sbagliare in fase di caricamento.

Ducale Impianti ed Elettrica Ducale hanno siti distinti, quindi ogni pagina va
sul dominio della propria azienda. L'officina e' un reparto di Elettrica Ducale
— stessa societa', stessa partita IVA — e sta quindi sul suo dominio, in una
cartella a parte.

In anteprima le tre convivono sullo stesso indirizzo solo perche' e' un unico
deploy Vercel. Non e' come saranno in produzione.

### Perche' questi slug

Il suffisso `-qr` non collide con niente che WordPress possa generare da solo,
e tiene distinte le due pagine che stanno sullo stesso dominio. Non era una
precauzione teorica: `elettricaducale.it/officina/`, il primo candidato per
l'officina, rispondeva gia' 200. Era la *pagina allegato* di una foto caricata
col nome "officina": WordPress ne crea una per ogni immagine, usando il nome del
file come indirizzo. La cartella avrebbe avuto la precedenza, ma se un giorno
fosse stata rimossa i QR stampati avrebbero mostrato una foto invece di un
errore.

Gli slug sono stati scelti dal cliente. I due piu' lunghi portano il QR a
49x49 moduli invece di 45x45: per questo il lato minimo in stampa e' 22 mm e
non 20, cosi' ogni modulo resta sopra 0,45 mm.

Verificato il 18 settembre 2026: tutti e tre rispondono 404, quindi sono liberi.

## Le pagine derivate non si modificano a mano

`impiantielettrici-qr/index.html` e' l'unica sorgente. Le altre due si generano da quella, cosi'
non divergono a ogni giro di correzioni:

```bash
python3 _source/make-pagine.py              # elettrica + officina
python3 _source/make-pagine.py officina     # una sola
```

Tutto cio' che distingue le tre pagine — dati, colori, uffici, sedi, recapiti —
sta in `_source/make-pagine.py`. Lo script si ferma con un errore se un testo
che deve sostituire non esiste piu': se hai cambiato `impiantielettrici-qr/index.html` in un
punto che lo riguarda te ne accorgi subito, invece di ritrovarti dati vecchi
nelle pagine sorelle.

**Quindi: si modifica `impiantielettrici-qr/index.html`, poi si rigenera.** Una modifica
fatta a mano dentro `quadri-qr/` o `officinacarpenteria-qr/` viene persa alla prima
rigenerazione.

## Cosa caricare

Va online **la cartella intera**, con il suo nome: `impiantielettrici-qr/`,
`quadri-qr/` oppure `officinacarpenteria-qr/`.

```
impiantielettrici-qr/
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
sorgente e gli script. Nemmeno `vercel.json` va caricato: serve solo all'anteprima, dove tiene
anche i reindirizzamenti dai vecchi indirizzi (`/card/`, `/elettrica/`,
`/officina/`, e poi `/ducale-qr/`, `/elettrica-qr/`, `/officina-qr/`) a quelli
definitivi, per i link gia' mandati al cliente. Reindirizza anche i vecchi file
QR ai nuovi: chi apre un link di una lista precedente riceve il codice giusto,
non uno che punta a un indirizzo che in produzione non esistera' mai.

## Pacchetti pronti da caricare

`consegna/` contiene un archivio per hosting, gia' con le cartelle giuste dentro:

| Archivio | Va su | Contiene |
|---|---|---|
| `consegna/ducaleimpianti.com.zip` | hosting Aruba di `ducaleimpianti.com` | `impiantielettrici-qr/` |
| `consegna/elettricaducale.it.zip` | hosting di `elettricaducale.it` | `quadri-qr/`, `officinacarpenteria-qr/` |

Si estrae nella radice del sito (vedi sotto). Si rifanno dopo ogni modifica alle pagine:

```bash
rm -f consegna/*.zip
zip -qrX consegna/ducaleimpianti.com.zip impiantielettrici-qr -x '*.DS_Store'
zip -qrX consegna/elettricaducale.it.zip quadri-qr officinacarpenteria-qr -x '*.DS_Store'
```

## Destinazione sull'hosting

Copiare la cartella nella radice del sito WordPress corrispondente, allo
stesso livello di `wp-admin`, `wp-content` e `.htaccess` — accanto a WordPress,
non dentro `wp-content`.

La radice non ha lo stesso nome ovunque. Su molti hosting si chiama
`public_html`; **su Aruba prende il nome del dominio**: nel File Manager e' la
cartella `www.ducaleimpianti.com`, e il risultato deve essere
`www.ducaleimpianti.com/impiantielettrici-qr/index.html`. Le cartelle
`..._Backup_...` che Aruba mostra accanto sono fuori dal sito: li' la pagina
non sarebbe raggiungibile.

- `impiantielettrici-qr/` sull'hosting di `ducaleimpianti.com`
- `quadri-qr/` e `officinacarpenteria-qr/` sull'hosting di `elettricaducale.it`

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

1. **Non creare in WordPress pagine, articoli o immagini con slug
   `impiantielettrici-qr`, `quadri-qr` o `officinacarpenteria-qr`.** Vale anche per le immagini:
   WordPress da' a ogni file caricato un indirizzo col suo nome, ed e' cosi' che
   `/officina/` risultava gia' occupato.
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
   **con `www` e in `https`**. Su `elettricaducale.it` vale lo stesso,
   verificato il 18 settembre 2026. Gli indirizzi nel QR finiscono con la barra:
   senza, Apache aggiungerebbe comunque un reindirizzamento per arrivarci.

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
scritto, ma le coordinate `46.083296,13.390925`. Cercando "Via dell'Artigianato
95" Google agganciava l'azienda accanto e il segnaposto cadeva sul capannone
sbagliato: l'ingresso giusto e' quello di fianco.

Le coordinate sono state indicate dal cliente sul posto. Il civico mappato su
OpenStreetMap cadeva 59 m piu' a sud-est, ancora sull'ingresso sbagliato: qui il
dato catastale non basta, serviva la verifica di chi ci lavora.

Sono scritte per esteso e non come link accorciato `maps.app.goo.gl`, che
dipenderebbe da un servizio esterno capace di smettere di risolvere: un
indirizzo raggiunto da materiale stampato deve reggere negli anni.

Gli altri link mappa restano a ricerca testuale sul civico 69, dove Google
aggancia correttamente le aziende del gruppo.

## QR code

Si generano qui, senza servizi esterni:

```bash
python3 _source/make-qr.py      # serve: pip install segno (verifica: opencv-python-headless)
```

I file finiscono in `qr/`, **cartella per la tipografia: non va caricata
sull'hosting.** Per ogni azienda: SVG, PDF ed EPS vettoriali, piu' un PNG ad
alta risoluzione per chi lo chiede.

| File | Indirizzo codificato |
|---|---|
| `qr/impiantielettrici-qr.*` | `https://www.ducaleimpianti.com/impiantielettrici-qr/?utm_source=biglietto&utm_medium=qr` |
| `qr/quadri-qr.*` | `https://www.elettricaducale.it/quadri-qr/?utm_source=biglietto&utm_medium=qr` |
| `qr/officinacarpenteria-qr.*` | `https://www.elettricaducale.it/officinacarpenteria-qr/?utm_source=biglietto&utm_medium=qr` |

Scelte, tutte deliberate perche' un QR stampato non si corregge piu':

- **QR statico.** Dentro c'e' direttamente l'indirizzo della pagina. I
  generatori online creano quasi sempre QR *dinamici*, che passano da un loro
  link di rimbalzo: quando l'abbonamento scade o il servizio chiude, tutto il
  materiale stampato smette di funzionare.
- **Correzione d'errore M.** Il biglietto e' carta piatta e pulita. Il codice
  viene 49x49 moduli per Ducale Impianti e per l'officina, 45x45 per Elettrica
  Ducale, che ha l'indirizzo piu' corto; con Q salirebbe fino a 57x57, piu'
  fitto a parita' di misura.
- **Lato minimo in stampa: 22 mm**, margine bianco compreso: sono 0,45 mm per
  modulo nel caso piu' fitto, comodi per qualsiasi telefono. Il margine bianco attorno fa parte del
  codice e non va tagliato: senza, molti telefoni non lo agganciano.
- **Nero pieno su bianco.** Niente colori ne' logo al centro.
- **Verifica automatica.** Lo script rilegge ogni PNG con due lettori
  indipendenti a sei misure diverse, e si ferma se anche una sola lettura
  restituisce un indirizzo diverso da quello voluto.

**In tipografia solo dopo che le tre pagine rispondono sui domini veri**, e dopo
aver scansionato ciascun codice da un telefono atterrando sulla pagina giusta.

### Verifica completa

```bash
python3 _source/verifica.py
```

Non si fida degli script che generano: ha la sua lista di cosa deve essere vero
e controlla tutto contro quella. Per ogni QR decodifica PDF, SVG, EPS e PNG con
due lettori a cinque misure, confronta il disegno modulo per modulo con quello
atteso e simula la foto da telefono di un biglietto stampato a 22 mm. Poi apre
l'indirizzo del QR in produzione e controlla che risponda al primo colpo, che la
pagina e le immagini siano identiche al byte a quelle del progetto, e che
telefoni, P. IVA, SDI, PEC, uffici, sito, LinkedIn e mappe siano quelli giusti.
Da rilanciare dopo ogni modifica.

### Tracciamento

L'UTM (`utm_source=biglietto`, `utm_medium=qr`) e' nel codice fin da ora perche'
dopo la stampa non si aggiunge piu'. Da solo pero' non conta niente: e'
un'etichetta, e oggi le tre pagine non hanno nessuno strumento che la legga.
Si puo' aggiungere in qualsiasi momento, anche a biglietti gia' stampati: le
scansioni arriveranno con l'etichetta giusta.

Se in futuro servissero supporti diversi (furgoni, cartelli di cantiere) si fa
un QR a parte con la sua sorgente, per esempio `utm_source=furgone`, e con
correzione d'errore Q, adatta a superfici esposte.

## Da completare

- **Risoluzione dei loghi.** Le lockup arrivate sono immagini raster: 740x268 px
  per Ducale Impianti, 1401x542 per Elettrica Ducale, 1204x468 per l'officina.
  Se si recupera la versione vettoriale (SVG, EPS o PDF) vale la pena
  rigenerare tutto da quella.
