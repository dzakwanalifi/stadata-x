# stadata_x/screens/settings_screen.py

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Center, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Input, Button, Static, Label

from pathlib import Path

from stadata_x import config
from stadata_x.api_client import ApiClient, ApiTokenError, NoInternetError

INSTRUCTIONS = """
Cara Mendapatkan Token API BPS:
1. Buka https://webapi.bps.go.id/developer/
2. Daftar atau Masuk ke akun Anda.
3. Salin Token API dari dashboard Anda.
4. Tempel di bawah ini dan simpan.
"""

class SettingsScreen(Screen):
    """Layar untuk konfigurasi token API."""

    BINDINGS = [("escape", "app.pop_screen", "Kembali")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Center():
            with Vertical(id="settings-container"):
                yield Label("Token API BPS Anda:") 
                yield Input(
                    value=config.load_token() or "",
                    password=True,
                    placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    id="token-input"
                )

                yield Label("Folder Unduhan Default (kosongkan untuk folder saat ini):", classes="label-top-margin")
                yield Input(
                    value=config.load_config().get("download_path", ""),
                    placeholder=str(Path.home()),
                    id="download-path-input"
                )

                yield Static(id="status-message", classes="status")

                with Horizontal(classes="buttons"):
                    yield Button("Simpan Token", variant="primary", id="save-button")
                    yield Button("Tes Koneksi", id="test-button")
                    yield Button("Kembali", id="back-button")

                yield Static(INSTRUCTIONS, classes="instructions", markup=True)
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Menangani penekanan tombol."""
        if event.button.id == "save-button":
            await self.action_save_token()
        elif event.button.id == "back-button":
            self.app.pop_screen()
        elif event.button.id == "test-button":
            await self.action_test_connection()

    async def action_save_token(self) -> None:
        """Menyimpan token dan pengaturan lainnya."""
        token_input = self.query_one("#token-input", Input)
        path_input = self.query_one("#download-path-input", Input)
        status_message = self.query_one("#status-message", Static)

        token = token_input.value.strip()
        path_value = path_input.value.strip()

        if token:
            config.save_token(token)

        current_config = config.load_config()
        current_config["download_path"] = path_value
        config.save_config(current_config)

        status_message.update("[green]✔ Pengaturan berhasil disimpan.[/green]")
        self.app.api_client = None 

    async def action_test_connection(self) -> None:
        """Menguji koneksi ke API BPS dengan token yang dimasukkan."""
        token_input = self.query_one("#token-input", Input)
        status_message = self.query_one("#status-message", Static)
        token = token_input.value.strip()

        if not token:
            status_message.update("[red]✖ Masukkan token terlebih dahulu untuk dites.[/red]")
            return

        status_message.update("[yellow]Menguji koneksi...[/yellow]")

        test_client = ApiClient(token=token)

        try:
            if not test_client.is_ready:
                raise ApiTokenError("Format token salah atau stadata gagal inisialisasi.")

            await test_client.list_domains()
            status_message.update("[green]✔ Koneksi berhasil! Token valid.[/green]")
        except ApiTokenError:
            status_message.update("[red]✖ Tes Gagal: Token tidak valid atau kedaluwarsa.[/red]")
        except NoInternetError:
            status_message.update("[red]✖ Tes Gagal: Tidak ada koneksi internet.[/red]")
        except Exception as e:
            status_message.update(f"[red]✖ Tes Gagal: Terjadi error tak terduga.\n{e}[/red]")

    def on_mount(self) -> None:
        """Fokuskan ke input saat layar dimuat."""
        self.query_one("#token-input", Input).focus()