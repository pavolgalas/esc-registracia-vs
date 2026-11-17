"""Texty návodu. Úpravy obsahu robte tu – logika appky je v app.py."""

AKTUALIZOVANE = "16. 11. 2026"

UVOD = (
    "Registrácia do ESC Routra je prvý krok k tomu, aby vaša vysoká škola mohla vydávať "
    "preukazy študenta s prvkami európskeho študentského preukazu (European Student Card, ESC)."
)

V_SKRATKE = """
- Registruje sa **vysoká škola sama**, aj keď bude ESC za ňu vydávať dodávateľ preukazov.
- Registráciu robí **oprávnený zástupca**. Nemusí to byť štatutár.
- Potrebujete **PIC kód** školy a osobný účet **EU Login** alebo **MyAcademicID**.
- Registráciu overuje helpdesk ESC. Ďalších používateľov a dodávateľa pridáte až po aktivácii účtu.
"""

# id kroku = názov stĺpca v hárku `stav`
KROKY = [
    {
        "id": "k1",
        "nazov": "Určte oprávneného zástupcu",
        "text": "Vyberte osobu, ktorá môže oficiálne konať v mene školy a prijať právne dokumenty k ESC Routru.",
        "detail": """
**Nemusí to byť štatutár.** Podmienky ESC hovoria o „zákonnom alebo oprávnenom zástupcovi“ a spôsob
určenia nechávajú na pravidlá každej školy. Môže to byť rektor alebo ním poverená osoba, napr. prorektor,
kvestor, vedúci zahraničného oddelenia alebo CIT.

Registrujúca osoba musí mať oprávnenie školu zaviazať. Prevádzkovateľ Routra si ho môže overiť,
preto odporúčame mať poverenie písomne.

Pri prvej registrácii prijíma právne dokumenty len tento jeden používateľ. Ďalších kolegov pridá až po aktivácii účtu.
""",
    },
    {
        "id": "k2",
        "nazov": "Prihláste sa do ESC Routra",
        "text": "Oprávnený zástupca sa prihlási na [router.europeanstudentcard.eu](https://router.europeanstudentcard.eu/) cez EU Login alebo MyAcademicID.",
        "detail": """
- **Nemusí ísť o účet, ktorým bola škola pôvodne registrovaná v systémoch Európskej komisie.**
  Stačí osobný účet oprávneného zástupcu. Ak ho nemá, vytvorí si nový.
- **EU Login** je prihlasovacia služba Európskej komisie. Účet je viazaný na osobu a jej e-mail, nie na školu.
- **MyAcademicID** umožňuje prihlásiť sa účtom vašej školy, ak je škola zapojená do federácie eduGAIN.
- V registračnom formulári uveďte **ten istý e-mail**, aký má účet, ktorým sa prihlasujete.
  Použite pracovný e-mail na doméne školy.
""",
    },
    {
        "id": "k3",
        "nazov": "Vyplňte registračný formulár",
        "text": "Formulárom žiadate o prístup školy do ESC Routra.",
        "detail": """
| Údaj | Čo uviesť |
|---|---|
| Typ organizácie | Vysoká škola (higher education institution) |
| Identifikátor | PIC kód školy |
| Krajina, mesto | Slovensko, sídlo školy |
| Oprávnený zástupca | Meno, priezvisko a e-mail |

PIC (Participant Identification Code) je deväťmiestny kód z portálu EU Funding & Tenders.
Škola ho používa v projektoch Erasmus+, pozná ho vaše zahraničné oddelenie.
Po prihlásení do tejto appky vidíte PIC svojej školy hore pod jej názvom.
""",
    },
    {
        "id": "k4",
        "nazov": "Prijmite právne dokumenty",
        "text": "Oprávnený zástupca si prečíta a prijme tri dokumenty.",
        "detail": """
- **Terms & Conditions** – pravidlá používania Routra a vydávania ESC.
- **Privacy Statement** – aké osobné údaje sa v Routri spracúvajú a aké práva majú dotknuté osoby.
- **Joint Controllership Arrangement (JCA)** – rozdelenie zodpovednosti za ochranu údajov medzi Európsku komisiu a školu.

Odporúčame dať dokumenty vopred prečítať zodpovednej osobe za ochranu osobných údajov.
Ak ich škola neprijme do troch mesiacov od registrácie, účet môže zaniknúť.
""",
    },
    {
        "id": "k5",
        "nazov": "Účet školy je aktívny",
        "text": "Helpdesk ESC skontroloval údaje, nastavil škole stav „Active“ a oprávnený zástupca dostal potvrdzujúci e-mail.",
        "detail": """
Helpdesk si môže vyžiadať doplnenie údajov. Sledujte e-mail uvedený vo formulári vrátane priečinka so spamom.
Tento krok odškrtnite až po doručení potvrdenia.
""",
    },
    {
        "id": "k6",
        "nazov": "Pridajte ďalších používateľov",
        "text": "Po aktivácii pridajte kolegov, najmä technického administrátora, aby prístup nezávisel od jednej osoby.",
        "detail": """
Len používateľ s rolou technického administrátora môže vygenerovať API token.
Ďalší postup závisí od toho, kto bude za školu vydávať ESC – pozrite si kartu „Po registrácii“.
""",
    },
]

