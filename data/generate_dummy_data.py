"""
Generator data dummy: santri, halaqah, dan riwayat setoran hafalan.
Struktur dibuat meniru pola pencatatan hafalan dayah/pesantren
(ziyadah = setoran hafalan baru, murajaah = mengulang hafalan lama).

Jalankan: python data/generate_dummy_data.py
Output: data/santri.csv, data/setoran.csv
"""
import csv
import random
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from quran_reference import SURAH_DATA

random.seed(42)

HALAQAH_LIST = ["Halaqah Al-Fatih", "Halaqah Ar-Rasyid", "Halaqah Al-Hafizh", "Halaqah An-Nur"]
MUSYRIF_LIST = ["Ust. Fauzan", "Ust. Ridwan", "Ustzh. Maryam", "Ust. Hafiz"]

NAMA_DEPAN = ["Ahmad", "Muhammad", "Fatih", "Rizky", "Fajar", "Aisyah", "Khadijah",
              "Zahra", "Hafiz", "Yusuf", "Ibrahim", "Salman", "Fatimah", "Hasan",
              "Husein", "Bilal", "Zaid", "Umar", "Sofia", "Nur"]
NAMA_BELAKANG = ["Al-Fatih", "Ramadhan", "Pratama", "Munawwar", "Siddiq", "Athallah",
                  "Nasution", "Hakim", "Al-Ghifari", "Mahendra"]


def generate_santri(n=40):
    santri = []
    for i in range(1, n + 1):
        santri.append({
            "santri_id": f"S{i:03d}",
            "nama": f"{random.choice(NAMA_DEPAN)} {random.choice(NAMA_BELAKANG)}",
            "halaqah": random.choice(HALAQAH_LIST),
            "musyrif": random.choice(MUSYRIF_LIST),
            "tanggal_masuk": (date(2025, 1, 1) + timedelta(days=random.randint(0, 180))).isoformat(),
            "target_khatam_bulan": random.choice([18, 24, 30, 36]),
        })
    return santri


def generate_setoran(santri_list, hari=180):
    """
    Simulasikan riwayat setoran harian per santri sejak tanggal masuk,
    dengan variasi kerajinan (sebagian santri konsisten, sebagian bolong-bolong).
    """
    setoran = []
    setoran_id = 1
    kualitas_opsi = ["Lancar", "Kurang Lancar", "Perlu Diulang"]
    kualitas_bobot = [0.65, 0.25, 0.10]

    for s in santri_list:
        tanggal_masuk = date.fromisoformat(s["tanggal_masuk"])
        # tingkat kerajinan acak per santri (0.4 - 0.95 peluang setor tiap hari aktif)
        kerajinan = random.uniform(0.4, 0.95)
        posisi_ayat_kumulatif = 0  # progress ziyadah dalam ayat kumulatif dari Al-Fatihah

        current = tanggal_masuk
        akhir = min(tanggal_masuk + timedelta(days=hari), date(2026, 7, 23))

        while current <= akhir:
            # skip hari jumat (libur setoran) - opsional
            if current.weekday() != 4 and random.random() < kerajinan:
                jenis = random.choices(["Ziyadah", "Murajaah"], weights=[0.4, 0.6])[0]
                jumlah_ayat = random.randint(1, 5) if jenis == "Ziyadah" else random.randint(5, 20)

                if jenis == "Ziyadah":
                    posisi_ayat_kumulatif += jumlah_ayat

                surah_info = _cari_surah(posisi_ayat_kumulatif if jenis == "Ziyadah"
                                          else random.randint(1, max(posisi_ayat_kumulatif, 1)))

                setoran.append({
                    "setoran_id": f"ST{setoran_id:05d}",
                    "santri_id": s["santri_id"],
                    "tanggal": current.isoformat(),
                    "jenis": jenis,
                    "surah": surah_info[1],
                    "juz": surah_info[3],
                    "jumlah_ayat": jumlah_ayat,
                    "kualitas": random.choices(kualitas_opsi, weights=kualitas_bobot)[0],
                    "musyrif": s["musyrif"],
                })
                setoran_id += 1
            current += timedelta(days=1)

    return setoran


def _cari_surah(posisi_ayat_kumulatif):
    kumulatif = 0
    for row in SURAH_DATA:
        kumulatif += row[2]
        if posisi_ayat_kumulatif <= kumulatif:
            return row
    return SURAH_DATA[-1]


def main():
    out_dir = os.path.dirname(__file__)
    santri_list = generate_santri(40)
    setoran_list = generate_setoran(santri_list, hari=200)

    with open(os.path.join(out_dir, "santri.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=santri_list[0].keys())
        writer.writeheader()
        writer.writerows(santri_list)

    with open(os.path.join(out_dir, "setoran.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=setoran_list[0].keys())
        writer.writeheader()
        writer.writerows(setoran_list)

    print(f"Generated {len(santri_list)} santri, {len(setoran_list)} catatan setoran")
    print(f"-> {out_dir}/santri.csv")
    print(f"-> {out_dir}/setoran.csv")


if __name__ == "__main__":
    main()
