# ESC Router – registrácia vysokých škôl

Jednoduchá appka v Streamlite pre slovenské vysoké školy:

- **návod** na registráciu do ESC Routra (viditeľný bez prihlásenia),
- **hlásenie stavu** – škola sa prihlási svojím kódom a odškrtne hotové kroky,
- **prehľad pre správcu** – štatistika, tabuľka škôl, export do Excelu, správa prístupových kódov.

Údaje sa ukladajú do Google Sheets.

## Súbory

| Súbor | Na čo slúži |
|---|---|
| `app.py` | Logika appky (prihlásenie, formulár školy, prehľad správcu). |
| `obsah.py` | Texty návodu. Úpravy obsahu robte tu. |
| `uloziste.py` | Zápis a čítanie z Google Sheets, prípadne z lokálnych súborov. |
| `skoly.csv` | Počiatočný zoznam škôl. Použije sa len pri prvom spustení. |
| `.streamlit/secrets.toml.example` | Vzor tajných nastavení. |

## 1. Vyskúšanie na vlastnom počítači

```
pip install -r requirements.txt
streamlit run app.py
```

Bez nastavených secrets beží appka v **skúšobnom režime**: údaje ukladá do priečinka `data/` a heslo správcu je `demo`.
Prihláste sa ako správca (ľavý panel), vygenerujte kódy a jedným z nich sa prihláste ako škola.

## 2. Zoznam škôl

`skoly.csv` obsahuje 33 slovenských vysokých škôl podľa Portálu VŠ (stav k 17. 11. 2026): 20 verejných, 3 štátne
a 10 súkromných. **Zahraničné vysoké školy pôsobiace na Slovensku v ňom nie sú** – ak sa ich povinnosť týka, doplňte ich.

| Stĺpec | Obsah | Zdroj |
|---|---|---|
| `skola_id` | Krátky jedinečný kód bez medzier a diakritiky. Po spustení ho už nemeňte. | interný |
| `nazov` | Aktuálny oficiálny názov školy. Zobrazuje sa školám aj v prehľade. | [Portál VŠ](https://www.portalvs.sk/sk/informacie-o-vysokych-skolach) |
| `typ` | verejná / štátna / súkromná | Portál VŠ |
| `pic` | PIC kód školy | zoznam držiteľov ECHE (EK, 24. 9. 2026) |
| `erasmus_kod` | Erasmus kód, napr. `SK BRATISL02` | zoznam držiteľov ECHE (EK, 24. 9. 2026) |

Názov sa vždy berie z registra VŠ, nie zo zoznamu ECHE. V zozname ECHE majú niektoré školy starý názov
(napr. DTI, VŠEM, VŠTE v Prešove), PIC a Erasmus kód sa však nemenia.

Na čo si dať pozor:

- **Vysoká škola Danubius** a **VŠ zdravotníctva a sociálnej práce sv. Alžbety** v zozname ECHE nie sú, PIC a Erasmus kód sú prázdne.
- **VŠ bezpečnostného manažérstva v Košiciach** má v zozname ECHE dva záznamy: `SK KOSICE04` (n. o., PIC 997863154)
  a novší `SK KOSICE05` (s. r. o., PIC 895681705). Použitý je novší – overte to so školou.

Po prvom spustení sa zoznam skopíruje do hárku `skoly` a ďalej sa spravuje tam. Ak v hárku chýba PIC alebo Erasmus kód
a v `skoly.csv` je vyplnený, appka ho pri spustení doplní. Vyplnené bunky ani názvy škôl neprepisuje.

## 3. Google Sheets

1. V [Google Cloud Console](https://console.cloud.google.com/) vytvorte projekt.
2. V časti *APIs & Services → Library* zapnite **Google Sheets API** a **Google Drive API**.
3. V časti *IAM & Admin → Service Accounts* vytvorte servisný účet. Rolu v projekte nepotrebuje.
4. Pri servisnom účte vytvorte kľúč typu **JSON** (*Keys → Add key*). Súbor si bezpečne uložte.
5. Vytvorte prázdnu tabuľku v Google Sheets. Hárky `skoly` a `stav` si appka vytvorí sama.
6. Tabuľku zdieľajte s e-mailom servisného účtu (`…@….iam.gserviceaccount.com`) s právom **Editor**.
   Nikomu ďalšiemu ju nezdieľajte – obsahuje prístupové kódy škôl.
7. Z adresy tabuľky si skopírujte jej ID (časť medzi `/d/` a `/edit`).

## 4. Tajné nastavenia (secrets)

Podľa vzoru `.streamlit/secrets.toml.example` pripravte tri veci:

- `admin_heslo` – dlhé heslo správcu,
- `sheet_id` – ID tabuľky,
- `[gcp_service_account]` – hodnoty z JSON kľúča.

Lokálne ich uložte do `.streamlit/secrets.toml`. Tento súbor ani JSON kľúč **nikdy nenahrávajte na GitHub**
(`.gitignore` ich vynecháva).

## 5. Nasadenie na Streamlit Community Cloud

1. Nahrajte priečinok do repozitára na GitHube (môže byť súkromný).
2. Na [share.streamlit.io](https://share.streamlit.io/) zvoľte *Create app*, vyberte repozitár a súbor `app.py`.
3. V *Advanced settings → Secrets* vložte obsah svojho `secrets.toml`.
4. Po nasadení otvorte appku. Žltý pruh „Skúšobný režim“ sa nesmie zobraziť – ak áno, secrets nie sú načítané.

## 6. Prvé spustenie

1. Prihláste sa ako správca (ľavý panel → *Správca*).
2. Skontrolujte, že prehľad ukazuje všetky školy.
3. Kliknite na **Vygenerovať chýbajúce kódy**.
4. Zapnite *Zobraziť kódy* a stiahnite si CSV. Každej škole pošlite jej kód spolu s odkazom na appku.

## 7. Bežná prevádzka

- **Nová škola:** pridajte riadok do hárku `skoly` a v appke vygenerujte chýbajúci kód.
- **Zmena kódu:** prepíšte alebo vymažte bunku `kod` v hárku `skoly` (po vymazaní vygenerujte nový).
- **Oprava stavu školy:** upravte riadok v hárku `stav`. Stĺpce `k1` až `k6` obsahujú dátum splnenia kroku
  (`RRRR-MM-DD`), prázdna bunka znamená nesplnené.
- **Úprava návodu:** zmeňte texty v `obsah.py` a nahrajte zmenu na GitHub. Appka sa nasadí sama.
- Zmeny v tabuľke sa v appke prejavia do minúty alebo po kliknutí na *Načítať znova*.
- Názvy stĺpcov v prvom riadku hárkov nemeňte.

## Bezpečnosť a obmedzenia

- Prístupový kód je jednoduchá ochrana vhodná pre údaj „v akom kroku registrácie škola je“.
  Appka nie je určená na osobné údaje študentov ani iné citlivé údaje.
- Kto pozná kód školy, môže zmeniť jej stav. Kód posielajte len kontaktnej osobe školy.
- Počet neúspešných prihlásení je obmedzený len v rámci jednej návštevy. Kódy preto nechajte v dĺžke,
  akú generuje appka.
- Bezplatná appka po dlhšej nečinnosti zaspí a prvé načítanie potom trvá dlhšie.
- Google Sheets API má limit počtu požiadaviek za minútu. Pri desiatkach škôl je to bez problémov.