# ---------- predošlá registrácia v ESC Routri ----------

PREVERENIE = {
    "": "Zatiaľ nepreverené",
    "mame_pristup": "Účet sme našli a máme k nemu prístup",
    "bez_pristupu": "Účet existuje, ale nevieme, kto ho spravuje",
    "nenasli": "Interne sme o účte nič nezistili",
}

PREDOSLA_REG_NADPIS = "Vaša škola už pravdepodobne má účet v ESC Routri"

PREDOSLA_REG_TEXT = """
Podľa informácií od tímu ESC Európskej komisie je v ESC Routri zaregistrovaná organizácia
**„{nazov}“**. Registrácia mohla vzniknúť skôr a súčasní kolegovia o nej nemusia vedieť.
Skôr než začnete novú registráciu, preverte, či a kto má k tomuto účtu prístup.
"""

PREDOSLA_REG_DOPLNOK = {
    "umb": (
        "**Pozor:** registrácia je vedená na úrovni **Ekonomickej fakulty**. Overte, či môže slúžiť "
        "celej univerzite, alebo treba riešiť registráciu za UMB ako celok. Túto otázku odporúčame "
        "konzultovať s národnou agentúrou."
    ),
}

PREDOSLA_REG_POSTUP = """
**Ako postupovať**

1. **Preverte interne,** kto mohol školu registrovať: zahraničné oddelenie (Erasmus+), CIT alebo správa
   informačných systémov, pracovisko vydávajúce preukazy študenta (aj ISIC), prípadne vedenie školy alebo fakulty.
   Hľadajte aj e-maily od ESC Routra alebo helpdesku ESC.
2. **Ak účet nájdete a máte k nemu prístup,** skontrolujte zoznam používateľov a oprávneného zástupcu.
   Ak sa zmenil, aktualizujte ho. Kroky 1 až 5 potom môžete odškrtnúť a pokračujete krokom 6.
3. **Ak účet existuje, ale nikto z vás k nemu nemá prístup,** alebo ste interne nič nezistili,
   **nezakladajte zatiaľ nový účet.** Napíšte národnej agentúre. V spolupráci s tímom ESC
   zistíme, komu je účet pridelený, a ako ho prevziať. Novú registráciu odporúčame začať,
   až keď sa potvrdí, že pôvodný účet už neexistuje.
"""

PREDOSLA_REG_VYRIESENA = (
    "Predošlú registráciu v ESC Routri ste preverili a máte k účtu prístup. "
    "Pokračujte krokmi, ktoré ešte nemáte hotové."
)

SPOSOB_POMOC = (
    "Ide len o vydávanie ESC: zápis kariet do ESC Routra a doplnenie ESC loga s QR kódom na preukaz. "
    "Nezáleží na tom, kto preukazy fyzicky vyrába. Ak to za školu bude robiť dodávateľ, "
    "musí mať v ESC Routri vlastný účet a škola ho musí pridať vo svojom účte."
)

SPOSOBY = {
    "": "Zatiaľ nerozhodnuté",
    "vlastna": "Škola sama",
    "dodavatel": "Dodávateľ v mene školy",
}

PO_REGISTRACII_VLASTNA = """
1. **Pridajte technického administrátora.** Len on môže vygenerovať API token.
2. **Vyberte spôsob vydávania ESC.** API sa odporúča stredným a veľkým školám, import CSV menším školám,
   webové rozhranie slúži najmä na testovanie.
3. **Vyskúšajte si postup v testovacom prostredí** (sandbox). Nenahrávajte doň skutočné osobné údaje.
4. **Pripravte identifikátory.** Každému študentovi prideľte ESI (európsky identifikátor študenta) a každej karte ESCN (číslo karty).
5. **Upravte dizajn preukazu.** Doplňte ESC logo s QR kódom podľa grafického manuálu.
"""

PO_REGISTRACII_DODAVATEL = """
1. **Dodávateľ potrebuje v Routri vlastný účet** typu „third-party processor“. Registruje sa s identifikačným číslom pre DPH, nie s PIC.
2. **Škola pridá dodávateľa vo svojom účte.** Bez tohto prepojenia dodávateľ nemôže karty vydávať ani spravovať.
3. **Oprávnený zástupca školy prijme aktualizovanú dohodu JCA** s údajmi dodávateľa. Dodávateľ sám dohodu JCA neprijíma.
4. **Uzavrite s dodávateľom zmluvu o spracúvaní osobných údajov.**
5. **Určite pravidlo pre ESI.** Za identifikátor študenta zodpovedá škola, aj keď ho technicky nahráva dodávateľ.

Registráciu školy dodávateľ urobiť nemôže. Kroky 1 až 5 registrácie musí vždy vykonať škola.
"""

