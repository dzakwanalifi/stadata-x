# stadata_x/widgets/spinner.py

from textual.widgets import Static
from textual.timer import Timer


class LoadingSpinner(Static):
    """Custom loading spinner dengan animasi teks titik-titik."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.base_text = "Sedang memuat data BPS"
        self.frames = [
            f"{self.base_text}",
            f"{self.base_text}.",
            f"{self.base_text}..",
            f"{self.base_text}...",
        ]

        self.frame_index = 0
        self.timer: Timer | None = None

    def on_mount(self) -> None:
        """Widget dimount - tidak langsung mulai animasi."""
        self.update(f"[bold white]{self.frames[0]}[/bold white]")

    def on_unmount(self) -> None:
        """Stop animasi saat widget unmount."""
        if self.timer:
            self.timer.stop()
            self.timer = None

    def _animate(self) -> None:
        """Update frame animasi."""
        self.update(f"[bold white]{self.frames[self.frame_index]}[/bold white]")
        self.frame_index = (self.frame_index + 1) % len(self.frames)

    def start(self) -> None:
        """Mulai animasi spinner."""
        if not self.timer:
            self.timer = self.set_interval(0.3, self._animate)
        self.display = True

    def stop(self) -> None:
        """Stop animasi spinner."""
        if self.timer:
            self.timer.stop()
            self.timer = None
        self.display = False
