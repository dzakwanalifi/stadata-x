# stadata_x/screens/welcome_screen.py

from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

LOGO_PATH = Path(__file__).parent.parent / "assets/logo.txt"

class WelcomeScreen(Screen):
    """Layar pembuka yang 'heboh' untuk aplikasi."""

    def compose(self) -> ComposeResult:
        """Render UI untuk layar ini."""
        logo_text = LOGO_PATH.read_text(encoding='utf-8')

        yield Static(logo_text, id="logo")
        yield Static("Membuka Data Indonesia, Satu Perintah Sekaligus.", id="slogan")
        yield Static("\nTekan Enter untuk Memulai...", id="prompt")

    def on_key(self, event) -> None:
        """Menangani penekanan tombol Enter."""
        if event.key == "enter":
            def go_to_dashboard():
                self.app.push_screen("dashboard")

            self.app.call_after_refresh(go_to_dashboard)