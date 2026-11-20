"""ESC Router – registrácia vysokých škôl: návod, hlásenie stavu a prehľad pre správcu.

Spustenie:  streamlit run app.py
Bez nastavených secrets beží appka v skúšobnom režime (údaje v priečinku data/, heslo správcu „demo“).
"""
from __future__ import annotations

import hmac
import importlib
import io
import secrets as pysecrets
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

import obsah
import uloziste

# Streamlit Cloud po aktualizácii z GitHubu spustí nový app.py, ale pomocné moduly
# môže mať v pamäti zo staršej verzie. Obnovíme ich pri každom spustení skriptu.
importlib.reload(obsah)
importlib.reload(uloziste)
from uloziste import SKOLY, SKOLY_COLS, STAV, STAV_COLS, LocalStore, SheetsStore  # noqa: E402

ROOT = Path(__file__).parent
TZ = ZoneInfo("Europe/Bratislava")
KROK_IDS = [k["id"] for k in obsah.KROKY]
MAX_POKUSOV = 5
MAX_POZNAMKA = 500
ZNAKY_KODU = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # bez zameniteľných znakov (0/O, 1/I)

st.set_page_config(page_title="ESC Router – registrácia VŠ", page_icon="🎓", layout="centered")


# ---------- nastavenia a úložisko ----------

