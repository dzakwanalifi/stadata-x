# stadata_x/screens/table_view_screen.py

import pandas as pd
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, LoadingIndicator
from textual.containers import VerticalScroll

from stadata_x.widgets.data_table import StadataDataTable
from stadata_x.screens.download_dialog_screen import DownloadDialogScreen

def is_numeric_col(series: pd.Series, sample_size: int = 50, threshold: float = 0.8) -> bool:
    """
    Mendeteksi apakah sebuah kolom (Series) kemungkinan besar berisi data numerik.

    Args:
        series: Kolom DataFrame Pandas untuk dianalisis.
        sample_size: Jumlah baris sampel yang akan diperiksa untuk efisiensi.
        threshold: Persentase (0.0 - 1.0) sampel yang harus numerik agar dianggap numerik.

    Returns:
        True jika kolom kemungkinan besar numerik, False jika tidak.
    """
    cleaned_series = series.dropna().sample(n=min(len(series.dropna()), sample_size))

    if cleaned_series.empty:
        return False

    numeric_count = 0
    for item in cleaned_series:
        try:
            str_item = str(item).replace(",", "")
            if str_item.strip():
                float(str_item)
                numeric_count += 1
        except (ValueError, TypeError):
            continue

    return (numeric_count / len(cleaned_series)) >= threshold

class TableViewScreen(Screen):
    """Layar untuk menampilkan pratinjau isi tabel BPS."""

    BINDINGS = [
        ("d", "download_table", "Download CSV"),
        ("escape", "app.pop_screen", "Kembali"),
    ]

    def __init__(self, domain_id: str, table_id: str, table_title: str, domain_name: str):
        self.domain_id = domain_id
        self.table_id = table_id
        self.table_title = table_title
        self.domain_name = domain_name
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll():
            yield Static(f"[bold]Pratinjau Tabel:[/bold] {self.table_title}", id="table-view-title")
            yield LoadingIndicator()
            yield StadataDataTable(id="table-preview")
        yield Footer()

    async def on_mount(self) -> None:
        """Ambil data tabel dan tampilkan."""
        table = self.query_one("#table-preview", StadataDataTable)
        loader = self.query_one(LoadingIndicator)
        table.display = False

        try:
            df = await self.app.api_client.view_static_table(self.domain_id, self.table_id)

            loader.display = False
            table.display = True

            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [' '.join(map(str, col)).strip() for col in df.columns.values]
                else:
                    df.columns = [str(col) for col in df.columns]

                table.clear(columns=True)

                column_keys = [table.add_column(label=col_name) for col_name in df.columns]

                for i, col_name in enumerate(df.columns):
                    is_numeric = is_numeric_col(df[col_name])
                    table.columns[column_keys[i]].justify = "right" if is_numeric else "left"

                max_rows = 100
                total_rows = len(df)
                display_df = df.head(max_rows) if total_rows > max_rows else df

                info_text = f"Menampilkan {max_rows} dari {total_rows} baris total. Gunakan 'd' untuk download lengkap." if total_rows > max_rows else None

                rows_data = []
                for row in display_df.itertuples(index=False, name=None):
                    row_list = [str(cell) for cell in row]
                    rows_data.append(row_list)

                if rows_data:
                    table.add_rows(rows_data)

                if info_text:
                    spanning_row = [f"[dim]{info_text}[/dim]"] + [""] * (len(df.columns) - 1)
                    table.add_row(*spanning_row)

            else:
                table.add_column("Info")
                table.add_row("Tidak ada data untuk ditampilkan.")


        except Exception as e:
            loader.display = False
            error_msg = str(e)
            # Provide more user-friendly error messages
            if "Tidak ada koneksi" in error_msg or "connection" in error_msg.lower():
                user_msg = "Tidak ada koneksi internet"
            elif "string indices must be integers" in error_msg:
                user_msg = "Format data tabel tidak sesuai (kemungkinan tabel kosong atau error API)"
            elif "empty" in error_msg.lower():
                user_msg = "Tabel kosong atau tidak tersedia"
            else:
                user_msg = f"Error: {error_msg[:100]}..."

            self.app.notify(f"Gagal memuat pratinjau: {user_msg}", severity="error", title="Error")
            self.app.pop_screen()

    async def action_download_table(self) -> None:
        """Membuka dialog unduhan dan memproses hasilnya."""

        def download_callback(result):
            """Dipanggil setelah dialog ditutup."""
            if result:
                filename, file_format = result
                self.run_worker(self.perform_download(filename, file_format))

        self.app.push_screen(
            DownloadDialogScreen(self.table_id, self.table_title),
            download_callback
        )

    async def perform_download(self, filename: str, file_format: str) -> None:
        """Melakukan pekerjaan download yang sebenarnya."""
        try:
            filepath = await self.app.api_client.download_table(
                self.domain_id,
                self.table_id,
                filename=filename,
                format=file_format
            )
            self.app.notify(f"File disimpan di: {filepath}", title="Download Berhasil", severity="information")
        except Exception as e:
            self.app.notify(f"Gagal download: {e}", title="Error", severity="error")
