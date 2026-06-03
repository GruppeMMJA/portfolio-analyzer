"""
Einmalig ausführen um einen neuen User anzulegen und secrets.toml zu generieren.

Aufruf:
    python setup_auth.py
"""

import bcrypt
import os
from pathlib import Path

SECRETS_PATH = Path("portfolio_analyzer/.streamlit/secrets.toml")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


def main():
    print("=== Portfolio Analyzer — User Setup ===\n")

    username = input("Benutzername (z.B. toni): ").strip().lower()
    if not username:
        print("Abbruch: Kein Benutzername eingegeben.")
        return

    name = input("Anzeigename (z.B. Toni Jungbauer): ").strip()
    email = input("E-Mail: ").strip().lower()

    import getpass
    password = getpass.getpass("Passwort (wird nicht angezeigt): ")
    if len(password) < 8:
        print("Abbruch: Passwort muss mindestens 8 Zeichen haben.")
        return

    hashed = hash_password(password)

    # Prüfen ob secrets.toml schon existiert
    existing_users = {}
    if SECRETS_PATH.exists():
        content = SECRETS_PATH.read_text(encoding="utf-8")
        print(f"\n{SECRETS_PATH} existiert bereits.")
        action = input("User hinzufügen (a) oder Datei neu erstellen (n)? [a/n]: ").strip().lower()
        if action != "n":
            # Bestehende Datei behalten und nur neuen User ergänzen
            print("\nFüge User zur bestehenden secrets.toml hinzu...")
            # Neuen Eintrag anhängen
            new_entry = f"""
[credentials.usernames.{username}]
email = "{email}"
name = "{name}"
password = "{hashed}"
"""
            with open(SECRETS_PATH, "a", encoding="utf-8") as f:
                f.write(new_entry)
            print(f"User '{username}' wurde hinzugefügt.")
            return

    # Neue secrets.toml erstellen
    import secrets as _secrets
    cookie_key = _secrets.token_hex(32)

    content = f"""# Streamlit Authenticator — Zugangsdaten
# Diese Datei NIEMALS auf GitHub pushen!

[credentials.usernames.{username}]
email = "{email}"
name = "{name}"
password = "{hashed}"

[cookie]
expiry_days = 30
key = "{cookie_key}"
name = "portfolio_auth"
"""

    SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SECRETS_PATH.write_text(content, encoding="utf-8")

    print(f"\n✓ secrets.toml erstellt: {SECRETS_PATH}")
    print(f"✓ User '{username}' angelegt")
    print("\nNächste Schritte:")
    print("  1. App starten: python -m streamlit run portfolio_analyzer/app.py")
    print("  2. Für Streamlit Cloud: Inhalt von secrets.toml ins Cloud-Dashboard kopieren")


if __name__ == "__main__":
    main()
