# stadata_x/screens/dynamic_table_builder_screen.py

from typing import Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Static, LoadingIndicator, Button,
    RadioSet, RadioButton, Checkbox, Collapsible
)
from textual.containers import VerticalScroll, Vertical, Horizontal
from textual.binding import Binding
from textual import on

from stadata_x.widgets.data_table import StadataDataTable
from stadata_x.api_client import BpsApiDataError
from stadata_x.screens.download_dialog_screen import DownloadDialogScreen

class DynamicTableBuilderScreen(Screen):
    """Layar interaktif untuk membangun dan melihat pratinjau tabel dinamis."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Kembali", show=True),
        Binding("d", "download_table", "Download Tabel", show=False),
    ]

    def __init__(self, domain_id: str, var_id: str, title: str, domain_name: str, metadata_source: Optional[str] = None):
        super().__init__()
        self.domain_id = domain_id
        self.var_id = var_id
        self.title = title
        self.domain_name = domain_name
        self.metadata_source = metadata_source or domain_id
        self.metadata = {}
        self.last_df = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(f"[bold]Pembangun Tabel Dinamis[/]\n[cyan]{self.title}[/]", id="builder-title")

        with VerticalScroll(id="builder-container"):
            yield Static("Memuat opsi konfigurasi...", id="builder-status")
            yield LoadingIndicator()

            # Kontainer untuk widget konfigurasi yang akan dibuat secara dinamis
            yield Vertical(id="config-area", classes="hidden")

            yield Button("Tampilkan Tabel", variant="primary", id="generate-table-button", disabled=True)

        with Vertical(id="preview-area"):
            yield Static("Pratinjau Tabel", classes="preview-title")
            yield LoadingIndicator(id="preview-loader", classes="hidden")
            yield StadataDataTable(id="table-preview")

        yield Footer()

    async def on_mount(self) -> None:
        """Ambil metadata untuk membangun UI konfigurasi."""
        try:
            self.metadata = await self.app.api_client.get_dynamic_table_metadata(
                domain_id=self.metadata_source,
                var_id=self.var_id
            )

            await self.build_config_ui()
        except Exception as e:
            self.query_one("#builder-status").update(f"[bold red]Gagal memuat metadata: {e}[/]")
            self.query_one(LoadingIndicator).display = False
            self.app.notify(f"Error: {e}", title="Gagal Memuat Metadata", severity="error")

    async def build_config_ui(self) -> None:
        """Membangun UI konfigurasi secara dinamis berdasarkan metadata."""
        config_area = self.query_one("#config-area")

        # Hapus pesan loading dan tampilkan area konfigurasi
        self.query_one("#builder-status").remove()
        self.query_one(LoadingIndicator).display = False
        config_area.remove_class("hidden")
        self.query_one("#generate-table-button").disabled = False

        vertical_vars = self.metadata.get("vertical_vars", [])
        horizontal_vars = self.metadata.get("horizontal_vars", [])
        years = self.metadata.get("years", [])

        if vertical_vars:
            config_area.mount(Static("[bold]1. Pilih Variabel untuk Baris:[/bold]"))
            with RadioSet(id="vervar-radioset"):
                for var in vertical_vars:
                    yield RadioButton(var.get("label", ""), id=str(var.get("id", "")))

            for var in vertical_vars:
                items = var.get("items", [])
                container = Vertical(classes="hidden checkbox-group", id=f"vervar-items-{var.get('id')}")
                with container:
                    container.mount(Static(f"[bold]Pilih item untuk '{var.get('label')}':[/bold]"))
                    for item in items:
                        yield Checkbox(item.get("label", ""), id=str(item.get("id", "")))
                config_area.mount(container)

            first_var = vertical_vars[0]
            try:
                self.query_one(f"#vervar-items-{first_var.get('id')}").remove_class("hidden")
            except Exception:
                pass
            try:
                self.query_one("#vervar-radioset", RadioSet).focus()
            except Exception:
                pass

        if horizontal_vars:
            config_area.mount(Static("[bold]2. Pilih Variabel untuk Kolom (centang semua):[/bold]", classes="mt-1"))
            with Vertical(id="turvar-checkboxes"):
                for var in horizontal_vars:
                    yield Checkbox(var.get("label", ""), value=True, id=str(var.get("id", "")))

        if years:
            config_area.mount(Static("[bold]3. Pilih Tahun:[/bold]", classes="mt-1"))
            with RadioSet(id="year-radioset"):
                for year in years:
                    yield RadioButton(year.get("label", ""), id=str(year.get("id", "")))
            try:
                self.query_one("#year-radioset", RadioSet).pressed_index = 0
            except Exception:
                pass

    @on(RadioSet.Changed, "#vervar-radioset")
    def on_vertical_var_changed(self, event: RadioSet.Changed):
        """Tampilkan/sembunyikan grup checkbox yang sesuai."""
        for group in self.query(".checkbox-group"):
            group.add_class("hidden")

        selected_group_id = f"#vervar-items-{event.pressed.id}"
        if self.query(selected_group_id):
            self.query_one(selected_group_id).remove_class("hidden")

    @on(Button.Pressed, "#generate-table-button")
    async def generate_table(self) -> None:
        """Kumpulkan pilihan dan panggil API untuk mendapatkan data tabel."""
        loader = self.query_one("#preview-loader")
        table = self.query_one("#table-preview")

        table.clear(columns=True)
        loader.remove_class("hidden")
        self.last_df = None

        try:
            vervar_radioset = self.query_one("#vervar-radioset", RadioSet)
            year_radioset = self.query_one("#year-radioset", RadioSet)

            vervar_id = vervar_radioset.pressed_button.id if vervar_radioset.pressed_button else ""
            year_id = year_radioset.pressed_button.id if year_radioset.pressed_button else ""

            turvar_ids = []
            try:
                turvar_ids = [
                    cb.id for cb in self.query("#turvar-checkboxes Checkbox") if cb.value
                ]
            except Exception:
                pass

            vervar_item_group_id = f"#vervar-items-{vervar_id}"
            vervar_item_ids = []
            try:
                vervar_item_ids = [
                    cb.id for cb in self.query(f"{vervar_item_group_id} Checkbox") if cb.value
                ]
            except Exception:
                pass

            if not all([vervar_id, year_id, turvar_ids, vervar_item_ids]):
                 raise ValueError("Harap lengkapi semua pilihan sebelum menampilkan tabel.")

            df = await self.app.api_client.get_dynamic_table_data(
                domain_id=self.domain_id,
                var_id=self.var_id,
                vertical_var_id=vervar_id,
                year=year_id,
                horizontal_var_ids=turvar_ids,
                vertical_var_item_ids=vervar_item_ids,
                source_domain=self.metadata.get("source_domain", self.metadata_source),
            )

            self.last_df = df.copy()

            # Tampilkan data di DataTable
            table.add_columns(*df.columns.to_list())
            table.add_rows(df.astype(str).values.tolist())

            self.set_bindings({"d": Binding("download_table", "Download Tabel", show=True)})

        except Exception as e:
            self.app.notify(f"Gagal menampilkan tabel: {e}", title="Error", severity="error")
            table.add_column("Error")
            table.add_row(str(e))
        finally:
            loader.add_class("hidden")

    async def action_download_table(self) -> None:
        """Membuka dialog unduhan untuk tabel dinamis yang sudah dibuat."""
        if self.last_df is None or self.last_df.empty:
            self.app.notify("Tidak ada data untuk diunduh. Tampilkan tabel terlebih dahulu.",
                            title="Download Gagal", severity="error")
            return

        download_title = f"{self.title}_{self.var_id}"

        def download_callback(result):
            if result:
                filename, file_format = result
                self.run_worker(
                    self.perform_dynamic_download(self.last_df, filename, file_format),
                    exclusive=True
                )

        self.app.push_screen(
            DownloadDialogScreen(self.var_id, download_title),
            download_callback
        )

    async def perform_dynamic_download(self, df, filename: str, file_format: str) -> None:
        """Melakukan pekerjaan download yang sebenarnya dari DataFrame yang ada."""
        from pathlib import Path
        from stadata_x import config
        import asyncio

        self.app.notify(f"Menyiapkan unduhan ke {filename}...", title="Download Dimulai")

        try:
            df_clean = await self.app.api_client._clean_bps_dataframe(df)

            config_path = config.load_config().get("download_path")
            base_path = Path(config_path) if config_path and Path(config_path).is_dir() else Path.cwd()
            filepath = base_path / filename

            if filepath.exists():
                self.app.notify(f"File sudah ada, menimpa: {filepath}", severity="warning", title="File Exists")

            if file_format == "csv":
                await asyncio.to_thread(df_clean.to_csv, filepath, index=False, encoding='utf-8-sig')
            elif file_format == "xlsx":
                await asyncio.to_thread(df_clean.to_excel, filepath, index=False, engine='openpyxl')
            elif file_format == "json":
                await asyncio.to_thread(df_clean.to_json, filepath, orient="records", indent=4)

            self.app.notify(f"File disimpan di: {filepath}", title="Download Berhasil", severity="information")

        except Exception as e:
            self.app.notify(f"Gagal menyimpan file: {e}", title="Download Error", severity="error")
