"""
Dashboard Learning Analytics - Progress Hafalan Al-Quran Santri
Jalankan: streamlit run app/dashboard.py
"""
import os
import sys
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src import metrics
from data.quran_reference import SURAH_DATA

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

st.set_page_config(page_title="Dashboard Hafalan Santri", page_icon="\U0001F4D6", layout="wide")


@st.cache_data(ttl=5)
def load_all():
    santri, setoran = metrics.load_data(DATA_DIR)
    return santri, setoran


def catat_setoran(santri_id, jenis, surah, jumlah_ayat, kualitas, musyrif):
    juz = next((row[3] for row in SURAH_DATA if row[1] == surah), 1)
    new_id = f"ST{int(date.today().strftime('%y%m%d%H%M%S'))}"
    row = {
        "setoran_id": new_id,
        "santri_id": santri_id,
        "tanggal": date.today().isoformat(),
        "jenis": jenis,
        "surah": surah,
        "juz": juz,
        "jumlah_ayat": jumlah_ayat,
        "kualitas": kualitas,
        "musyrif": musyrif,
    }
    path = os.path.join(DATA_DIR, "setoran.csv")
    df = pd.DataFrame([row])
    df.to_csv(path, mode="a", header=False, index=False)
    st.cache_data.clear()


# ---------- Sidebar navigasi ----------
st.sidebar.title("\U0001F4D6 Hafalan Dashboard")
page = st.sidebar.radio("Menu", ["Ringkasan Pesantren", "Progress Per Santri", "Input Setoran (Scan QR)"])

santri_df, setoran_df = load_all()

