# stadata_x/config.py

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".stadata-x"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> dict:
    """Membaca seluruh file konfigurasi."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_config(data: dict) -> None:
    """Menyimpan data ke file konfigurasi."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_token(token: str) -> None:
    config_data = load_config()
    config_data["api_token"] = token
    save_config(config_data)

def load_token() -> str | None:
    return load_config().get("api_token")