def secret(name: str, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return default


@st.cache_resource(show_spinner="Pripájam úložisko…")
def get_store():
    sa, sheet_id = secret("gcp_service_account"), secret("sheet_id")
    if sa and sheet_id:
        return SheetsStore(sa, sheet_id)
    return LocalStore(ROOT / "data")


DEMO = type(get_store()).__name__ == LocalStore.__name__  # po reloade modulu nefunguje isinstance
ADMIN_HESLO = secret("admin_heslo") or ("demo" if DEMO else None)


@st.cache_data(ttl=60, show_spinner=False)
def nacitaj_skoly() -> pd.DataFrame:
    return get_store().read(SKOLY, SKOLY_COLS)


@st.cache_data(ttl=30, show_spinner=False)
def nacitaj_stav() -> pd.DataFrame:
    return get_store().read(STAV, STAV_COLS)


def obnov():
    nacitaj_skoly.clear()
    nacitaj_stav.clear()


def prvy_import():
    """Ak je hárok `skoly` prázdny, naplní ho zo súboru skoly.csv."""
    if not nacitaj_skoly().empty:
        return
    seed = pd.read_csv(ROOT / "skoly.csv", dtype=str, keep_default_na=False)
    seed["kod"] = ""
    get_store().replace(SKOLY, SKOLY_COLS, seed)
    obnov()


def doplnenie_kodov():
    """Doplní chýbajúce PIC, Erasmus kódy a údaj o predošlej registrácii zo skoly.csv do hárku `skoly`.

    Prepisuje len prázdne bunky, takže úpravy urobené priamo v tabuľke ostanú zachované.
    Názov školy nemení – ten sa spravuje v tabuľke podľa registra VŠ.
    """
    skoly = nacitaj_skoly()
    seed = pd.read_csv(ROOT / "skoly.csv", dtype=str, keep_default_na=False).set_index("skola_id")
    zmena = False
    for col in ("pic", "erasmus_kod", "predosla_reg"):
        for i, sid in skoly["skola_id"].items():
            if not skoly.at[i, col] and sid in seed.index and seed.at[sid, col]:
                skoly.at[i, col] = seed.at[sid, col]
                zmena = True
    if zmena:
        get_store().replace(SKOLY, SKOLY_COLS, skoly)
        obnov()


# ---------- pomocné funkcie ----------

def teraz() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M")


def dnes() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d")


def sk_datum(iso: str) -> str:
    try:
        return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%-d. %-m. %Y")
    except ValueError:
        return iso


def novy_kod() -> str:
    raw = "".join(pysecrets.choice(ZNAKY_KODU) for _ in range(8))
    return f"{raw[:4]}-{raw[4:]}"


def norm_kod(kod: str) -> str:
    return kod.strip().upper().replace(" ", "")


def zhoda(a: str, b: str) -> bool:
    return bool(a) and bool(b) and hmac.compare_digest(a.encode(), b.encode())


def bezpecny_text(text: str) -> str:
    """Skráti poznámku a zabráni tomu, aby ju Excel vyhodnotil ako vzorec."""
    text = " ".join(text.split())[:MAX_POZNAMKA]
    return "'" + text if text[:1] in "=+-@" else text


def stav_skoly(skola_id: str) -> dict:
    df = nacitaj_stav()
    hit = df[df["skola_id"] == skola_id]
    return hit.iloc[0].to_dict() if not hit.empty else {c: "" for c in STAV_COLS}


def aktualny_krok(row) -> str:
    for k in obsah.KROKY:
        if not row[k["id"]]:
            return k["nazov"]
    return "Registrácia dokončená"


# ---------- návod ----------

def zobraz_navod(stav: dict | None = None):
    karty = st.tabs(["Postup registrácie", "Po registrácii", "Dokumenty a webinár", "Časté otázky"])
    with karty[0]:
        st.markdown(obsah.V_SKRATKE)
        for i, k in enumerate(obsah.KROKY, start=1):
            hotovo = bool(stav and stav.get(k["id"]))
            znacka = "✅ " if hotovo else ""
            st.markdown(f"**{znacka}{i}. {k['nazov']}**  \n{k['text']}")
            with st.expander("Podrobnosti"):
                st.markdown(k["detail"])
    with karty[1]:
        st.info(obsah.PO_REGISTRACII_UVOD)
        st.subheader("ESC vydáva škola sama")
        st.markdown(obsah.PO_REGISTRACII_VLASTNA)
        st.subheader("ESC vydáva dodávateľ v mene školy")
        st.markdown(obsah.PO_REGISTRACII_DODAVATEL)
        with st.expander("Čo musí byť na preukaze a čo sa posiela do Routra"):
            st.markdown(obsah.NA_PREUKAZE)
    with karty[2]:
        st.subheader("Webinár Európskej komisie")
        st.markdown(obsah.WEBINAR)
        st.subheader("Dokumenty a odkazy")
        for nazov, url, popis in obsah.ODKAZY:
            st.markdown(f"[{nazov}]({url})  \n{popis}")
    with karty[3]:
        for otazka, odpoved in obsah.OTAZKY:
            with st.expander(otazka):
                st.write(odpoved)
    st.caption(f"Návod aktualizovaný {obsah.AKTUALIZOVANE}. {obsah.KONTAKT}")


# ---------- prihlásenie ----------

def prihlasenie_skoly():
    skoly = nacitaj_skoly()
    with st.form("login_skola"):
        st.subheader("Prihlásenie vysokej školy")
        nazvy = dict(zip(skoly["skola_id"], skoly["nazov"]))
        skola_id = st.selectbox(
            "Vysoká škola", options=list(nazvy), format_func=nazvy.get, index=None,
            placeholder="Vyberte školu",
        )
        kod = st.text_input("Prístupový kód", type="password", help="Kód ste dostali e-mailom od národnej agentúry.")
        odoslat = st.form_submit_button("Prihlásiť sa", type="primary")
    if not odoslat:
        return
    if st.session_state.get("pokusy", 0) >= MAX_POKUSOV:
        st.error("Príliš veľa neúspešných pokusov. Zatvorte kartu prehliadača a skúste to neskôr.")
        return
    ocakavany = ""
    if skola_id:
        ocakavany = norm_kod(skoly.loc[skoly["skola_id"] == skola_id, "kod"].iloc[0])
    if skola_id and zhoda(norm_kod(kod), ocakavany):
        st.session_state["skola_id"] = skola_id
        st.session_state["pokusy"] = 0
        st.rerun()
    st.session_state["pokusy"] = st.session_state.get("pokusy", 0) + 1
    st.error("Škola alebo prístupový kód nesedia. Skontrolujte kód z e-mailu.")


def prihlasenie_spravcu():
    with st.sidebar.expander("Správca"):
        if ADMIN_HESLO is None:
            st.caption("Heslo správcu nie je nastavené (secrets: admin_heslo).")
            return
        with st.form("login_admin"):
            heslo = st.text_input("Heslo správcu", type="password")
            if st.form_submit_button("Prihlásiť"):
                if zhoda(heslo, ADMIN_HESLO):
                    st.session_state["admin"] = True
                    st.rerun()
                st.error("Nesprávne heslo.")


# ---------- pohľad školy ----------

def zobraz_predoslu_registraciu(skola, stav: dict):
    vysledok = stav["preverenie"]
    if vysledok == "mame_pristup":
        st.success(obsah.PREDOSLA_REG_VYRIESENA)
        return
    with st.container(border=True):
        st.markdown(f"#### {obsah.PREDOSLA_REG_NADPIS}")
        st.markdown(obsah.PREDOSLA_REG_TEXT.format(nazov=skola["predosla_reg"]))
        if skola["skola_id"] in obsah.PREDOSLA_REG_DOPLNOK:
            st.markdown(obsah.PREDOSLA_REG_DOPLNOK[skola["skola_id"]])
        st.markdown(obsah.PREDOSLA_REG_POSTUP)
        st.caption("Výsledok preverenia zaznačte nižšie vo formulári a uložte.")


def pohlad_skoly(skola_id: str):
    skoly = nacitaj_skoly()
    hit = skoly[skoly["skola_id"] == skola_id]
    if hit.empty:
        st.session_state.pop("skola_id", None)
        st.rerun()
    skola = hit.iloc[0]
    stav = stav_skoly(skola_id)

    st.subheader(skola["nazov"])
    if skola["predosla_reg"]:
        zobraz_predoslu_registraciu(skola, stav)
    if skola["pic"]:
        st.markdown(f"**PIC:** `{skola['pic']}` · **Erasmus kód:** `{skola['erasmus_kod']}`")
        st.caption("PIC uvediete v registračnom formulári ESC Routra (krok 3). Údaje pochádzajú zo zoznamu držiteľov ECHE.")
    else:
        st.info(
            "Vašu školu sme v zozname držiteľov ECHE nenašli, preto tu nemáme jej PIC kód. "
            "PIC nájdete v portáli EU Funding & Tenders, prípadne ho zistíte na zahraničnom oddelení."
        )
    hotove = sum(bool(stav[k]) for k in KROK_IDS)
    st.progress(hotove / len(KROK_IDS), text=f"{hotove} zo {len(KROK_IDS)} krokov hotových")
    if stav["aktualizovane"]:
        st.caption(f"Stav naposledy uložený {stav['aktualizovane']}.")

    with st.form("stav_form"):
        st.markdown("**Odškrtnite kroky, ktoré má vaša škola hotové, a uložte.**")
        volby = {}
        for i, k in enumerate(obsah.KROKY, start=1):
            popis = f"{i}. {k['nazov']}"
            if stav[k["id"]]:
                popis += f" (hotové {sk_datum(stav[k['id']])})"
            volby[k["id"]] = st.checkbox(popis, value=bool(stav[k["id"]]), key=f"cb_{k['id']}")
        preverenie = stav["preverenie"]
        if skola["predosla_reg"]:
            moznosti = list(obsah.PREVERENIE)
            preverenie = st.radio(
                "Výsledok preverenia predošlej registrácie", options=moznosti, format_func=obsah.PREVERENIE.get,
                index=moznosti.index(stav["preverenie"]) if stav["preverenie"] in moznosti else 0,
            )
        sposoby = list(obsah.SPOSOBY)
        sposob = st.radio(
            "Kto bude za školu vydávať ESC?", options=sposoby, format_func=obsah.SPOSOBY.get,
            index=sposoby.index(stav["sposob"]) if stav["sposob"] in sposoby else 0, horizontal=True,
        )
        st.caption(obsah.SPOSOB_POMOC)
        poznamka = st.text_area(
            "Poznámka alebo otázka pre národnú agentúru (nepovinné)",
            value=stav["poznamka"].lstrip("'"), max_chars=MAX_POZNAMKA,
            help="Neuvádzajte osobné údaje študentov ani heslá.",
        )
        ulozit = st.form_submit_button("Uložiť stav", type="primary")

    if ulozit:
        novy = {"skola_id": skola_id, "sposob": sposob, "preverenie": preverenie, "poznamka": bezpecny_text(poznamka), "aktualizovane": teraz()}
        for kid in KROK_IDS:
            novy[kid] = (stav[kid] or dnes()) if volby[kid] else ""
        try:
            get_store().upsert(STAV, STAV_COLS, novy)
        except Exception:
            st.error("Stav sa nepodarilo uložiť. Skúste to o chvíľu znova.")
        else:
            obnov()
            st.session_state["ulozene"] = True
            st.rerun()
    if st.session_state.pop("ulozene", False):
        st.success("Stav je uložený. Ďakujeme.")

    st.divider()
    st.subheader("Návod")
    zobraz_navod(stav)


# ---------- pohľad správcu ----------

def prehlad() -> pd.DataFrame:
    df = nacitaj_skoly()[["skola_id", "nazov", "typ", "pic", "erasmus_kod", "predosla_reg"]].merge(nacitaj_stav(), on="skola_id", how="left").fillna("")
    df["hotove_kroky"] = df[KROK_IDS].apply(lambda r: sum(bool(v) for v in r), axis=1)
    df["aktualny_krok"] = df.apply(aktualny_krok, axis=1)
    df["sposob"] = df["sposob"].map(obsah.SPOSOBY).fillna("")
    df["preverenie"] = df.apply(
        lambda r: obsah.PREVERENIE.get(r["preverenie"], "") if r["predosla_reg"] else "", axis=1
    )
    return df


def pohlad_spravcu():
    st.subheader("Prehľad registrácií")
    st.caption(f"Úložisko: {get_store().nazov}")
    if st.button("Načítať znova"):
        obnov()
        st.rerun()

    df = prehlad()
    n = len(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Školy spolu", n)
    c2.metric("Začali", int((df["hotove_kroky"] > 0).sum()))
    c3.metric("Účet aktívny", int((df["k5"] != "").sum()))
    c4.metric("Dokončené", int((df["hotove_kroky"] == len(KROK_IDS)).sum()))

    st.markdown("**Počet škôl podľa počtu hotových krokov**")
    rozdelenie = df["hotove_kroky"].value_counts().reindex(range(len(KROK_IDS) + 1), fill_value=0)
    rozdelenie.index = [f"{i} krok" if i == 1 else f"{i} kroky" if i in (2, 3, 4) else f"{i} krokov" for i in rozdelenie.index]
    st.bar_chart(rozdelenie, x_label="Hotové kroky", y_label="Počet škôl")

    f1, f2 = st.columns(2)
    typy = f1.multiselect("Typ školy", sorted(t for t in df["typ"].unique() if t))
    faza = f2.selectbox("Stav", ["Všetky", "Nezačali", "Rozpracované", "Dokončené", "S poznámkou", "S predošlou registráciou"])
    v = df.copy()
    if typy:
        v = v[v["typ"].isin(typy)]
    if faza == "Nezačali":
        v = v[v["hotove_kroky"] == 0]
    elif faza == "Rozpracované":
        v = v[(v["hotove_kroky"] > 0) & (v["hotove_kroky"] < len(KROK_IDS))]
    elif faza == "Dokončené":
        v = v[v["hotove_kroky"] == len(KROK_IDS)]
    elif faza == "S poznámkou":
        v = v[v["poznamka"] != ""]
    elif faza == "S predošlou registráciou":
        v = v[v["predosla_reg"] != ""]

    tabulka = v[["nazov", "typ", "pic", "erasmus_kod", "predosla_reg", "preverenie", "hotove_kroky", "aktualny_krok", "sposob", "aktualizovane", "poznamka"] + KROK_IDS]
    tabulka = tabulka.rename(columns={
        "nazov": "Škola", "typ": "Typ", "pic": "PIC", "erasmus_kod": "Erasmus kód", "predosla_reg": "Predošlá registrácia v Routri", "preverenie": "Preverenie", "hotove_kroky": "Hotové kroky", "aktualny_krok": "Aktuálny krok",
        "sposob": "Kto vydáva ESC", "aktualizovane": "Aktualizované", "poznamka": "Poznámka",
        **{k["id"]: f"{i}. {k['nazov']}" for i, k in enumerate(obsah.KROKY, start=1)},
    })
    st.dataframe(tabulka, hide_index=True, width="stretch")

    buf = io.BytesIO()
    tabulka.to_excel(buf, index=False, sheet_name="Prehľad")
    st.download_button(
        "Stiahnuť prehľad (Excel)", buf.getvalue(), file_name=f"esc-registracie-{dnes()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.divider()
    st.subheader("Prístupové kódy škôl")
    skoly = nacitaj_skoly()
    bez_kodu = int((skoly["kod"].str.strip() == "").sum())
    st.write(f"Bez kódu: {bez_kodu} z {len(skoly)} škôl.")
    if bez_kodu and st.button("Vygenerovať chýbajúce kódy"):
        skoly = skoly.copy()
        mask = skoly["kod"].str.strip() == ""
        skoly.loc[mask, "kod"] = [novy_kod() for _ in range(int(mask.sum()))]
        get_store().replace(SKOLY, SKOLY_COLS, skoly)
        obnov()
        st.rerun()
    if st.toggle("Zobraziť kódy"):
        st.dataframe(skoly[["nazov", "kod"]].rename(columns={"nazov": "Škola", "kod": "Kód"}), hide_index=True, width="stretch")
        st.download_button(
            "Stiahnuť kódy (CSV)", skoly[["nazov", "kod"]].to_csv(index=False).encode("utf-8-sig"),
            file_name="esc-pristupove-kody.csv", mime="text/csv",
        )
    st.caption("Zoznam škôl a kódy upravujete priamo v hárku „skoly“. Zmeny sa v appke prejavia do minúty alebo po kliknutí na „Načítať znova“.")


# ---------- hlavná stránka ----------

def main():
    st.title("Registrácia vysokej školy do ESC Routra")
    if DEMO:
        st.warning("Skúšobný režim: Google Sheets nie je nastavený, údaje sa ukladajú len lokálne. Heslo správcu je „demo“.")
    try:
        prvy_import()
        doplnenie_kodov()
    except Exception:
        st.error("Úložisko nie je dostupné. Skontrolujte nastavenie Google Sheets (README, časť 3).")
        st.stop()

    if st.session_state.get("admin"):
        if st.sidebar.button("Odhlásiť správcu"):
            st.session_state.pop("admin")
            st.rerun()
        pohlad_spravcu()
        return

    skola_id = st.session_state.get("skola_id")
    if skola_id:
        if st.sidebar.button("Odhlásiť školu"):
            st.session_state.pop("skola_id")
            st.rerun()
        pohlad_skoly(skola_id)
        return

    st.write(obsah.UVOD)
    prihlasenie_spravcu()
    prihlasenie_skoly()
    st.divider()
    st.subheader("Návod")
    zobraz_navod()


main()
