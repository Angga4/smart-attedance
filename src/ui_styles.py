import tkinter as tk

BG_COLOR = "#0b0f19"
CARD_COLOR = "#131c2e"
BORDER_COLOR = "#1e293b"
TEXT_PRIMARY = "#f1f5f9"
TEXT_MUTED = "#94a3b8"
ACCENT_BLUE = "#6366f1"       
ACCENT_BLUE_HOVER = "#4f46e5"
SUCCESS_GREEN = "#10b981"
SUCCESS_GREEN_HOVER = "#059669"
WARNING_ORANGE = "#f59e0b"
WARNING_ORANGE_HOVER = "#d97706"
DANGER_RED = "#f43f5e"
DANGER_RED_HOVER = "#e11d48"
INPUT_BG = "#1e293b"

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 10)
FONT_BODY = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")

def buat_kartu(parent, padx=30, pady=25):
    """Membuat Card Container dengan sudut bersih bernuansa modern"""
    card = tk.Frame(parent, bg=CARD_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=padx, pady=pady)
    return card

def tambah_efek_hover(widget, warna_asal, warna_hover):
    """Efek halus saat kursor menyentuh tombol"""
    widget.bind("<Enter>", lambda e: widget.config(bg=warna_hover))
    widget.bind("<Leave>", lambda e: widget.config(bg=warna_asal))