# stadata_x/api_client.py

import stadata
import asyncio
from pathlib import Path
import pandas as pd
from stadata_x import config
from pandas import DataFrame
from requests.exceptions import ConnectionError, HTTPError, Timeout
import time
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Any

class FileExistsError(Exception):
    """Exception kustom saat file yang akan didownload sudah ada."""
    def __init__(self, filepath):
        self.filepath = filepath
        super().__init__(f"File sudah ada di: {filepath}")

class ApiTokenError(Exception): pass
class BpsServerError(Exception): pass
class NoInternetError(Exception): pass

class BpsApiDataError(Exception):
    """Exception kustom saat API BPS mengembalikan data tak terduga."""
    pass

class ApiClient:
    """Kelas untuk berinteraksi dengan WebAPI BPS melalui stadata."""

    CACHE_FILE = config.CONFIG_DIR / "domain_cache.json"
    CACHE_DURATION = timedelta(days=7)

    def __init__(self, token: str | None = None):
        """
        Inisialisasi klien.

        Args:
            token (str | None): Jika disediakan, gunakan token ini.
                                Jika tidak, coba muat dari file konfigurasi.
        """
        self.token = token or config.load_token()
        self.client = None
        if self.token:
            try:
                self.client = stadata.Client(self.token)
            except Exception:
                self.client = None

    @property
    def is_ready(self) -> bool:
        """Mengecek apakah klien siap digunakan (token ada dan valid)."""
        return self.client is not None

    async def _api_call_with_retry(self, api_function: Callable[..., Any], *args, **kwargs):
        """
        Wrapper untuk memanggil fungsi API stadata dengan mekanisme retry.

        Args:
            api_function: Fungsi dari stadata.client yang akan dipanggil (misal: self.client.list_domain).
            *args, **kwargs: Argumen yang akan diteruskan ke api_function.
        """
        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                result = await asyncio.to_thread(api_function, *args, **kwargs)
                return result
            except HTTPError as e:
                if e.response.status_code == 429:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Rate limit terdeteksi. Mencoba lagi dalam {delay} detik...")
                        await asyncio.sleep(delay)
                        continue 
                raise
            except Exception:
                raise 

        raise BpsServerError("Gagal mengambil data setelah beberapa kali percobaan.")

    async def list_domains(self) -> DataFrame:
        """Mengambil daftar semua domain, menggunakan cache jika tersedia."""

        if self.CACHE_FILE.exists():
            try:
                cache_age = datetime.now() - datetime.fromtimestamp(self.CACHE_FILE.stat().st_mtime)
                if cache_age < self.CACHE_DURATION:
                    with open(self.CACHE_FILE, "r") as f:
                        data = json.load(f)
                    return pd.DataFrame(data)
            except (IOError, json.JSONDecodeError):
                pass

        if not self.is_ready:
            raise ApiTokenError("Token API tidak diatur.")

        try:
            df = await self._api_call_with_retry(self.client.list_domain)

            if not df.empty:
                config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                with open(self.CACHE_FILE, "w") as f:
                    df.to_json(f, orient="records", indent=4)

            return df

        except ConnectionError:
            raise NoInternetError("Tidak ada koneksi internet.")
        except HTTPError as e:
            if e.response.status_code == 401:
                raise ApiTokenError("Token API tidak valid.")
            elif e.response.status_code >= 500:
                raise BpsServerError("Server BPS sedang mengalami masalah.")
            else:
                raise 
        except Timeout:
            raise NoInternetError("Koneksi ke server BPS timeout.")

    async def list_static_tables(self, domain_id: str) -> DataFrame:
        """Mengambil daftar tabel statis untuk domain tertentu."""
        if not self.is_ready:
            raise ApiTokenError("Token API tidak diatur.")

        try:
            return await self._api_call_with_retry(
                self.client.list_statictable, domain=[domain_id]
            )
        except ConnectionError:
            raise NoInternetError("Tidak ada koneksi internet.")
        except HTTPError as e:
            if e.response.status_code == 401:
                raise ApiTokenError("Token API tidak valid.")
            elif e.response.status_code >= 500:
                raise BpsServerError("Server BPS sedang mengalami masalah.")
            else:
                raise 
        except Timeout:
            raise NoInternetError("Koneksi ke server BPS timeout.")

    async def view_static_table(self, domain_id: str, table_id: str) -> DataFrame:
        """Melihat isi tabel statis BPS dengan validasi output."""
        if not self.is_ready:
            raise ApiTokenError("Token API tidak diatur.")

        try:
            result = await self._api_call_with_retry(
                self.client.view_statictable, domain=domain_id, table_id=table_id
            )

            if not isinstance(result, pd.DataFrame):
                error_message = f"API BPS mengembalikan data tak terduga: {str(result)}"
                raise BpsApiDataError(error_message)

            return result
        except ConnectionError:
            raise NoInternetError("Tidak ada koneksi internet.")
        except HTTPError as e:
            if e.response.status_code == 401:
                raise ApiTokenError("Token API tidak valid.")
            elif e.response.status_code >= 500:
                raise BpsServerError("Server BPS sedang mengalami masalah.")
            else:
                raise 
        except Timeout:
            raise NoInternetError("Koneksi ke server BPS timeout.")

    async def download_table(
        self,
        domain_id: str,
        table_id: str,
        filename: str,
        format: str = "csv",
        overwrite: bool = False
    ) -> str:
        """Download tabel dan simpan dalam format yang dipilih."""
        if not self.is_ready:
            raise ApiTokenError("Token API tidak diatur.")

        df = await self.view_static_table(domain_id, table_id)
        if df.empty:
            raise Exception("Data tabel kosong atau tidak ditemukan")

        df_clean = await self._clean_bps_dataframe(df)

        config_path = config.load_config().get("download_path")
        if config_path and Path(config_path).is_dir():
            base_path = Path(config_path)
        else:
            base_path = Path.cwd()

        filepath = base_path / filename

        if filepath.exists() and not overwrite:
            raise FileExistsError(filepath)

        if format == "csv":
            await asyncio.to_thread(df_clean.to_csv, filepath, index=False, encoding='utf-8-sig')
        elif format == "xlsx":
            await asyncio.to_thread(df_clean.to_excel, filepath, index=False, engine='openpyxl')
        elif format == "json":
            await asyncio.to_thread(df_clean.to_json, filepath, orient="records", indent=4)
        else:
            raise ValueError(f"Format tidak didukung: {format}")

        return str(filepath)

    async def _clean_bps_dataframe(self, df) -> DataFrame:
        """Membersihkan DataFrame BPS agar lebih readable."""
        try:
            if isinstance(df.columns, pd.MultiIndex):
                new_columns = []
                for col in df.columns:
                    col_name = ' '.join(str(x) for x in col if pd.notna(x) and str(x) != 'nan')
                    new_columns.append(col_name.strip())

                df.columns = new_columns

            df.columns = [f"Unnamed_{i}" if col == "" or pd.isna(col) else str(col)
                         for i, col in enumerate(df.columns)]

            df = df.dropna(how='all')

            df = df.reset_index(drop=True)

            return df

        except Exception as e:
            return df
