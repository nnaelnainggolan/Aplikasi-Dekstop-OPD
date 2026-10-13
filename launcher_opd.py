"""Launcher OPD Automation Suite.

Menu tunggal untuk memilih dan menjalankan salah satu dari tiga program yang
sudah ada, masing-masing di folder aslinya dan lewat file .bat aslinya:
  1. Capture Ruijie (ruijie-auto-report / 06_MULTI_PROJECT.bat)
  2. Drive Watcher  (ruijie-drive-v2 / START.bat)
  3. Audit OPD      (OPD_Audit_ / JALANKAN_AUDIT.bat)

Launcher ini TIDAK mengubah, menyalin, atau menjalankan ulang logika ketiga
program tersebut. Ia hanya membuka file .bat masing-masing di jendela
terminal baru, seperti diklik dua kali secara manual, lalu launcher tetap
terbuka agar bisa menjalankan program lain berikutnya.

Letakkan file ini SEJAJAR dengan ketiga folder proyek, misalnya:
  OPD Automation Suite\\
    launcher_opd.py
    LAUNCHER_OPD.bat
    ruijie-auto-report\\06_MULTI_PROJECT.bat
    ruijie-drive-v2\\START.bat
    OPD_Audit_\\JALANKAN_AUDIT.bat

Nama folder proyek boleh berbeda: sunting PROGRAMS di bawah jika perlu.
"""
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

if getattr(sys, "frozen", False):
    # Dibungkus PyInstaller (--onefile): __file__ menunjuk ke folder ekstraksi
    # sementara (_MEIxxxx), bukan lokasi .exe. sys.executable adalah yang benar.
    ROOT = Path(sys.executable).resolve().parent
else:
    ROOT = Path(__file__).resolve().parent

# Palet warna flat/modern.
BG = "#0f172a"          # latar jendela: slate gelap
CARD_BG = "#1e293b"     # latar kartu: slate lebih terang
CARD_HOVER = "#27364a"  # kartu saat disorot mouse
CARD_DISABLED = "#161f30"
TEXT_MAIN = "#f1f5f9"
TEXT_SUB = "#94a3b8"
TEXT_DISABLED = "#5b6577"
ACCENT_ERROR = "#f87171"
FOOTER = "#475569"

# name -> (folder proyek, nama file .bat, deskripsi singkat, ikon, warna aksen)
PROGRAMS = [
    {
        "label": "Capture Ruijie",
        "sub": "36 Project",
        "folder": "ruijie-auto-report",
        "bat": "06_MULTI_PROJECT.bat",
        "desc": "Login manual lalu ambil grafik 36 project dari Ruijie Cloud ke Excel.",
        "icon": "\U0001F4E1",  # satelit
        "accent": "#38bdf8",
    },
    {
        "label": "Drive Watcher",
        "sub": "OPD Automation v5",
        "folder": "ruijie-drive-v2",
        "bat": "START.bat",
        "desc": "Memantau folder screenshot lokal dan menyisipkannya ke Excel satu per satu.",
        "icon": "\U0001F4C1",  # folder
        "accent": "#34d399",
    },
    {
        "label": "Audit OPD",
        "sub": None,
        "folder": "OPD_Audit_",
        "bat": "JALANKAN_AUDIT.bat",
        "desc": "Memeriksa folder laporan Excel: slot mana yang masih kosong.",
        "icon": "\U0001F50D",  # kaca pembesar
        "accent": "#fbbf24",
    },
]

CREATE_NEW_CONSOLE = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)


def bat_path(program):
    return ROOT / program["folder"] / program["bat"]


def run_program(program):
    path = bat_path(program)
    if not path.is_file():
        messagebox.showerror(
            "Tidak ditemukan",
            f"{program['bat']} tidak ditemukan di:\n{path}\n\n"
            "Pastikan folder proyek berada sejajar dengan launcher ini "
            "dan namanya tidak diubah.",
        )
        return
    try:
        # Jendela terminal baru, seperti diklik dua kali langsung; launcher tidak menunggu.
        subprocess.Popen(
            ["cmd.exe", "/c", "start", "", "cmd.exe", "/k", str(path)],
            cwd=str(path.parent),
            creationflags=CREATE_NEW_CONSOLE,
        )
    except Exception as exc:  # tampilkan apa adanya, jangan sampai launcher ikut tertutup
        messagebox.showerror("Gagal menjalankan", f"{program['bat']} gagal dijalankan:\n{exc}")


