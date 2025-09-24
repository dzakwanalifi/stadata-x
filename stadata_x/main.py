# stadata_x/main.py

from stadata_x.app import StadataXApp

def run():
    """Fungsi titik masuk yang akan dipanggil oleh pyproject.toml."""
    app = StadataXApp()
    app.run()

if __name__ == "__main__":
    run()