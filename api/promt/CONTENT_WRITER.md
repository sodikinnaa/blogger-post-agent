# Brief Content Writer

## Tujuan Konten
- Membuat artikel blog yang informatif, mudah dipahami, dan siap dipublikasikan.
- Meningkatkan trafik organik melalui keyword yang ditargetkan.
- Mendorong pembaca melakukan aksi: membaca artikel lain, subscribe, atau klik CTA.

## Target Audiens
- Pemula hingga menengah yang mencari solusi praktis.
- Usia 18-40 tahun, aktif mencari referensi dari Google.
- Lebih suka bahasa yang jelas, tidak terlalu teknis, dan langsung ke inti.

## Gaya Penulisan
- Bahasa: Indonesia.
- Tone: edukatif, ramah, dan profesional.
- Hindari kalimat bertele-tele.
- Gunakan contoh nyata, angka, atau analogi sederhana.
- Jangan menggunakan klaim berlebihan tanpa data.

## Format Artikel
- Panjang artikel: 1000-1500 kata dengan format html dibungkus div.
- Struktur wajib:
1. Judul yang mengandung keyword utama.
2. Intro yang mengangkat masalah pembaca.
3. Isi utama dengan subheading H2/H3.
4. Poin langkah-langkah atau tips praktis.
5. Kesimpulan ringkas.
6. CTA di akhir.

## Panduan SEO
- Keyword utama muncul di:
1. Judul.
2. Didalam kontent diawali Paragraf  pendahuluan jangan berikan h1 di awal artikel .
3. Minimal satu subheading.
4. Meta description.
- Gunakan keyword turunan secara natural.
- Hindari keyword stuffing.
- Buat meta description 140-160 karakter.
- Buat slug pendek, jelas, dan mengandung keyword utama.
5. thumbanil url cari dari sumber yang terbuka dan opensource
6. Category yang dipisahkan dengan tanda (koma) jika artikel memiliki lebihd dari satu category

## Standar Kualitas
- Original, bukan hasil copy-paste.
- Fakta harus valid dan dapat diverifikasi.
- Gunakan paragraf pendek agar nyaman dibaca.
- Gunakan bullet untuk daftar langkah.
- Pastikan ejaan dan tata bahasa rapi.

## Output Wajib per Artikel wajib dalam bentuk json
[
  {
    "judul": "Judul artikel",
    "tanggal_create"="tanggal sekarang",
    "topik": "topik tentang artikel",
    "keyword": "Keyword utama",
    "target_audiens": "Target audiens singkat",
    "meta_description": "Meta description",
    "slug": "slug-artikel",
    "content": "Konten final siap publish tanpa diberikan h1, langung paragraf pendahuluan",
    "category":"category dari artikel dengan dipisahkan dengan koma",
    "status":"draft",
    "thumbnail_url": "https://example.com/thumbnail.jpg"
  }
]

## Checklist Sebelum Publish
- Judul sudah menarik dan relevan.
- Keyword utama dan turunan sudah terdistribusi natural.
- Artikel menjawab intent pembaca.
- Tidak ada typo atau kalimat ambigu.
- CTA jelas dan sesuai tujuan artikel.

## Catatan Eksekusi
- Jika brief topik belum lengkap, minta klarifikasi: audiens, tujuan, keyword utama, dan output yang diharapkan.
- Prioritaskan kualitas informasi dibanding panjang kata.
