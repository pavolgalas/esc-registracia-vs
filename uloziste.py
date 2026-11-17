"""Ukladanie údajov: Google Sheets (ostrá prevádzka) alebo lokálne CSV súbory (skúšobný režim).

Obe úložiská majú rovnaké rozhranie:
    read(tab, cols)             -> DataFrame so stĺpcami `cols` (všetko ako text)
    upsert(tab, cols, row)      -> vloží alebo prepíše riadok podľa prvého stĺpca
    replace(tab, cols, df)      -> prepíše celý hárok
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

SKOLY = "skoly"
STAV = "stav"
SKOLY_COLS = ["skola_id", "nazov", "typ", "pic", "erasmus_kod", "predosla_reg", "kod"]
STAV_COLS = ["skola_id", "k1", "k2", "k3", "k4", "k5", "k6", "sposob", "poznamka", "aktualizovane", "preverenie"]


def _frame(rows: list[list[str]], header: list[str], cols: list[str]) -> pd.DataFrame:
    width = len(header)
    fixed = [(r + [""] * width)[:width] for r in rows]
    df = pd.DataFrame(fixed, columns=header, dtype=str)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols].fillna("")
    return df[df[cols[0]].str.strip() != ""].reset_index(drop=True)


class SheetsStore:
    """Jeden Google Sheet s hárkami `skoly` a `stav`."""

    nazov = "Google Sheets"

    def __init__(self, service_account_info: dict, sheet_id: str):
        import gspread

        self._gspread = gspread
        client = gspread.service_account_from_dict(dict(service_account_info))
        self.sh = client.open_by_key(sheet_id)

    def _ws(self, tab: str, cols: list[str]):
        try:
            ws = self.sh.worksheet(tab)
        except self._gspread.WorksheetNotFound:
            ws = self.sh.add_worksheet(title=tab, rows=200, cols=len(cols))
        header = ws.row_values(1)
        chybajuce = [c for c in cols if c not in header]
        if chybajuce:
            # Nové stĺpce z novšej verzie appky sa pridajú na koniec hlavičky.
            nova = header + chybajuce
            if ws.col_count < len(nova):
                ws.add_cols(len(nova) - ws.col_count)
            ws.update(range_name="A1", values=[nova], value_input_option="RAW")
        return ws

    def read(self, tab: str, cols: list[str]) -> pd.DataFrame:
        values = self._ws(tab, cols).get_all_values()
        if not values:
            return pd.DataFrame(columns=cols, dtype=str)
        return _frame(values[1:], values[0], cols)

    def upsert(self, tab: str, cols: list[str], row: dict) -> None:
        ws = self._ws(tab, cols)
        header = ws.row_values(1)
        values = [[str(row.get(c, "")) for c in header]]
        keys = ws.col_values(1)
        key = str(row[cols[0]])
        if key in keys[1:]:
            r = keys.index(key, 1) + 1
            ws.update(range_name=f"A{r}", values=values, value_input_option="RAW")
        else:
            ws.append_row(values[0], value_input_option="RAW")

    def replace(self, tab: str, cols: list[str], df: pd.DataFrame) -> None:
        ws = self._ws(tab, cols)
        ws.clear()
        data = [cols] + df[cols].astype(str).values.tolist()
        ws.update(range_name="A1", values=data, value_input_option="RAW")


class LocalStore:
    """CSV súbory v priečinku `data/`. Len na skúšanie – na Streamlit Cloude sa po reštarte stratia."""

    nazov = "lokálne súbory (skúšobný režim)"

    def __init__(self, folder: Path):
        self.folder = folder
        self.folder.mkdir(parents=True, exist_ok=True)

    def _path(self, tab: str) -> Path:
        return self.folder / f"{tab}.csv"

    def read(self, tab: str, cols: list[str]) -> pd.DataFrame:
        p = self._path(tab)
        if not p.exists():
            return pd.DataFrame(columns=cols, dtype=str)
        df = pd.read_csv(p, dtype=str, keep_default_na=False)
        return _frame(df.values.tolist(), list(df.columns), cols)

    def upsert(self, tab: str, cols: list[str], row: dict) -> None:
        df = self.read(tab, cols)
        new = {c: str(row.get(c, "")) for c in cols}
        mask = df[cols[0]] == new[cols[0]]
        if mask.any():
            df.loc[mask, cols] = [new[c] for c in cols]
        else:
            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
        df.to_csv(self._path(tab), index=False)

    def replace(self, tab: str, cols: list[str], df: pd.DataFrame) -> None:
        df[cols].astype(str).to_csv(self._path(tab), index=False)
