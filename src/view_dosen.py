import tkinter as tk
from tkinter import messagebox, ttk
import random
import string
from ui_styles import (
    BG_COLOR, CARD_COLOR, TEXT_PRIMARY, TEXT_MUTED, SUCCESS_GREEN, 
    SUCCESS_GREEN_HOVER, WARNING_ORANGE, WARNING_ORANGE_HOVER, DANGER_RED, 
    DANGER_RED_HOVER, ACCENT_BLUE, ACCENT_BLUE_HOVER, FONT_BOLD, 
    buat_kartu, tambah_efek_hover
)

class DosenView(tk.Frame):
    def __init__(self, parent, controller, nama_dosen, nip_dosen):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.nip_dosen = nip_dosen
        self.kode_aktif = None
        self.kode_mk_aktif = None
        self.nama_mk_aktif = None

        wrapper = tk.Frame(self, bg=BG_COLOR)
        wrapper.pack(fill="both", expand=True, padx=40, pady=30)

        tk.Label(wrapper, text=f"Panel Dosen: {nama_dosen}", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, 15))

        card = buat_kartu(wrapper)
        card.pack(fill="x", expand=True, pady=(0, 15))

        tk.Label(card, text="PILIH MATA KULIAH", font=("Segoe UI", 8, "bold"), bg=CARD_COLOR, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        
        daftar_matkul = self.controller.db.ambil_matkul_dosen(nip_dosen)
        self.combo_mk = ttk.Combobox(card, values=daftar_matkul, state="readonly", font=("Segoe UI", 10))
        self.combo_mk.pack(fill="x", pady=(0, 20), ipady=6)
        if daftar_matkul:
            self.combo_mk.current(0)

        btn_gen = tk.Button(card, text="GENERATE KODE SESI (AKTIF SELAMANYA)", bg=SUCCESS_GREEN, fg="#ffffff", 
                            font=FONT_BOLD, relief="flat", cursor="hand2", command=self.aksi_generate)
        btn_gen.pack(fill="x", ipady=10, pady=(0, 15))
        tambah_efek_hover(btn_gen, SUCCESS_GREEN, SUCCESS_GREEN_HOVER)

        self.lbl_kode = tk.Label(card, text="KODE AKTIF: - - - - - - -", font=("Segoe UI", 15, "bold"), bg=CARD_COLOR, fg=WARNING_ORANGE)
        self.lbl_kode.pack(pady=5)

        btn_rekap = tk.Button(wrapper, text="Lihat Rekap Absensi Real-Time", bg=ACCENT_BLUE, fg="#ffffff", font=FONT_BOLD, relief="flat", cursor="hand2", command=self.aksi_rekap)
        btn_rekap.pack(fill="x", ipady=9, pady=4)
        tambah_efek_hover(btn_rekap, ACCENT_BLUE, ACCENT_BLUE_HOVER)

        btn_akhir = tk.Button(wrapper, text="Akhiri Sesi & Auto-Alpha", bg=WARNING_ORANGE, fg="#ffffff", font=FONT_BOLD, relief="flat", cursor="hand2", command=self.aksi_akhiri)
        btn_akhir.pack(fill="x", ipady=9, pady=4)
        tambah_efek_hover(btn_akhir, WARNING_ORANGE, WARNING_ORANGE_HOVER)

        btn_logout = tk.Button(wrapper, text="Keluar / Logout Akun", bg=DANGER_RED, fg="#ffffff", font=FONT_BOLD, relief="flat", cursor="hand2", command=self.controller.proses_logout)
        btn_logout.pack(fill="x", ipady=9, pady=(15, 0))
        tambah_efek_hover(btn_logout, DANGER_RED, DANGER_RED_HOVER)

    def aksi_generate(self):
        pilihan = self.combo_mk.get().strip()
        if not pilihan:
            messagebox.showerror("Error", "Pilih mata kuliah terlebih dahulu!")
            return
        
        parts = pilihan.split(" - ", 1)
        self.kode_mk_aktif = parts[0]
        self.nama_mk_aktif = parts[1] if len(parts) > 1 else ""

        self.kode_aktif = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        self.controller.db.simpan_sesi_aktif(self.nip_dosen, self.kode_aktif, self.kode_mk_aktif, self.nama_mk_aktif)
        
        self.lbl_kode.config(text=f"KODE AKTIF: {self.kode_aktif}")
        messagebox.showinfo("Berhasil", f"Sesi aktif dibuka untuk {self.nama_mk_aktif}!\nKode tidak akan kedaluwarsa sampai Anda mengakhirinya.")

    def aksi_rekap(self):
        if not self.kode_aktif:
            messagebox.showwarning("Peringatan", "Belum ada sesi yang di-generate!")
            return

        data_rekap = self.controller.db.ambil_rekap_sesi(self.kode_aktif)
        top = tk.Toplevel(self)
        top.title(f"Rekap: {self.nama_mk_aktif}")
        top.geometry("450x350")
        top.config(bg=BG_COLOR)
        
        tk.Label(top, text=f"Kehadiran: {self.nama_mk_aktif} ({self.kode_aktif})", font=FONT_BOLD, bg=BG_COLOR, fg=TEXT_PRIMARY).pack(pady=12)
        
        txt = tk.Text(top, width=48, height=15, bg=CARD_COLOR, fg=TEXT_PRIMARY, relief="flat", font=("Consolas", 9))
        txt.pack(padx=15, pady=5)
        
        if not data_rekap:
            txt.insert(tk.END, "Belum ada mahasiswa yang absen.")
        else:
            for idx, r in enumerate(data_rekap, 1):
                txt.insert(tk.END, f"{idx}. [{r.get('nim')}] {r.get('nama_mhs')} - {r.get('status')}\n")
        txt.config(state="disabled")

    def aksi_akhiri(self):
        if not self.kode_aktif:
            messagebox.showwarning("Peringatan", "Tidak ada sesi aktif saat ini.")
            return

        if messagebox.askyesno("Konfirmasi", f"Akhiri sesi {self.nama_mk_aktif}? Mahasiswa yang belum absen akan otomatis diberi status Alpha."):
            jml = self.controller.db.akhiri_sesi_dan_rekap_alpha(self.nip_dosen, self.kode_aktif, self.kode_mk_aktif, self.nama_mk_aktif)
            messagebox.showinfo("Selesai", f"Sesi ditutup. {jml} mahasiswa berhasil direkap Alpha.")
            self.controller.proses_logout()