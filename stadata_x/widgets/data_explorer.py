# stadata_x/widgets/data_explorer.py

import asyncio
import time 
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static, RadioSet, RadioButton
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


class DynamicTableSelected(Message):
    """Pesan yang dikirim saat sebuah tabel dinamis dipilih di DataExplorer."""
    def __init__(self, var_id: str, title: str):
        self.var_id = var_id
        self.title = title
        super().__init__()


class DataExplorer(Widget):
    """Widget komposit untuk menampilkan dan menavigasi data BPS."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_view = "domain"
        self.selected_domain = None
        self.is_loading = False
        self._selection_lock = asyncio.Lock()
        self.table_type = "static" 

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
            # Temporarily hide dynamic table selector due to async generator bug
            with RadioSet(id="table-type-selector", disabled=True, classes="hidden"):
                yield RadioButton("Tabel Statis", value=True, id="static")
                yield RadioButton("Tabel Dinamis", id="dynamic", disabled=True)
            yield StadataDataTable(id="main-datatable")
            yield LoadingSpinner(id="loader")

    @on(RadioSet.Changed)
    async def on_table_type_changed(self, event: RadioSet.Changed) -> None:
        """Dipanggil saat pengguna mengganti jenis tabel."""
        self.table_type = event.pressed.id
        if self.selected_domain:
            domain_id, domain_name = self.selected_domain
            await self._load_table_list(domain_id, domain_name)

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

        self.query_one("#table-type-selector", RadioSet).disabled = True
        self.query_one("#table-type-selector").styles.display = "none"

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
            self.table_type = "static"
            # Skip RadioSet initialization since it's hidden
            # self.query_one(RadioSet).pressed_index = 0
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

    async def _load_table_list(self, domain_id: str, domain_name: str):
        """Mengambil dan menampilkan daftar tabel statis ATAU dinamis."""
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
                "footer": f"Memuat daftar tabel {self.table_type}..."
            }))

            if self.table_type == "static":
                df = await self._fetch_with_min_delay(
                    self.app.api_client.list_static_tables(domain_id=domain_id)
                )
                table.add_columns("ID", "Nama Tabel", "Terakhir Update")
                if not df.empty:
                    for row in df.itertuples():
                        table.add_row(str(row.table_id), str(row.title), str(row.updt_date))
                else:
                    table.add_row("", "Tidak ada tabel statis ditemukan", "")

            else: # self.table_type == "dynamic"
                df = await self._fetch_with_min_delay(
                    self.app.api_client.list_dynamic_tables(domain_id=domain_id)
                )
                table.add_columns("ID", "Judul Variabel", "Subjek")
                if not df.empty:
                    for row in df.itertuples():
                        table.add_row(str(row.var_id), str(row.title), str(row.sub_name))
                        table.get_row_at(table.row_count - 1).metadata_source = getattr(row, "source_domain", None)
                else:
                    table.add_row("", "Tidak ada tabel dinamis ditemukan", "")

            self.post_message(DataExplorerMessage("update_prompt", {
                "breadcrumbs": breadcrumbs,
                "footer": "[Esc] Kembali  |  [Enter] Pilih Tabel"
            }))

            self.current_view = "table"
        except Exception as e:
            self.post_message(DataExplorerMessage("update_prompt", {
                "breadcrumbs": f"[bold red]Error memuat tabel {self.table_type}[/]",
                "footer": str(e)
            }))
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

                try:
                    selector = self.query_one("#table-type-selector", RadioSet)
                    selector.disabled = False
                    selector.styles.display = "block"
                except Exception:
                    pass

                self.post_message(DataExplorerMessage("update_prompt", {"text": f"Memuat tabel untuk: [bold cyan]{domain_name}[/]..."}))
                await self._load_table_list(domain_id, domain_name)

            elif self.current_view == "table":
                row_data = event.control.get_row_at(event.cursor_row)

                if not row_data or not row_data[0]:
                    return

                if self.table_type == "static":
                    table_id, table_title = row_data[0], row_data[1]
                    self.post_message(TableSelected(table_id, table_title))
                else:
                    var_id, title = row_data[0], row_data[1]
                    metadata_source = getattr(event.control.get_row_at(event.cursor_row), "metadata_source", None)
                    message = DynamicTableSelected(var_id, title)
                    message.metadata_source = metadata_source
                    self.post_message(message)
