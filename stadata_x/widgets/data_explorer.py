# stadata_x/widgets/data_explorer.py

import asyncio
import time 
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical
from textual import on
from textual.events import Message

from .data_table import StadataDataTable
from .spinner import LoadingSpinner


class DataExplorerMessage(Message):
    """Message sent by DataExplorer to communicate with parent screen."""
    def __init__(self, action: str, data: dict = None):
        self.action = action
        self.data = data or {}
        super().__init__()


class TableSelected(Message):
    """Pesan yang dikirim saat sebuah tabel dipilih di DataExplorer."""
    def __init__(self, table_id: str, table_title: str):
        self.table_id = table_id
        self.table_title = table_title
        super().__init__()


class DataExplorer(Widget):
    """Widget komposit untuk menampilkan dan menavigasi data BPS."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_view = "domain"
        self.selected_domain = None
        self.is_loading = False 
        self._selection_lock = asyncio.Lock() 

    async def _fetch_with_min_delay(self, awaitable_task, min_delay=0.3):
        """
        Menjalankan task sambil memastikan ada penundaan minimal untuk UX.
        Ini mencegah spinner "berkedip" dan hilang terlalu cepat.
        """
        data_result, _ = await asyncio.gather(
            awaitable_task,
            asyncio.sleep(min_delay)
        )

        return data_result

    def compose(self) -> ComposeResult:
        with Vertical(id="content-area"):
            yield StadataDataTable(id="main-datatable")
            yield LoadingSpinner(id="loader")

    async def display_domains(self):
        """Mengambil dan menampilkan daftar domain dari BPS."""
        if self.is_loading:
            return

        self.is_loading = True
        table = self.query_one("#main-datatable", StadataDataTable)
        loader = self.query_one("#loader", LoadingSpinner)

        table.disabled = True 
        table.display = False
        loader.display = True
        loader.start()

        table.clear(columns=True)

        try:
            self.post_message(DataExplorerMessage("update_prompt", {
                "breadcrumbs": "[bold]Beranda[/]",
                "footer": "Memuat daftar domain..."
            }))

            df = await self._fetch_with_min_delay(
                self.app.api_client.list_domains()
            )
            self.post_message(DataExplorerMessage("update_prompt", {
                "breadcrumbs": "[bold]Beranda[/]",
                "footer": "[Enter] Pilih Wilayah"
            }))

            table.add_columns("ID Domain", "Nama Wilayah")
            for row in df.itertuples():
                table.add_row(row.domain_id, row.domain_name)

            self.current_view = "domain"
            self.selected_domain = None
        except Exception as e:
            self.post_message(DataExplorerMessage("update_prompt", {
                "breadcrumbs": "[bold red]Error[/]",
                "footer": str(e)
            }))
            self.current_view = "domain"
            self.selected_domain = None
        finally:
            loader.stop()
            loader.display = False
            table.display = True
            table.disabled = False 
            self.is_loading = False 

    async def display_tables_for(self, domain_id: str, domain_name: str):
        """Mengambil dan menampilkan daftar tabel untuk domain terpilih."""
        if self.is_loading:
            return

        self.is_loading = True
        table = self.query_one("#main-datatable", StadataDataTable)
        loader = self.query_one("#loader", LoadingSpinner)

        table.disabled = True 
        table.display = False
        loader.display = True
        loader.start()

        table.clear(columns=True)

        try:
            breadcrumbs = f"Beranda > [cyan]{domain_name}[/]"
            self.post_message(DataExplorerMessage("update_prompt", {
                "breadcrumbs": breadcrumbs,
                "footer": "Memuat tabel..."
            }))

            df = await self._fetch_with_min_delay(
                self.app.api_client.list_static_tables(domain_id=domain_id)
            )

            self.post_message(DataExplorerMessage("update_prompt", {
                "breadcrumbs": breadcrumbs,
                "footer": "[Esc] Kembali  |  [Enter] Lihat Tabel"
            }))

            table.add_columns("ID", "Nama Tabel", "Terakhir Update")
            if not df.empty:
                for row in df.itertuples():
                    table.add_row(str(row.table_id), str(row.title), str(row.updt_date))
            else:
                table.add_row("", "Tidak ada tabel statis ditemukan", "")

            self.current_view = "table"
        except Exception as e:
            self.post_message(DataExplorerMessage("update_prompt", {"text": f"[red]Error: {str(e)}[/red]"}))
            self.current_view = "domain"
        finally:
            loader.stop()
            loader.display = False
            table.display = True
            table.disabled = False 
            self.is_loading = False 

    @on(StadataDataTable.RowSelected)
    async def handle_row_selection(self, event: StadataDataTable.RowSelected):
        """Mendelegasikan event pemilihan baris."""
        if self._selection_lock.locked():
            return 

        async with self._selection_lock:
            if self.is_loading:
                return

            if self.current_view == "domain":
                row_data = event.control.get_row_at(event.cursor_row)
                domain_id, domain_name = row_data[0], row_data[1]

                if not domain_id or domain_id == "":
                    return

                self.selected_domain = (domain_id, domain_name)
                self.post_message(DataExplorerMessage("update_prompt", {"text": f"Memuat tabel untuk: [bold cyan]{domain_name}[/]..."}))
                await self.display_tables_for(domain_id, domain_name)

            elif self.current_view == "table":
                row_data = event.control.get_row_at(event.cursor_row)
                table_id, table_title = row_data[0], row_data[1]

                if table_id and table_id != "":
                    self.post_message(TableSelected(table_id, table_title))
