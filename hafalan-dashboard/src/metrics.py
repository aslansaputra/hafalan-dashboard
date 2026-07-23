"""
Kalkulasi metrik progress hafalan dari data setoran.
"""
import pandas as pd
from datetime import date

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data"))
from quran_reference import TOTAL_AYAT_QURAN, get_surah_dataframe


def load_data(data_dir):
    santri = pd.read_csv(os.path.join(data_dir, "santri.csv"))
    setoran = pd.read_csv(os.path.join(data_dir, "setoran.csv"), parse_dates=["tanggal"])
    santri["tanggal_masuk"] = pd.to_datetime(santri["tanggal_masuk"])
    return santri, setoran


def total_ayat_per_santri(setoran: pd.DataFrame) -> pd.DataFrame:
    """Total ayat hafalan baru (ziyadah) per santri, plus jumlah murajaah."""
    ziyadah = setoran[setoran["jenis"] == "Ziyadah"].groupby("santri_id")["jumlah_ayat"].sum()
    murajaah = setoran[setoran["jenis"] == "Murajaah"].groupby("santri_id")["jumlah_ayat"].sum()
    df = pd.DataFrame({
        "total_ayat_ziyadah": ziyadah,
        "total_ayat_murajaah": murajaah,
    }).fillna(0).reset_index()
    df["persen_khatam"] = (df["total_ayat_ziyadah"] / TOTAL_AYAT_QURAN * 100).round(2)
    df["estimasi_juz"] = (df["total_ayat_ziyadah"] / TOTAL_AYAT_QURAN * 30).round(1)
    return df


def kecepatan_hafalan(setoran: pd.DataFrame, santri: pd.DataFrame) -> pd.DataFrame:
    """Rata-rata ayat ziyadah per minggu sejak tanggal masuk, per santri."""
    ziyadah = setoran[setoran["jenis"] == "Ziyadah"]
    total = ziyadah.groupby("santri_id")["jumlah_ayat"].sum().reset_index(name="total_ayat")
    merged = total.merge(santri[["santri_id", "tanggal_masuk", "target_khatam_bulan"]], on="santri_id", how="right").fillna(0)
    hari_aktif = (pd.Timestamp(date.today()) - merged["tanggal_masuk"]).dt.days.clip(lower=1)
    merged["ayat_per_minggu"] = (merged["total_ayat"] / hari_aktif * 7).round(1)

    sisa_ayat = TOTAL_AYAT_QURAN - merged["total_ayat"]
    minggu_tersisa = sisa_ayat / merged["ayat_per_minggu"].replace(0, pd.NA)
    minggu_tersisa = minggu_tersisa.replace([float("inf"), float("-inf")], pd.NA)
    merged["estimasi_minggu_khatam"] = minggu_tersisa.round(1)
    return merged[["santri_id", "total_ayat", "ayat_per_minggu", "estimasi_minggu_khatam", "target_khatam_bulan"]]


def rasio_konsistensi(setoran: pd.DataFrame, santri: pd.DataFrame) -> pd.DataFrame:
    """Rasio hari setor vs hari aktif sejak masuk (indikator kerajinan)."""
    hari_setor = setoran.groupby("santri_id")["tanggal"].nunique().reset_index(name="hari_setor")
    merged = santri[["santri_id", "tanggal_masuk"]].merge(hari_setor, on="santri_id", how="left").fillna(0)
    hari_aktif = (pd.Timestamp(date.today()) - merged["tanggal_masuk"]).dt.days.clip(lower=1)
    merged["hari_aktif"] = hari_aktif
    merged["persen_konsistensi"] = (merged["hari_setor"] / hari_aktif * 100).round(1).clip(upper=100)
    return merged[["santri_id", "hari_setor", "hari_aktif", "persen_konsistensi"]]


def progress_harian(setoran: pd.DataFrame, santri_id: str = None) -> pd.DataFrame:
    """Progress kumulatif ayat ziyadah dari waktu ke waktu (untuk grafik line)."""
    df = setoran[setoran["jenis"] == "Ziyadah"].copy()
    if santri_id:
        df = df[df["santri_id"] == santri_id]
    daily = df.groupby(["santri_id", "tanggal"])["jumlah_ayat"].sum().reset_index()
    daily = daily.sort_values(["santri_id", "tanggal"])
    daily["kumulatif_ayat"] = daily.groupby("santri_id")["jumlah_ayat"].cumsum()
    return daily


def rekap_halaqah(setoran: pd.DataFrame, santri: pd.DataFrame) -> pd.DataFrame:
    """Rekap total ayat per halaqah, untuk perbandingan kelompok."""
    merged = setoran[setoran["jenis"] == "Ziyadah"].merge(santri[["santri_id", "halaqah"]], on="santri_id")
    rekap = merged.groupby("halaqah")["jumlah_ayat"].sum().reset_index(name="total_ayat_ziyadah")
    rekap["rata2_persen_khatam"] = (rekap["total_ayat_ziyadah"] / TOTAL_AYAT_QURAN * 100).round(2)
    return rekap.sort_values("total_ayat_ziyadah", ascending=False)
