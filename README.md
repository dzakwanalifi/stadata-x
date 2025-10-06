# STADATA-X

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/stadata-x.svg)](https://pypi.org/project/stadata-x/)
[![Tests](https://github.com/dzakwanalifi/stadata-x/actions/workflows/ci.yml/badge.svg)](https://github.com/dzakwanalifi/stadata-x/actions)
[![Code Coverage](https://codecov.io/gh/dzakwanalifi/stadata-x/branch/main/graph/badge.svg)](https://codecov.io/gh/dzakwanalifi/stadata-x)
[![GitHub Release](https://img.shields.io/github/v/release/dzakwanalifi/stadata-x)](https://github.com/dzakwanalifi/stadata-x/releases)

**Membuka Data Statistik Indonesia, Satu Perintah Sekaligus.**

`stadata-x` adalah sebuah aplikasi terminal (TUI) modern yang dirancang untuk menjelajahi, melihat, dan mengunduh data dari Badan Pusat Statistik (BPS) Indonesia secara interaktif. Dibangun dengan Python dan [Textual](https://github.com/textualize/textual), aplikasi ini menyediakan antarmuka yang cepat dan efisien untuk mengakses kekayaan data publik BPS langsung dari command line Anda.

Lupakan mengunduh file secara manual. Dengan `stadata-x`, Anda dapat dengan mudah menavigasi data berdasarkan wilayah, mencari tabel statistik, melihat pratinjau, dan mengunduhnya dalam berbagai format (CSV, Excel, JSON).

## 📸 Screenshots

### Layar Selamat Datang
![Layar Selamat Datang](assets/welcome-screen.png)

### Pemilihan Wilayah
![Pemilihan Wilayah](assets/region-selection.png)

---

## ✨ Fitur Utama

-   🎯 **Navigasi Interaktif**: Jelajahi data BPS berdasarkan wilayah (Provinsi/Kabupaten/Kota) melalui antarmuka yang responsif.
-   📊 **Pratinjau Tabel**: Lihat isi tabel statistik langsung di terminal sebelum mengunduh, dengan pewarnaan dan perataan kolom otomatis untuk keterbacaan maksimal.
-   📥 **Unduhan Multi-Format**: Unduh data yang Anda butuhkan dalam format CSV, Excel (.xlsx), atau JSON.
-   ⚙️ **Manajemen Konfigurasi**: Simpan Token API BPS dan atur folder unduhan default dengan mudah.
-   🔄 **Penanganan Error Cerdas**: Dilengkapi dengan mekanisme *retry* otomatis untuk mengatasi *rate limiting* API dan penanganan error koneksi yang tangguh.
-   🚀 **Caching**: Permintaan data yang sering diakses (seperti daftar wilayah) disimpan dalam cache untuk mempercepat waktu muat.
-   🎨 **Antarmuka Modern**: Pengalaman pengguna yang mulus dan modern di dalam terminal Anda.

## 📋 Persyaratan Sistem

-   **Python**: 3.9 atau yang lebih baru
-   **Terminal**: Terminal modern yang mendukung ANSI colors (Windows Terminal, iTerm2, GNOME Terminal, dll.)
-   **Token API BPS**: Diperlukan untuk mengakses data (gratis dari portal developer BPS)

## 📈 Status & Coverage

- ✅ **113 Tests Passed** - Test suite lengkap dengan coverage tinggi
- ✅ **Cross-platform** - Kompatibel Windows, Linux, dan macOS (Python 3.9-3.13)
- ✅ **CI/CD Active** - GitHub Actions dengan testing multi-platform
- ✅ **PyPI Published** - Tersedia untuk instalasi global via `pip install stadata-x`

## 🚀 Instalasi

Pastikan Anda memiliki Python 3.9 atau yang lebih baru. `stadata-x` dapat diinstal dengan mudah menggunakan `pip`, `pipx`, atau `uv`.

### Menggunakan `pipx` (Direkomendasikan)

`pipx` menginstal paket Python dalam lingkungan terisolasi, yang merupakan cara terbaik untuk menginstal aplikasi command-line.

```bash
pipx install stadata-x
```

### Menggunakan `pip`

```bash
pip install stadata-x
```

### Menggunakan `uv`

```bash
uv pip install stadata-x
```

### Verifikasi Instalasi

Setelah instalasi, verifikasi bahwa aplikasi terinstal dengan benar:

```bash
stadata-x --version
```

## 🔧 Troubleshooting

### Masalah Instalasi Umum

#### **1. Build Error dengan `lxml`**
**Error**: `fatal error C1083: Cannot open include file: 'libxml/xmlversion.h'`

**Solusi**:
```bash
# Gunakan wheel-only installation
pip install stadata-x --only-binary=all

# Atau gunakan uv
uv pip install stadata-x --only-binary=all
```

**Penjelasan**: `stadata-x` menggunakan `lxml>=6.0.0` yang sudah include libxml2 binaries.

#### **2. Python Version Compatibility**
**Error**: `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`

**Solusi**:
- Pastikan menggunakan Python 3.9 atau yang lebih baru
- `stadata-x` mendukung Python 3.9-3.13

#### **3. Permission Error (Windows)**
**Error**: `PermissionError: [Errno 13] Permission denied`

**Solusi**:
```bash
# Jalankan sebagai administrator atau gunakan virtual environment
python -m venv venv
venv\Scripts\activate
pip install stadata-x
```

#### **4. SSL/Connection Error**
**Error**: `ssl.SSLCertVerificationError` atau connection timeout

**Solusi**:
```bash
# Update pip dan certificates
pip install --upgrade pip certifi

# Atau gunakan HTTP instead HTTPS
pip install stadata-x --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

#### **5. Dependency Conflict**
**Error**: `ERROR: Cannot install stadata-x because these package versions have conflicting dependencies`

**Solusi**:
```bash
# Gunakan virtual environment terisolasi
python -m venv isolated_env
isolated_env\Scripts\activate
pip install stadata-x

# Atau gunakan pip-tools untuk resolve dependencies
pip install pip-tools
pip-compile --output-file=requirements.txt pyproject.toml
pip-sync
```

### Alternative Installation Methods

#### **Menggunakan Conda (Windows Recommended)**
```bash
# Install Miniconda atau Anaconda
# Buat environment baru
conda create -n stadata-env python=3.11
conda activate stadata-env

# Install package
pip install stadata-x
```

#### **Menggunakan pipx (Isolated Environment)**
```bash
pipx install stadata-x
```

#### **Manual Installation dari Source**
```bash
# Clone repository
git clone https://github.com/dzakwanalifi/stadata-x.git
cd stadata-x

# Install dengan uv
uv sync --dev
uv run stadata-x --version
```

### Debug dan Logging

#### **Enable Verbose Output**
```bash
# Untuk pip
pip install stadata-x -v

# Untuk uv
uv pip install stadata-x --verbose
```

#### **Check System Information**
```bash
# Python version
python --version

# pip version
pip --version

# OS information
python -c "import platform; print(platform.platform())"

# Check installed packages
pip list | grep -E "(stadata|lxml|textual)"
```

### Masalah Runtime

#### **API Token Error**
```
ApiTokenError: Token API tidak diatur
```

**Solusi**:
1. Jalankan `stadata-x`
2. Tekan `s` untuk Settings
3. Masukkan Token API BPS Anda
4. Test koneksi dengan tombol "Tes Koneksi"

#### **Network/Connection Error**
```
NoInternetError: Tidak ada koneksi internet
```

**Solusi**:
- Check koneksi internet
- Coba lagi dalam beberapa saat (rate limiting)
- Gunakan VPN jika diperlukan

#### **Cache Issues**
```bash
# Clear cache
# Windows
rmdir /s %USERPROFILE%\.stadata-x

# Linux/Mac
rm -rf ~/.stadata-x
```

### Getting Help

Jika masalah berlanjut:

1. **Check GitHub Issues**: https://github.com/dzakwanalifi/stadata-x/issues
2. **Create New Issue**: Sertakan:
   - Python version (`python --version`)
   - OS information
   - Full error traceback
   - Installation method used
3. **Contact**: dzakwan624@gmail.com

## ⚡ Quick Start

1. **Konfigurasi Token API BPS**:
   ```bash
   stadata-x
   # Tekan 's' untuk masuk ke pengaturan
   # Tempel token API BPS Anda
   ```

2. **Jelajahi Data**:
   ```bash
   stadata-x
   # Pilih wilayah → Pilih tabel → Lihat pratinjau → Unduh
   ```

## Konfigurasi Awal: API Key BPS

Untuk menggunakan aplikasi ini, Anda memerlukan Token API dari BPS. Token ini gratis dan berfungsi sebagai kunci untuk mengakses data.

#### Cara Mendapatkan Token API

1.  **Kunjungi Portal WebAPI BPS**: Buka [webapi.bps.go.id/developer/](https://webapi.bps.go.id/developer/).
2.  **Daftar/Masuk**: Buat akun baru atau masuk jika Anda sudah memilikinya.
3.  **Salin Token**: Setelah masuk, salin Token API yang ditampilkan di dashboard Anda.
4.  **Konfigurasi di `stadata-x`**:
    -   Jalankan aplikasi: `stadata-x`
    -   Tekan `s` untuk masuk ke menu Pengaturan.
    -   Tempel Token API Anda, lalu simpan.
    -   Gunakan tombol "Tes Koneksi" untuk memvalidasi token Anda.

## Penggunaan

Jalankan aplikasi dari terminal Anda:

```bash
stadata-x
```

### ⌨️ Navigasi Dasar

| Tombol | Fungsi |
|--------|--------|
| `↑/↓` atau `j/k` | Bergerak di dalam daftar |
| `Enter` | Pilih item (wilayah atau tabel) |
| `Escape` | Kembali ke level sebelumnya |
| `s` | Buka halaman Pengaturan |
| `d` | Buka dialog unduhan (saat di pratinjau tabel) |
| `q` | Keluar dari aplikasi |

### 📁 Struktur Proyek

```
stadata-x/
├── stadata_x/          # Kode aplikasi utama
│   ├── assets/         # CSS dan asset statis
│   ├── screens/        # Layar-layar aplikasi
│   ├── widgets/        # Komponen UI kustom
│   └── *.py            # Modul utama
├── assets/             # Screenshot dan gambar dokumentasi
├── .gitignore          # File yang diabaikan Git
├── LICENSE             # Lisensi MIT
├── pyproject.toml      # Konfigurasi proyek Python
└── README.md           # Dokumentasi ini
```

## 🤝 Kontribusi

Kontribusi, laporan bug, dan permintaan fitur sangat kami hargai! 🎉

### Cara Berkontribusi

1. **Fork** repositori ini
2. **Buat branch** untuk fitur Anda (`git checkout -b feature/AmazingFeature`)
3. **Commit** perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4. **Push** ke branch (`git push origin feature/AmazingFeature`)
5. **Buka Pull Request**

### Pengembangan Lokal

Untuk pengembangan lokal, kloning repositori dan instal dependensi:

```bash
git clone https://github.com/dzakwanalifi/stadata-x.git
cd stadata-x
pip install -e ".[dev]"
```

Jalankan aplikasi dalam mode pengembangan dengan *hot-reloading*:

```bash
textual run --dev stadata_x/main.py
```

### Panduan Pengembangan

-   Gunakan `ruff` untuk linting dan formatting
-   Ikuti konvensi penamaan PEP 8
-   Tambahkan docstring untuk fungsi baru
-   Update dokumentasi jika diperlukan

## 🙏 Acknowledgments

-   **Badan Pusat Statistik (BPS)** - Untuk menyediakan data publik yang berharga
-   **[Textual](https://github.com/textualize/textual)** - Framework TUI yang powerful
-   **[stadata](https://github.com/bps-statistics/stadata)** - Library Python resmi untuk API BPS

## 📞 Dukungan

Jika Anda mengalami masalah atau memiliki pertanyaan:

-   📧 **Email**: dzakwan624@gmail.com
-   🐛 **Issues**: [GitHub Issues](https://github.com/dzakwanalifi/stadata-x/issues)
-   📖 **Dokumentasi**: [README ini](README.md)

## 📄 Lisensi

Proyek ini dilisensikan di bawah [Lisensi MIT](LICENSE) - lihat file [LICENSE](LICENSE) untuk detail lebih lanjut.

---

<div align="center">

**Dibuat dengan ❤️ untuk komunitas data Indonesia**

⭐ Jika Anda menyukai proyek ini, berikan bintang di GitHub!

</div>
