# STADATA-X

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/stadata-x.svg)](https://badge.fury.io/py/stadata-x)

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

-   **Python**: 3.8 atau yang lebih baru
-   **Terminal**: Terminal modern yang mendukung ANSI colors (Windows Terminal, iTerm2, GNOME Terminal, dll.)
-   **Token API BPS**: Diperlukan untuk mengakses data (gratis dari portal developer BPS)

## 🚀 Instalasi

Pastikan Anda memiliki Python 3.8 atau yang lebih baru. `stadata-x` dapat diinstal dengan mudah menggunakan `pip` atau `pipx`.

### Menggunakan `pipx` (Direkomendasikan)

`pipx` menginstal paket Python dalam lingkungan terisolasi, yang merupakan cara terbaik untuk menginstal aplikasi command-line.

```bash
pipx install stadata-x
```

### Menggunakan `pip`

```bash
pip install stadata-x
```

### Verifikasi Instalasi

Setelah instalasi, verifikasi bahwa aplikasi terinstal dengan benar:

```bash
stadata-x --version
```

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
