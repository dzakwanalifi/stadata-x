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
import requests
from html import unescape

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

def handle_api_errors(func: Callable) -> Callable:
    """Decorator untuk menangani error umum dari API call."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.is_ready:
            raise ApiTokenError("Token API tidak diatur.")
        try:
            return await func(self, *args, **kwargs)
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
    return wrapper

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

    @handle_api_errors
    async def list_static_tables(self, domain_id: str) -> DataFrame:
        """Mengambil daftar tabel statis untuk domain tertentu."""
        return await self._api_call_with_retry(
            self.client.list_statictable, domain=[domain_id]
        )

    @handle_api_errors
    async def view_static_table(self, domain_id: str, table_id: str) -> DataFrame:
        """Melihat isi tabel statis BPS dengan validasi output."""
        result = await self._api_call_with_retry(
            self.client.view_statictable, domain=domain_id, table_id=table_id
        )

        print(f"DEBUG: API result type: {type(result)}")
        if hasattr(result, 'shape'):
            print(f"DEBUG: DataFrame shape: {result.shape}")
        elif isinstance(result, str):
            print(f"DEBUG: String result (first 200 chars): {result[:200]}")
        else:
            print(f"DEBUG: Other result type: {str(result)[:200]}")

        if not isinstance(result, pd.DataFrame):
            error_message = f"API BPS mengembalikan data tak terduga (tipe: {type(result).__name__}): {str(result)[:500]}"
            raise BpsApiDataError(error_message)

        if result.empty:
            raise BpsApiDataError("Tabel BPS kosong atau tidak tersedia")

        return result

    @handle_api_errors
    async def list_dynamic_tables(self, domain_id: str) -> DataFrame:
        """Mengambil daftar tabel dinamis untuk domain tertentu."""
        return await self._api_call_with_retry(
            self.client.list_dynamictable, domain=[domain_id]
        )

    @handle_api_errors
    async def get_dynamic_table_metadata(self, domain_id: str, var_id: str) -> dict:
        token = config.load_token()
        if not token:
            raise ApiTokenError("Token API tidak diatur.")

        base_url = "https://webapi.bps.go.id/v1/api/list"

        async def fetch_for_domain(target_domain: str) -> dict:
            params = {"domain": target_domain, "var": var_id, "key": token}

            async def fetch(model: str):
                response = await asyncio.to_thread(
                    requests.get,
                    base_url,
                    params={**params, "model": model},
                    timeout=30
                )
                response.raise_for_status()
                return response.json()

            vervar_json, turvar_json, th_json, turth_json = await asyncio.gather(
                fetch("vervar"),
                fetch("turvar"),
                fetch("th"),
                fetch("turth"),
            )

            def extract_list(data_json, mapping):
                if data_json.get("data-availability") != "available":
                    return []
                data = data_json.get("data", [])
                if isinstance(data, list) and len(data) == 2 and isinstance(data[1], list):
                    items = []
                    for item in data[1]:
                        new_item = {}
                        for src, dst in mapping.items():
                            if src in item:
                                new_item[dst] = item[src]
                        if new_item:
                            items.append(new_item)
                    return items
                return []

            vertical_vars = extract_list(vervar_json, {
                "item_ver_id": "id",
                "vervar": "label",
                "kode_ver_id": "code",
                "group_ver_id": "group",
                "name_group_ver_id": "group_name"
            })

            horizontal_vars = extract_list(turvar_json, {
                "turvar_id": "id",
                "turvar": "label",
                "group_turvar_id": "group",
                "name_group_turvar": "group_name"
            })

            years = extract_list(th_json, {
                "th_id": "id",
                "th": "label"
            })

            derived_years = extract_list(turth_json, {
                "turth_id": "id",
                "turth": "label",
                "group_turth_id": "group",
                "name_group_turth": "group_name"
            })

            for item in vertical_vars + horizontal_vars + years + derived_years:
                if "label" in item and isinstance(item["label"], str):
                    item["label"] = unescape(item["label"]).strip()

            return {
                "vertical_vars": vertical_vars,
                "horizontal_vars": horizontal_vars,
                "years": years,
                "derived_years": derived_years,
                "source_domain": target_domain,
            }

        metadata = await fetch_for_domain(domain_id)

        if (
            (not metadata["vertical_vars"] or not metadata["horizontal_vars"] or not metadata["years"])
            and domain_id != "0000"
        ):
            fallback_metadata = await fetch_for_domain("0000")
            if fallback_metadata["vertical_vars"] and fallback_metadata["horizontal_vars"] and fallback_metadata["years"]:
                metadata = fallback_metadata
                metadata["source_domain"] = "0000"

        if not metadata["vertical_vars"] or not metadata["horizontal_vars"] or not metadata["years"]:
            raise BpsApiDataError("Metadata tabel dinamis tidak tersedia untuk parameter tersebut.")

        return metadata

    @staticmethod
    def _decode_datacontent_key(key: str) -> dict:
        segments = {
            "domain": key[0:4],
            "year": key[4:6],
            "vertical_group": key[6:8],
            "vertical_item": key[8:13],
            "horizontal": key[13:16],
            "derived": key[16:19],
        }
        return segments

    @handle_api_errors
    async def get_dynamic_table_data(
        self,
        domain_id: str,
        var_id: str,
        vertical_var_id: str,
        year: str,
        horizontal_var_ids: list[str],
        vertical_var_item_ids: list[str],
        source_domain: str | None = None,
    ) -> DataFrame:
        token = config.load_token()
        if not token:
            raise ApiTokenError("Token API tidak diatur.")

        effective_domain = source_domain or domain_id

        params = {
            "model": "data",
            "domain": effective_domain,
            "var": var_id,
            "key": token,
            "th": year,
        }

        if vertical_var_id:
            params["vervar"] = vertical_var_id
        if horizontal_var_ids:
            params["turvar"] = ";".join(horizontal_var_ids)
        if vertical_var_item_ids:
            params["turth"] = ";".join(vertical_var_item_ids)

        response = await asyncio.to_thread(
            requests.get,
            "https://webapi.bps.go.id/v1/api/list",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()

        if result.get("data-availability") != "available":
            raise BpsApiDataError("Data tabel dinamis tidak tersedia untuk parameter tersebut.")

        datacontent = result.get("datacontent")
        if not isinstance(datacontent, dict):
            raise BpsApiDataError("Respons API tidak mengandung datacontent yang valid.")

        records = []
        for key, value in datacontent.items():
            decoded = self._decode_datacontent_key(key)
            decoded["value"] = value
            decoded["raw_key"] = key
            records.append(decoded)

        df = pd.DataFrame(records)
        if df.empty:
            raise BpsApiDataError("Data tabel dinamis kosong.")

        return df

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
