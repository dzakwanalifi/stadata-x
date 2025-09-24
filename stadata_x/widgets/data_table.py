# stadata_x/widgets/data_table.py

from textual.widgets import DataTable

class StadataDataTable(DataTable):
    """Widget tabel data yang akan menampilkan data BPS."""

    def on_mount(self) -> None:
        """Inisialisasi tabel sebagai kanvas kosong."""
        self.cursor_type = "row"

    def clear(self, columns: bool = False) -> None:
        """Clear tabel data dan opsional juga kolom."""
        super().clear()
        if columns:
            for column in list(self.ordered_columns):
                self.remove_column(column.key)
