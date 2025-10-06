# stadata_x/screens/dashboard_screen.py

from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, Footer
from textual import on

from stadata_x.widgets.header import StadataHeader
from stadata_x.widgets.footer import StadataFooter
from stadata_x.widgets.data_explorer import DataExplorer, DataExplorerMessage, TableSelected, DynamicTableSelected
from stadata_x.widgets.data_table import StadataDataTable
from stadata_x.screens.table_view_screen import TableViewScreen
from stadata_x.screens.dynamic_table_builder_screen import DynamicTableBuilderScreen 

class DashboardScreen(Screen):
    """Layar utama yang sekarang hanya bertugas sebagai manajer layout."""

    BINDINGS = [
        ("escape", "go_back", "Kembali"),
    ]

    def __init__(self):
        super().__init__()
        self._last_token_state = None

    def compose(self) -> ComposeResult:
        yield StadataHeader()
        yield Static(id="breadcrumbs-bar", classes="breadcrumbs")
        yield DataExplorer(id="data-explorer")
        yield Footer()

    async def on_mount(self) -> None:
        """Mendelegasikan pemuatan awal ke widget DataExplorer."""
        self._last_token_state = self.app.api_client.is_ready
        explorer = self.query_one(DataExplorer)
        breadcrumbs_bar = self.query_one("#breadcrumbs-bar")

        if not self.app.api_client.is_ready:
            breadcrumbs_bar.update("[bold red]Token API tidak valid.[/]")
            self.query_one(Footer).show_keys = False 
        else:
            self.query_one(Footer).show_keys = True 
            await explorer.display_domains()

    async def on_screen_resume(self) -> None:
        """Memuat ulang data jika token berubah."""
        current_token_state = self.app.api_client.is_ready
        if self._last_token_state != current_token_state:
            self._last_token_state = current_token_state
            await self.on_mount()

    @on(DataExplorerMessage)
    def handle_data_explorer_message(self, event: DataExplorerMessage):
        """Menangani pesan dari DataExplorer widget untuk update UI."""
        if event.action == "update_prompt":
            breadcrumbs_bar = self.query_one("#breadcrumbs-bar")
            footer = self.query_one(Footer)

            if "breadcrumbs" in event.data:
                breadcrumbs_bar.update(event.data["breadcrumbs"])

            if "footer" in event.data:
                footer.title = event.data["footer"]

            if "text" in event.data:
                breadcrumbs_bar.update(event.data["text"])

    @on(TableSelected)
    def handle_table_selection_from_explorer(self, event: TableSelected):
        """Menangkap pesan dari DataExplorer dan membuka layar pratinjau."""
        explorer = self.query_one(DataExplorer)

        table_id = event.table_id
        table_title = event.table_title

        domain_id, domain_name = explorer.selected_domain
        self.app.push_screen(
            TableViewScreen(domain_id, table_id, table_title, domain_name)
        )

    @on(DynamicTableSelected)
    def handle_dynamic_table_selection_from_explorer(self, event: DynamicTableSelected):
        explorer = self.query_one(DataExplorer)

        var_id = event.var_id
        title = event.title
        metadata_source = getattr(event, "metadata_source", None)

        if explorer.selected_domain:
            domain_id, domain_name = explorer.selected_domain
            source_domain = metadata_source or domain_id
            self.app.push_screen(
                DynamicTableBuilderScreen(
                    domain_id=domain_id,
                    var_id=var_id,
                    title=title,
                    domain_name=domain_name,
                    metadata_source=source_domain
                )
            )
        else:
            self.app.notify("Domain tidak terpilih.", title="Error Navigasi", severity="error")

    async def action_go_back(self) -> None:
        """Aksi yang dipanggil saat tombol Escape ditekan."""
        explorer = self.query_one(DataExplorer)
        if explorer.current_view == "table":
            await explorer.display_domains()