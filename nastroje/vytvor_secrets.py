"""Vytvorí obsah secrets pre appku z JSON kľúča servisného účtu Google.

Použitie:
    python nastroje/vytvor_secrets.py cesta/ku/klucu.json

Skript sa spýta na ID tabuľky a heslo správcu a zapíše súbor .streamlit/secrets.toml.
Jeho obsah potom skopírujte do Streamlit Community Cloud (App settings -> Secrets).
Súbor secrets.toml ani JSON kľúč nenahrávajte na GitHub.
"""
from __future__ import annotations

import getpass
import json
import re
import sys
from pathlib import Path

POLIA = [
    "type", "project_id", "private_key_id", "private_key", "client_email", "client_id",
    "auth_uri", "token_uri", "auth_provider_x509_cert_url", "client_x509_cert_url", "universe_domain",
]


def toml_str(hodnota: str) -> str:
    # JSON reťazec je zároveň platný TOML reťazec (rovnaké escape sekvencie).
    return json.dumps(hodnota)


def sheet_id_z(vstup: str) -> str:
    """Prijme ID aj celú adresu tabuľky."""
    m = re.search(r"/spreadsheets/d/([A-Za-z0-9_-]+)", vstup)
    return m.group(1) if m else vstup.strip()


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Použitie: python nastroje/vytvor_secrets.py cesta/ku/klucu.json")
    kluc = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if kluc.get("type") != "service_account":
        sys.exit("Súbor nie je JSON kľúč servisného účtu (chýba \"type\": \"service_account\").")

    sheet_id = sheet_id_z(input("Adresa alebo ID Google tabuľky: "))
    heslo = getpass.getpass("Heslo správcu appky (aspoň 12 znakov): ")
    if len(heslo) < 12:
        sys.exit("Heslo je príliš krátke.")

    riadky = [
        f"admin_heslo = {toml_str(heslo)}",
        f"sheet_id = {toml_str(sheet_id)}",
        "",
        "[gcp_service_account]",
    ]
    riadky += [f"{k} = {toml_str(str(kluc[k]))}" for k in POLIA if k in kluc]

    ciel = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
    ciel.parent.mkdir(exist_ok=True)
    ciel.write_text("\n".join(riadky) + "\n", encoding="utf-8")
    print(f"Zapísané: {ciel}")
    print(f"Tabuľku zdieľajte s týmto e-mailom ako Editor: {kluc['client_email']}")


if __name__ == "__main__":
    main()
