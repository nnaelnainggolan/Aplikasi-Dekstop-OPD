"""Ubah gambar logo (PNG/JPG apa saja) menjadi icon.ico untuk OPD Automation Suite.

Cara pakai:
  1. Taruh gambar logo di folder ini, beri nama logo.png (atau logo.jpg).
     Sebaiknya persegi (mis. 512x512) dan latarnya tidak transparan kalau ingin
     tampil rapi di semua ukuran ikon Windows.
  2. Jalankan BUAT_IKON.bat.
  3. icon.ico akan dibuat di folder ini. Jalankan ulang BUILD_EXE.bat agar
     ikon baru ikut tertanam di .exe.
"""
from pathlib import Path
import sys

try:
    from PIL import Image
except ImportError:
    print("Pillow belum terpasang. BUAT_IKON.bat seharusnya memasangnya otomatis.")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
CANDIDATES = ["logo.png", "logo.jpg", "logo.jpeg", "logo.bmp"]
SIZES = [16, 24, 32, 48, 64, 128, 256]


def find_logo():
    for name in CANDIDATES:
        path = ROOT / name
        if path.is_file():
            return path
    return None


def main():
    source = find_logo()
    if not source:
        print("Tidak menemukan logo.png / logo.jpg / logo.jpeg / logo.bmp di folder ini.")
        print("Taruh gambar logo Anda di folder ini dengan salah satu nama tersebut, lalu jalankan lagi.")
        sys.exit(1)

    image = Image.open(source).convert("RGBA")
    if image.width != image.height:
        side = max(image.width, image.height)
        square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        square.paste(image, ((side - image.width) // 2, (side - image.height) // 2))
        image = square
        print(f"Catatan: {source.name} tidak persegi, ditengahkan otomatis ke kanvas {side}x{side}.")

    out = ROOT / "icon.ico"
    image.save(out, format="ICO", sizes=[(s, s) for s in SIZES])
    print(f"Berhasil: {out.name} dibuat dari {source.name} ({len(SIZES)} ukuran: {SIZES}).")
    print("Sekarang jalankan ulang BUILD_EXE.bat agar ikon baru ikut tertanam di .exe.")


if __name__ == "__main__":
    main()
