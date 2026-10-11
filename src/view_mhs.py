import tkinter as tk
from tkinter import messagebox
from ui_styles import (
    BG_COLOR, CARD_COLOR, TEXT_PRIMARY, TEXT_MUTED, INPUT_BG, 
    BORDER_COLOR, SUCCESS_GREEN, SUCCESS_GREEN_HOVER, DANGER_RED, 
    DANGER_RED_HOVER, WARNING_ORANGE, FONT_BOLD, buat_kartu, 
    tambah_efek_hover
)

class MahasiswaView(tk.Frame):
    def __init__(self, parent, controller, nama_mhs, nim_mhs):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.nama_mhs = nama_mhs
        self.nim_mhs = nim_mhs

        wrapper = tk.Frame(self, bg=BG_COLOR)
        wrapper.pack(fill="both", expand=True, padx=40, pady=30)

        tk.Label(wrapper, text=f"Selamat Datang, {self.nama_mhs}", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, 15))

        card = buat_kartu(wrapper)
        card.pack(fill="x", expand=True, pady=(0, 15))

        tk.Label(card, text="KODE ABSENSI (7 DIGIT DARI DOSEN)", font=("Segoe UI", 8, "bold"), bg=CARD_COLOR, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        self.entry_kode = tk.Entry(card, font=("Segoe UI", 16, "bold"), bg=INPUT_BG, fg=WARNING_ORANGE, insertbackground=TEXT_PRIMARY, relief="flat", justify="center", highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.entry_kode.pack(ipady=8, fill="x", pady=(0, 20))

        tk.Label(card, text="STATUS KEHADIRAN", font=("Segoe UI", 8, "bold"), bg=CARD_COLOR, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        self.status_var = tk.StringVar(value="Hadir")
        f_stat = tk.Frame(card, bg=CARD_COLOR)
        f_stat.pack(anchor="w", pady=(0, 15))

        for st in ["Hadir", "Izin", "Sakit"]:
            tk.Radiobutton(f_stat, text=st, variable=self.status_var, value=st, 
                           bg=CARD_COLOR, fg=TEXT_PRIMARY, selectcolor=INPUT_BG, 
                           activebackground=CARD_COLOR, activeforeground=TEXT_PRIMARY, cursor="hand2").pack(side=tk.LEFT, padx=(0, 20))

        btn_kirim = tk.Button(card, text="KIRIM KEHADIRAN", bg=SUCCESS_GREEN, fg="#ffffff", 
                              font=FONT_BOLD, relief="flat", cursor="hand2", command=self.aksi_kirim)
        btn_kirim.pack(fill="x", ipady=10, pady=(5, 0))
        tambah_efek_hover(btn_kirim, SUCCESS_GREEN, SUCCESS_GREEN_HOVER)

        btn_logout = tk.Button(wrapper, text="Keluar / Logout Akun", bg=DANGER_RED, fg="#ffffff", font=FONT_BOLD, relief="flat", cursor="hand2", command=self.controller.proses_logout)
        btn_logout.pack(fill="x", ipady=9, pady=(10, 0))
        tambah_efek_hover(btn_logout, DANGER_RED, DANGER_RED_HOVER)

    def aksi_kirim(self):
        kode_sesi = self.entry_kode.get().strip().upper()
        status = self.status_var.get()

        if len(kode_sesi) != 7:
            messagebox.showerror("Gagal", "Kode absensi harus tepat 7 digit!")
            return

        info = self.controller.db.ambil_info_sesi_dari_kode(kode_sesi)
        if not info:
            messagebox.showerror("Gagal", "Kode sesi tidak valid atau dosen telah menutup sesi ini!")
            return

        if self.controller.db.cek_sudah_absen_sesi(self.nim_mhs, kode_sesi):
            messagebox.showerror("Gagal", f"Anda sudah pernah mengirim presensi untuk matkul {info['nama_mk']} pada sesi ini!")
            return

        sukses = self.controller.db.simpan_absensi(self.nim_mhs, self.nama_mhs, info["kode_mk"], kode_sesi, status)
        if sukses:
            messagebox.showinfo("Sukses", f"Presensi [{status}] berhasil dicatat ke sistem!")
            self.controller.proses_logout()
        else:
            messagebox.showerror("Error", "Gagal menyimpan ke database online.")