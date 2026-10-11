import tkinter as tk
from tkinter import messagebox
from ui_styles import (
    BG_COLOR, CARD_COLOR, TEXT_PRIMARY, TEXT_MUTED, ACCENT_BLUE, 
    ACCENT_BLUE_HOVER, INPUT_BG, BORDER_COLOR, FONT_SUBTITLE, 
    FONT_BODY, FONT_BOLD, buat_kartu, tambah_efek_hover
)

class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        wrapper = tk.Frame(self, bg=BG_COLOR)
        wrapper.pack(fill="both", expand=True, padx=40, pady=30)

        tk.Label(wrapper, text="SMART ATTENDANCE", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_PRIMARY).pack(pady=(15, 5))
        tk.Label(wrapper, text="Sistem Presensi Akademik Terintegrasi", font=FONT_SUBTITLE, bg=BG_COLOR, fg=TEXT_MUTED).pack(pady=(0, 25))

        card = buat_kartu(wrapper)
        card.pack(fill="x", expand=True)

        tk.Label(card, text="PILIH STATUS PENGGUNA", font=("Segoe UI", 8, "bold"), bg=CARD_COLOR, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 8))
        
        self.role_var = tk.StringVar(value="Mahasiswa")
        frame_radio = tk.Frame(card, bg=CARD_COLOR)
        frame_radio.pack(anchor="w", pady=(0, 20))
        
        for r_val in ["Mahasiswa", "Dosen"]:
            tk.Radiobutton(frame_radio, text=r_val, variable=self.role_var, value=r_val, 
                           bg=CARD_COLOR, fg=TEXT_PRIMARY, selectcolor=INPUT_BG, 
                           activebackground=CARD_COLOR, activeforeground=TEXT_PRIMARY,
                           font=FONT_BODY, cursor="hand2").pack(side=tk.LEFT, padx=(0, 30))

        tk.Label(card, text="NIM / NIP (USERNAME)", font=("Segoe UI", 8, "bold"), bg=CARD_COLOR, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        self.entry_user = tk.Entry(card, font=FONT_BODY, bg=INPUT_BG, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, relief="flat", highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.entry_user.pack(ipady=8, fill="x", pady=(0, 15))

        tk.Label(card, text="PASSWORD", font=("Segoe UI", 8, "bold"), bg=CARD_COLOR, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        self.entry_pass = tk.Entry(card, font=FONT_BODY, show="•", bg=INPUT_BG, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, relief="flat", highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.entry_pass.pack(ipady=8, fill="x", pady=(0, 25))

        self.btn_login = tk.Button(card, text="MASUK KE SISTEM", bg=ACCENT_BLUE, fg="#ffffff", 
                                   font=FONT_BOLD, relief="flat", cursor="hand2", command=self.proses_login)
        self.btn_login.pack(fill="x", ipady=10)
        tambah_efek_hover(self.btn_login, ACCENT_BLUE, ACCENT_BLUE_HOVER)

    def proses_login(self):
        role = self.role_var.get()
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showerror("Peringatan", "Username dan Password wajib diisi!")
            return

        self.btn_login.config(text="Memeriksa Kredensial...", state="disabled")
        self.update_idletasks()

        berhasil, pesan_nama = self.controller.db.verifikasi_login(username, password, role)

        if berhasil:
            self.controller.logged_in_user = username
            if role == "Dosen":
                self.controller.tampilkan_dosen(pesan_nama, username)
            else:
                self.controller.tampilkan_mhs(pesan_nama, username)
        else:
            messagebox.showerror("Login Gagal", pesan_nama)
            self.btn_login.config(text="MASUK KE SISTEM", state="normal")