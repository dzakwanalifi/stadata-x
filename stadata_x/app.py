# stadata_x/app.py

from textual.app import App
from stadata_x.api_client import ApiClient
from stadata_x.screens.welcome_screen import WelcomeScreen
from stadata_x.screens.dashboard_screen import DashboardScreen
from stadata_x.screens.settings_screen import SettingsScreen
from stadata_x.screens.table_view_screen import TableViewScreen


class StadataXApp(App):
    """Sebuah aplikasi TUI canggih untuk data BPS."""
    CSS_PATH = "assets/app.css"
    SCREENS = {
        "welcome": WelcomeScreen,
        "dashboard": DashboardScreen,
        "settings": SettingsScreen,
        "table_view": TableViewScreen,
    }
    BINDINGS = [
        ("q", "quit", "Keluar"),
        ("s", "push_screen('settings')", "Pengaturan"), 
        ("d", "toggle_dark", "Toggle Mode Gelap/Terang"),
    ]

    def __init__(self):
        super().__init__()
        self._api_client = None

    @property
    def api_client(self) -> ApiClient:
        """Properti untuk mengakses atau membuat ulang klien API."""
        if self._api_client is None:
            self._api_client = ApiClient()
        return self._api_client

    @api_client.setter
    def api_client(self, value):
        """Memungkinkan kita untuk mereset klien API."""
        self._api_client = value


    def on_mount(self) -> None:
        self.push_screen("welcome")