def bind_recursive(widget, sequence, handler):
    widget.bind(sequence, handler)
    for child in widget.winfo_children():
        bind_recursive(child, sequence, handler)


def _recolor(widget, bg):
    try:
        widget.configure(bg=bg)
    except tk.TclError:
        pass
    for child in widget.winfo_children():
        _recolor(child, bg)


def build_card(parent, program):
    found = bat_path(program).is_file()
    bg = CARD_BG if found else CARD_DISABLED
    fg_title = TEXT_MAIN if found else TEXT_DISABLED
    fg_sub = TEXT_SUB if found else TEXT_DISABLED
    accent = program["accent"] if found else "#334155"

    outer = tk.Frame(parent, bg=BG)
    outer.pack(fill="x", padx=22, pady=7)

    # Kartu: baris aksen tipis di kiri + isi.
    card = tk.Frame(outer, bg=bg)
    card.pack(fill="x")
    tk.Frame(card, bg=accent, width=5).pack(side="left", fill="y")

    body = tk.Frame(card, bg=bg, padx=16, pady=13)
    body.pack(side="left", fill="both", expand=True)

    top_row = tk.Frame(body, bg=bg)
    top_row.pack(fill="x", anchor="w")
    tk.Label(top_row, text=program["icon"], font=("Segoe UI Emoji", 16), bg=bg, fg=fg_title).pack(side="left")
    title_box = tk.Frame(top_row, bg=bg)
    title_box.pack(side="left", padx=(10, 0), anchor="w")
    tk.Label(
        title_box, text=program["label"], font=("Segoe UI", 11, "bold"), bg=bg, fg=fg_title, anchor="w",
    ).pack(anchor="w")
    if program["sub"]:
        tk.Label(title_box, text=program["sub"], font=("Segoe UI", 8), bg=bg, fg=accent, anchor="w").pack(anchor="w")

    desc_text = program["desc"] if found else program["desc"] + "  \u2022  folder/.bat tidak ditemukan"
    desc_fg = fg_sub if found else ACCENT_ERROR
    tk.Label(
        body, text=desc_text, font=("Segoe UI", 8), bg=bg, fg=desc_fg, anchor="w", justify="left", wraplength=360,
    ).pack(fill="x", pady=(6, 0), anchor="w")

    if found:
        def on_enter(_event=None):
            for w in (card, body, top_row, title_box):
                w.configure(bg=CARD_HOVER)
            _recolor(body, CARD_HOVER)

        def on_leave(_event=None):
            for w in (card, body, top_row, title_box):
                w.configure(bg=bg)
            _recolor(body, bg)

        def on_click(_event=None):
            run_program(program)

        bind_recursive(card, "<Enter>", on_enter)
        bind_recursive(card, "<Leave>", on_leave)
        bind_recursive(card, "<Button-1>", on_click)
        card.configure(cursor="hand2")
        body.configure(cursor="hand2")

    return found


def build_ui():
    root = tk.Tk()
    root.title("OPD Automation - Launcher")
    root.geometry("440x430")
    root.minsize(440, 430)
    root.configure(bg=BG)

    header = tk.Frame(root, bg=BG)
    header.pack(fill="x", pady=(24, 4))
    tk.Label(header, text="OPD Automation Suite", font=("Segoe UI", 15, "bold"), bg=BG, fg=TEXT_MAIN).pack()
    tk.Label(
        header, text="Pilih program yang ingin dijalankan", font=("Segoe UI", 9), bg=BG, fg=TEXT_SUB,
    ).pack(pady=(2, 0))

    body = tk.Frame(root, bg=BG)
    body.pack(fill="both", expand=True, pady=(14, 0))

    missing = []
    for program in PROGRAMS:
        found = build_card(body, program)
        if not found:
            missing.append(program["folder"])

    footer = tk.Frame(root, bg=BG)
    footer.pack(fill="x", pady=(6, 16))
    if missing:
        tk.Label(
            footer, text="Folder tidak ditemukan: " + ", ".join(missing),
            font=("Segoe UI", 8), bg=BG, fg=ACCENT_ERROR,
        ).pack()
    else:
        tk.Label(footer, text=str(ROOT), font=("Segoe UI", 7), bg=BG, fg=FOOTER).pack()

    return root


if __name__ == "__main__":
    try:
        build_ui().mainloop()
    except Exception as exc:
        # Fallback bila Tkinter/tampilan bermasalah: tetap beri pesan yang jelas di terminal.
        print("Launcher gagal dibuka:", exc)
        sys.exit(1)
