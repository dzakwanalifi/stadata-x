# stadata_x/widgets/header.py

from textual.widgets import Header

class StadataHeader(Header):
    """Header kustom dengan judul aplikasi."""

    def __init__(self) -> None:
        super().__init__(show_clock=True)
        self.title = "[bold cyan]📊 STADATA-X[/]"
