import tkinter as tk
import atexit
import signal
import sys
from database import DatabaseOnline
from ui_styles import BG_COLOR
from view_login import LoginView
from view_dosen import DosenView
from view_mhs import MahasiswaView

class AplikasiUtama(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Attendance System - Modern UI")
        self.geometry("480x540")
        self.config(bg=BG_COLOR)
        self.resizable(False, False)

        self.db = DatabaseOnline()
        self.logged_in_user = None

        atexit.register(self.darurat_exit_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        self.protocol("WM_DELETE_WINDOW", self.on_close_app)

        self.container = tk.Frame(self, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)

        self.tampilkan_login()

    def ganti_view(self, view_class, *args):
        for widget in self.container.winfo_children():
            widget.destroy()
        view = view_class(self.container, self, *args)
        view.pack(fill="both", expand=True)

    def tampilkan_login(self):
        self.logged_in_user = None
        self.ganti_view(LoginView)

    def tampilkan_dosen(self, nama, nip):
        self.ganti_view(DosenView, nama, nip)

    def tampilkan_mhs(self, nama, nim):
        self.ganti_view(MahasiswaView, nama, nim)

    def proses_logout(self):
        if self.logged_in_user:
            try:
                self.db.tutup_semua_sesi_dosen(self.logged_in_user)
                self.db.set_logout(self.logged_in_user)
            except:
                pass
        self.tampilkan_login()

    def darurat_exit_handler(self):
        try:
            self.db.cleanup_darurat_semua()
        except:
            pass

    def signal_handler(self, sig, frame):
        self.darurat_exit_handler()
        sys.exit(0)

    def on_close_app(self):
        self.darurat_exit_handler()
        self.destroy()

if __name__ == "__main__":
    app = AplikasiUtama()
    app.mainloop()