# ================= HALAMAN 1: RINGKASAN =================
if page == "Ringkasan Pesantren":
    st.title("Ringkasan Progress Hafalan Al-Quran")

    total_ayat = metrics.total_ayat_per_santri(setoran_df)
    konsistensi = metrics.rasio_konsistensi(setoran_df, santri_df)
    rekap_halaqah = metrics.rekap_halaqah(setoran_df, santri_df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Santri", len(santri_df))
    col2.metric("Total Setoran Tercatat", len(setoran_df))
    col3.metric("Rata-rata Progress Khatam", f"{total_ayat['persen_khatam'].mean():.1f}%")
    col4.metric("Rata-rata Konsistensi", f"{konsistensi['persen_konsistensi'].mean():.0f}%")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Perbandingan Progress Antar Halaqah")
        fig = px.bar(rekap_halaqah, x="halaqah", y="total_ayat_ziyadah",
                     text="rata2_persen_khatam", color="halaqah")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Distribusi Kualitas Setoran")
        kualitas_count = setoran_df["kualitas"].value_counts().reset_index()
        kualitas_count.columns = ["kualitas", "jumlah"]
        fig2 = px.pie(kualitas_count, names="kualitas", values="jumlah", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Heatmap Aktivitas Setoran (per hari, 30 hari terakhir)")
    recent = setoran_df[setoran_df["tanggal"] >= (pd.Timestamp.today() - pd.Timedelta(days=30))]
    heat = recent.groupby([recent["tanggal"].dt.date, "santri_id"]).size().reset_index(name="jumlah_setoran")
    if not heat.empty:
        pivot = heat.pivot(index="santri_id", columns="tanggal", values="jumlah_setoran").fillna(0)
        fig3 = px.imshow(pivot, aspect="auto", color_continuous_scale="Greens",
                          labels=dict(color="Jml Setoran"))
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Tabel Progress Seluruh Santri")
    tabel = santri_df.merge(total_ayat, on="santri_id", how="left").merge(
        konsistensi[["santri_id", "persen_konsistensi"]], on="santri_id", how="left")
    st.dataframe(
        tabel[["santri_id", "nama", "halaqah", "persen_khatam", "estimasi_juz", "persen_konsistensi"]]
        .sort_values("persen_khatam", ascending=False),
        use_container_width=True, hide_index=True,
    )

# ================= HALAMAN 2: PROGRESS PER SANTRI =================
elif page == "Progress Per Santri":
    st.title("Progress Individual Santri")

    pilihan = st.selectbox("Pilih Santri", santri_df["santri_id"] + " - " + santri_df["nama"])
    santri_id = pilihan.split(" - ")[0]
    info = santri_df[santri_df["santri_id"] == santri_id].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Halaqah", info["halaqah"])
    col2.metric("Musyrif", info["musyrif"])
    col3.metric("Target Khatam", f"{info['target_khatam_bulan']} bulan")

    kecepatan = metrics.kecepatan_hafalan(setoran_df, santri_df)
    row = kecepatan[kecepatan["santri_id"] == santri_id].iloc[0]

    col4, col5, col6 = st.columns(3)
    col4.metric("Total Ayat Ziyadah", int(row["total_ayat"]))
    col5.metric("Kecepatan Hafalan", f"{row['ayat_per_minggu']} ayat/minggu")
    estimasi = row["estimasi_minggu_khatam"]
    col6.metric("Estimasi Khatam", f"{estimasi:.0f} minggu lagi" if pd.notna(estimasi) else "-")

    st.subheader("Grafik Progress Kumulatif Hafalan")
    progress = metrics.progress_harian(setoran_df, santri_id)
    if not progress.empty:
        fig = px.line(progress, x="tanggal", y="kumulatif_ayat", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data ziyadah untuk santri ini.")

    st.subheader("Riwayat Setoran Terbaru")
    riwayat = setoran_df[setoran_df["santri_id"] == santri_id].sort_values("tanggal", ascending=False).head(15)
    st.dataframe(riwayat[["tanggal", "jenis", "surah", "jumlah_ayat", "kualitas", "musyrif"]],
                 use_container_width=True, hide_index=True)

# ================= HALAMAN 3: INPUT SETORAN VIA SCAN QR =================
elif page == "Input Setoran (Scan QR)":
    st.title("Input Setoran - Scan QR Kartu Santri")
    st.caption("Pengajar scan QR kartu santri (atau upload foto QR), lalu isi detail setoran.")

    if "scanned_id" not in st.session_state:
        st.session_state.scanned_id = None

    tab_camera, tab_manual = st.tabs(["\U0001F4F7 Scan Kamera", "\u270D\uFE0F Pilih Manual"])

    with tab_camera:
        img_file = st.camera_input("Arahkan kamera ke QR code kartu santri")
        if img_file is not None:
            from PIL import Image
            from pyzbar import pyzbar
            image = Image.open(img_file)
            hasil = pyzbar.decode(image)
            if hasil:
                kode = hasil[0].data.decode("utf-8")
                if kode in santri_df["santri_id"].values:
                    st.session_state.scanned_id = kode
                    st.success(f"QR terbaca: {kode}")
                else:
                    st.error(f"Kode '{kode}' tidak ditemukan di data santri.")
            else:
                st.warning("QR code belum terbaca, coba lagi dengan pencahayaan lebih baik.")

    with tab_manual:
        manual_pilihan = st.selectbox("Atau pilih santri manual",
                                       ["-"] + list(santri_df["santri_id"] + " - " + santri_df["nama"]))
        if manual_pilihan != "-":
            st.session_state.scanned_id = manual_pilihan.split(" - ")[0]

    st.divider()

    if st.session_state.scanned_id:
        santri_id = st.session_state.scanned_id
        info = santri_df[santri_df["santri_id"] == santri_id].iloc[0]
        st.info(f"**Santri terpilih:** {info['nama']} ({santri_id}) - {info['halaqah']}")

        with st.form("form_setoran"):
            c1, c2 = st.columns(2)
            jenis = c1.radio("Jenis Setoran", ["Ziyadah", "Murajaah"], horizontal=True)
            kualitas = c2.selectbox("Kualitas Bacaan", ["Lancar", "Kurang Lancar", "Perlu Diulang"])
            surah = st.selectbox("Surah", [row[1] for row in SURAH_DATA])
            jumlah_ayat = st.number_input("Jumlah Ayat", min_value=1, max_value=50, value=5)
            musyrif = st.text_input("Nama Musyrif/Pengajar", value=info["musyrif"])
            submitted = st.form_submit_button("Simpan Setoran", use_container_width=True, type="primary")

            if submitted:
                catat_setoran(santri_id, jenis, surah, jumlah_ayat, kualitas, musyrif)
                st.success(f"Setoran {jenis} untuk {info['nama']} berhasil dicatat!")
                st.session_state.scanned_id = None
                st.rerun()
    else:
        st.info("Scan QR kartu santri atau pilih manual di atas untuk mulai input setoran.")
