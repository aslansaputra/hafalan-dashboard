# 📖 Dashboard Analitik Hafalan Al-Quran Santri

Dashboard analitik pembelajaran (learning analytics) untuk melacak progress hafalan
Al-Quran santri di pesantren/dayah — dilengkapi fitur **scan QR code** kartu santri
agar pengajar (musyrif) bisa langsung mencatat setoran murajaah/ziyadah dari HP/tablet.

> Project portofolio pribadi. Data yang digunakan adalah **data dummy** yang meniru
> struktur pencatatan hafalan pesantren pada umumnya.

## ✨ Fitur

- **Ringkasan Pesantren** — total progress, perbandingan antar halaqah, distribusi kualitas
  setoran, heatmap aktivitas harian
- **Progress Per Santri** — grafik kumulatif hafalan, kecepatan hafalan (ayat/minggu),
  estimasi waktu khatam berdasarkan kecepatan rata-rata
- **Input Setoran via Scan QR** — pengajar scan QR kartu santri lewat kamera, lalu input
  jenis setoran (ziyadah/murajaah), surah, jumlah ayat, dan kualitas bacaan
- **Generator Kartu Santri** — membuat kartu santri berisi QR code unik per santri, siap cetak

## 🖼️ Preview

| Ringkasan Pesantren | Kartu Santri (QR) |
|---|---|
| Grafik progress, heatmap, perbandingan halaqah | QR unik per santri untuk scan setoran |

*(tambahkan screenshot dashboard kamu di sini setelah dijalankan)*

## 🏗️ Struktur Data

- **Santri** — identitas, halaqah, musyrif pembimbing, target khatam
- **Setoran** — riwayat harian: jenis (*ziyadah*/*murajaah*), surah, jumlah ayat, kualitas bacaan
- **Referensi Al-Quran** — 114 surah, 30 juz, 6.236 ayat (`data/quran_reference.py`)

## 🚀 Cara Menjalankan

```bash
# 1. Clone & masuk folder
git clone <repo-url>
cd hafalan-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate data dummy (santri + riwayat setoran)
python data/generate_dummy_data.py

# 4. Generate kartu santri + QR code
python data/generate_qr_cards.py

# 5. Jalankan dashboard
streamlit run app/dashboard.py
```

Dashboard akan terbuka di `http://localhost:8501`.

> **Catatan scan QR:** fitur scan pakai `st.camera_input` (butuh izin kamera browser) dan
> `pyzbar` untuk decode. Di Linux, `pyzbar` butuh library sistem `libzbar0`
> (`sudo apt install libzbar0` jika belum ada).

## 📁 Struktur Project

```
hafalan-dashboard/
├── data/
│   ├── quran_reference.py       # referensi 114 surah/30 juz/jumlah ayat
│   ├── generate_dummy_data.py   # generator santri.csv & setoran.csv
│   ├── generate_qr_cards.py     # generator kartu santri + QR
│   ├── santri.csv                (hasil generate)
│   └── setoran.csv               (hasil generate)
├── src/
│   └── metrics.py               # kalkulasi progress, kecepatan, konsistensi
├── app/
│   └── dashboard.py             # aplikasi Streamlit (3 halaman)
├── assets/qrcodes/              # kartu santri + QR (hasil generate)
├── requirements.txt
└── README.md
```

## 🛠️ Tech Stack

- **Python** — Pandas untuk pengolahan data
- **Streamlit** — dashboard interaktif
- **Plotly** — visualisasi (bar, pie, line, heatmap)
- **qrcode + Pillow** — generate kartu santri & QR code
- **pyzbar** — decode QR dari kamera

## 💡 Pengembangan Selanjutnya

- Autentikasi login untuk musyrif
- Ekspor laporan progress ke PDF/Excel per santri
- Notifikasi santri yang tidak setor > N hari
- Prediksi risiko keterlambatan khatam pakai regresi sederhana

---
Data yang digunakan hanyalah data dummy, pengguna dapat menggunakan data yang relevan untuk menggunakan fiturnya dengan optimal.
