"""
Generate QR code untuk setiap santri berdasarkan santri.csv.
QR berisi santri_id (contoh: S001) yang nantinya di-scan oleh pengajar
saat mencatat setoran murajaah/ziyadah.

Jalankan: python data/generate_qr_cards.py
Output: assets/qrcodes/<santri_id>.png + assets/qrcodes/kartu_santri.pdf (kartu cetak)
"""
import csv
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
QR_DIR = os.path.join(BASE_DIR, "assets", "qrcodes")
CARD_W, CARD_H = 650, 400


def load_santri():
    with open(os.path.join(BASE_DIR, "data", "santri.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def make_qr_image(payload: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def make_kartu_santri(santri: dict) -> Image.Image:
    """Buat kartu santri sederhana: nama + halaqah + QR code."""
    card = Image.new("RGB", (CARD_W, CARD_H), "white")
    draw = ImageDraw.Draw(card)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except OSError:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.rectangle([0, 0, CARD_W - 1, CARD_H - 1], outline="black", width=3)
    draw.rectangle([0, 0, CARD_W - 1, 60], fill="#1b5e20")
    draw.text((20, 15), "KARTU SANTRI - HAFALAN AL-QURAN", font=font_title, fill="white")

    qr_payload = santri["santri_id"]
    qr_img = make_qr_image(qr_payload).resize((220, 220))
    card.paste(qr_img, (CARD_W - 240, 100))

    draw.text((20, 90), f"Nama", font=font_body, fill="black")
    draw.text((20, 115), santri["nama"], font=font_title, fill="black")
    draw.text((20, 170), f"ID Santri : {santri['santri_id']}", font=font_body, fill="black")
    draw.text((20, 200), f"Halaqah   : {santri['halaqah']}", font=font_body, fill="black")
    draw.text((20, 230), f"Musyrif   : {santri['musyrif']}", font=font_body, fill="black")
    draw.text((20, 260), f"Target khatam: {santri['target_khatam_bulan']} bulan", font=font_body, fill="black")
    draw.text((20, CARD_H - 40), "Scan QR ini saat setoran murajaah/ziyadah", font=font_body, fill="#555555")

    return card


def main():
    os.makedirs(QR_DIR, exist_ok=True)
    santri_list = load_santri()

    for s in santri_list:
        kartu = make_kartu_santri(s)
        kartu.save(os.path.join(QR_DIR, f"kartu_{s['santri_id']}.png"))

    print(f"Generated {len(santri_list)} kartu santri (QR + kartu cetak) -> {QR_DIR}")


if __name__ == "__main__":
    main()
