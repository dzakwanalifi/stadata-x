# stadata_x/main.py

from stadata_x.app import StadataXApp

def run():
    """Fungsi titik masuk yang akan dipanggil oleh pyproject.toml."""
    try:
        app = StadataXApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    run()