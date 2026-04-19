# Blogger Post CLI

CLI Python untuk generate artikel dengan OpenAI lalu mempostingnya langsung ke Blogger.

## Fitur

- Cek status credential Blogger
- Generate artikel menggunakan system prompt dari `promt/CONTENT_WRITER.md`
- Auto post hasil generate ke Blogger
- Response terstruktur dengan `status`, `message`, `data`, dan `meta`

## Struktur Singkat

```text
cli.py
api/
  blogger.py
  openai.py
  config/
    app.py
  credential/
    blogs/
promt/
  CONTENT_WRITER.md
env.example
requirement.txt
```

## Kebutuhan

- Windows
- Python 3.10+
- Akun OpenAI atau endpoint OpenAI-compatible
- Blogger API OAuth client secret (`secret.json`)

## Instalasi

1. Buat virtual environment.

```powershell
py -m venv .venv
```

2. Aktifkan virtual environment.

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependency.

```powershell
python -m pip install -r .\requirement.txt
```

## Konfigurasi Environment

Salin `env.example` menjadi `.env`, lalu isi nilainya.

```env
OPENAI_API_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key_here
BLOG_ID=your_blog_id_here
```

Keterangan:

- `OPENAI_API_URL`: base URL OpenAI atau endpoint kompatibel
- `OPENAI_API_KEY`: API key untuk model
- `BLOG_ID`: ID blog target Blogger

## Konfigurasi Credential Blogger

Simpan file OAuth client secret Google sebagai:

```text
api/credential/blogs/secret.json
```

Saat pertama kali otorisasi berhasil, file storage akan dibuat otomatis di:

```text
api/credential/blogs/credentials.storage
```

## Menjalankan CLI

```powershell
python .\cli.py
```

Menu yang tersedia:

1. `Cek status Blogger credential`
2. `Generate artikel`
3. `q` untuk keluar

## Alur Generate Artikel

Saat memilih `Generate artikel`, aplikasi akan:

1. Membaca system prompt dari `promt/CONTENT_WRITER.md`
2. Mengirim prompt user ke OpenAI
3. Mengambil hasil JSON artikel
4. Mengubah hasil menjadi payload Blogger
5. Memposting artikel ke Blogger secara otomatis

Field hasil AI yang diharapkan:

```json
[
  {
    "title": "Judul artikel",
    "meta_description": "Meta description",
    "content": "Konten HTML artikel",
    "labels": ["category1", "category2"],
    "status": "DRAFT",
    "thumbnail_url": "https://example.com/image.jpg"
  }
]
```

Catatan:

- `status` akan dinormalisasi sebelum dikirim ke Blogger
- `publish` atau `published` dipetakan ke `LIVE`
- `meta_description` saat ini disisipkan sebagai komentar HTML di konten karena Blogger API tidak menyediakan field meta description resmi pada `posts.insert`

## Dependency

Isi `requirement.txt` saat ini:

- `openai`
- `google-api-python-client`
- `oauth2client`
- `httplib2`

## Build Menjadi EXE

Build paling aman saat ini memakai `PyInstaller` mode `onedir`.

1. Install PyInstaller.

```powershell
python -m pip install pyinstaller
```

2. Build aplikasi.

```powershell
pyinstaller --name BloggerPost --onedir --console --add-data "promt;promt" cli.py
```

3. Hasil build ada di folder `dist/BloggerPost`.

Setelah build, pastikan file berikut tersedia di hasil distribusi:

- `.env`
- `api/credential/blogs/secret.json`
- `api/credential/blogs/credentials.storage` jika sudah pernah login

## Troubleshooting

### Credential Blogger belum siap

Pastikan file berikut ada:

```text
api/credential/blogs/secret.json
```

Lalu jalankan opsi `1. Cek status Blogger credential`.

### BLOG_ID belum diatur

Isi nilai `BLOG_ID` di file `.env`.

### Status post ditolak Blogger

Gunakan status berikut:

- `DRAFT`
- `LIVE`
- `SCHEDULED`

## Pengembangan Lanjutan

Beberapa pengembangan yang masuk akal:

- Tambah konfirmasi sebelum publish
- Simpan hasil generate ke file atau database
- Tambah workflow CI/CD untuk build artifact `.exe`
- Rapikan resource path agar lebih aman untuk PyInstaller `--onefile`
