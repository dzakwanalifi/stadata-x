# stadata_x/screens/download_dialog_screen.py

from pathlib import Path
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Grid, Vertical
from textual.widgets import Button, Input, Label, RadioSet, RadioButton

class DownloadDialogScreen(ModalScreen):
    """Layar dialog untuk mengonfirmasi detail unduhan."""

    def __init__(self, table_id: str, table_title: str):
        self.table_id = table_id
        self.table_title = table_title
        clean_title = "".join(c for c in table_title if c.isalnum() or c in " .-_").rstrip()
        self.default_filename = f"{clean_title[:50]}_{table_id}"
        super().__init__()

    def compose(self) -> ComposeResult:
        with Grid(id="download-dialog"):
            yield Label("Simpan Sebagai:")
            yield Input(self.default_filename, id="filename-input")

            yield Label("Format:")
            with Vertical():
                with RadioSet(id="format-radioset"):
                    yield RadioButton("CSV (.csv)", id="csv", value=True)
                    yield RadioButton("Excel (.xlsx)", id="xlsx")
                    yield RadioButton("JSON (.json)", id="json")

            yield Button("Batal", variant="default", id="cancel-button")
            yield Button("Download", variant="primary", id="download-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "download-button":
            filename_input = self.query_one("#filename-input", Input).value
            radioset = self.query_one("#format-radioset", RadioSet)
            selected_format = radioset.pressed_button.id

            if not filename_input.endswith(f".{selected_format}"):
                filename_input += f".{selected_format}"

            self.dismiss((filename_input, selected_format))
        else:
            self.dismiss(None)