NA_PREUKAZE = """
**Na preukaze:** ESC logo, ktoré tvorí QR kód, vlajka EÚ a text „European Student Card“.
QR kód má mať aspoň 15 × 15 mm. Proporcie loga sa nesmú meniť.

**Do Routra:** ESI, ESCN, PIC školy, meno a e-mail držiteľa, dátum platnosti karty, stupeň štúdia a typ karty.

ESI sa na preukaz netlačí. Preukazy vydané od 1. 1. 2028 musia mať nové ESC logo, hologram už nie je potrebný.
"""

WEBINAR = """
**10. december 2026 · online.** Tím ESC predstaví európsky študentský preukaz, naživo ukáže vydávanie kariet
v ESC Routri a odpovie na otázky.

[Čas a registrácia na stránke Európskej komisie](https://erasmus-plus.ec.europa.eu/european-student-card-initiative/events/european-student-card-training-webinars)
"""

ODKAZY = [
    ("ESC Router", "https://router.europeanstudentcard.eu/", "Prihlásenie a registrácia školy."),
    ("Ako začať s ESC", "https://erasmus-plus.ec.europa.eu/european-student-card-initiative/card/get-started", "Oficiálny postup registrácie a videonávod (v angličtine)."),
    ("Podmienky používania ESC", "https://erasmus-plus.ec.europa.eu/european-student-card-initiative/card/how-to-join/terms-conditions", "Kto môže školu registrovať a aké má povinnosti."),
    ("Všeobecné špecifikácie ESC (PDF)", "https://ec.europa.eu/assets/eac/erasmus-plus/student-card/esc-general-specs-05122025.pdf", "Čo je ESC, registrácia, vydávanie a správa kariet."),
    ("Technické špecifikácie ESC (PDF)", "https://ec.europa.eu/assets/eac/erasmus-plus/student-card/esc-technical-specs-05122025.pdf", "API, import CSV, ESI, ESCN, QR kód, sandbox."),
    ("Grafický manuál ESC loga (PDF)", "https://ec.europa.eu/assets/eac/erasmus-plus/student-card/esc-graphic-charter_v4-apr26.pdf", "Ako umiestniť ESC logo na existujúci preukaz."),
    ("Helpdesk ESC", "https://esci-sd.atlassian.net/servicedesk/customer/portals", "Technické otázky a problémy s registráciou."),
]

OTAZKY = [
    ("Je ESC nový preukaz?", "Nie. Ide o váš súčasný preukaz študenta doplnený o spoločné európske prvky. Môže byť plastový aj digitálny a nezáleží na použitej technológii."),
    ("Musí registráciu urobiť rektor osobne?", "Nie. Stačí osoba, ktorú škola podľa svojich pravidiel poverí konať v jej mene. Poverenie odporúčame mať písomne."),
    ("Potrebujeme účet, ktorým bola škola registrovaná v systémoch Európskej komisie?", "Nie. Stačí osobný účet EU Login alebo MyAcademicID oprávneného zástupcu. Ak ho nemá, vytvorí si nový."),
    ("Môže registráciu za školu urobiť dodávateľ preukazov?", "Nie. Škola sa registruje sama a právne dokumenty prijíma jej oprávnený zástupca. Dodávateľa škola pridá až po aktivácii svojho účtu."),
    ("Kto prideľuje ESI?", "Škola. Odporúčame používať rovnaký identifikátor ako v Erasmus Without Paper a pri prihlasovaní cez MyAcademicID."),
    ("Ako sa ESC overuje?", "Naskenovaním QR kódu bežným smartfónom. Zobrazí sa stránka Routra s informáciou, či je karta platná."),
    ("Čo ak už naša škola v ESC Routri účet má?", "Nezakladajte nový. Preverte interne, kto účet spravuje (zahraničné oddelenie, CIT, pracovisko preukazov). Ak to nezistíte, obráťte sa na národnú agentúru – pomôžeme vám v spolupráci s tímom ESC účet prevziať."),
    ("Čo ak sa účet dlho nepoužíva?", "Účet, ku ktorému nebola 12 mesiacov priradená žiadna karta, sa odstráni. Registráciu načasujte tak, aby na ňu nadviazalo vydávanie preukazov."),
]

KONTAKT = "Národná agentúra SAAIC, Digital Contact Point pre program Erasmus+."
