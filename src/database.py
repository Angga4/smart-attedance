from abc import ABC, abstractmethod
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class AbsenError(Exception):
    """Custom exception untuk penanganan error khusus pada sistem absensi."""
    pass


class User(ABC):
    def __init__(self, username, password, nama):
        self._username = username          
        self.__password = password         
        self._nama = nama

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, value):
        self.__password = value

    @property
    def nama(self):
        return self._nama

    @abstractmethod
    def login(self):
        """Method abstrak yang wajib di-override oleh subclass."""
        pass

    
    def __str__(self):
        return f"Pengguna Sistem: {self._nama} ({self._username})"

    def __eq__(self, other):
        if isinstance(other, User):
            return self._username == other._username
        return False


class Dosen(User):
    def __init__(self, username, password, nama, nidn):
        super().__init__(username, password, nama)
        self.nidn = nidn

    def login(self):
        return f"Dosen {self._nama} dengan NIDN {self.nidn} berhasil masuk."

    def buat_laporan(self, jenis="harian"):
        return f"Dosen {self._nama} mencetak laporan absensi rekap jenis: {jenis}."


class Mahasiswa(User):
    def __init__(self, username, password, nama, nim):
        super().__init__(username, password, nama)
        self.nim = nim

    def login(self):
        return f"Mahasiswa {self._nama} dengan NIM {self.nim} berhasil masuk."

    def buat_laporan(self, jenis="harian"):
        return f"Mahasiswa {self._nama} melihat riwayat absensi jenis: {jenis}."



class RiwayatAbsenIterator:
    """Custom iterator untuk menelusuri data rekap absensi baris per baris."""
    def __init__(self, data_list):
        self._data_list = data_list
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._data_list):
            item = self._data_list[self._index]
            self._index += 1
            return item
        raise StopIteration


class DatabaseOnline:
    def __init__(self, credentials_path="data/credentials.json", sheet_name="RekapAbsensi"):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open(sheet_name)
            self.sheet_rekap = self.spreadsheet.worksheet("RekapAbsensi")
            self.sheet_user = self.spreadsheet.worksheet("Users")
            
            try:
                self.sheet_mk = self.spreadsheet.worksheet("MataKuliah")
            except:
                self.sheet_mk = self.spreadsheet.add_worksheet(title="MataKuliah", rows=10, cols=3)
                self.sheet_mk.append_row(["nip_dosen", "kode_mk", "nama_mk"])

            try:
                self.sheet_sesi = self.spreadsheet.worksheet("SesiAktif")
            except:
                self.sheet_sesi = self.spreadsheet.add_worksheet(title="SesiAktif", rows=10, cols=5)
                self.sheet_sesi.append_row(["nip_dosen", "kode_unik", "kode_mk", "nama_mk", "status"])
        except Exception as e:
            print(f"Gagal terhubung ke Google Sheets: {e}")

    def verifikasi_login(self, username, password, role):
        if not self.sheet_user:
            return False, "Database online tidak terhubung."
        

        try:
            records = self.sheet_user.get_all_records()
            for idx, row in enumerate(records, start=2):
                db_role = str(row.get('role', '')).strip()
                db_user = str(row.get('id_user', '')).strip()
                db_pass = str(row.get('password', '')).strip()
                db_nama = str(row.get('nama', '')).strip()
                db_status = str(row.get('status_login', '')).strip()

                if db_user == str(username).strip():
                    if db_role.lower() != role.lower() or db_pass != str(password).strip():
                        raise AbsenError("Password atau Peran tidak valid.")
                    
                    if db_status.lower() == "online":
                        raise AbsenError("Akses ditolak! Akun ini sedang aktif di perangkat lain.")
                    
                    self.sheet_user.update_cell(idx, 5, "Online")
                    return True, db_nama

            return False, "Username/ID tidak ditemukan."
        except AbsenError as ae:
            return False, str(ae)
        finally:
            pass 

    def set_logout(self, username):
        if not self.sheet_user:
            return
        records = self.sheet_user.get_all_records()
        for idx, row in enumerate(records, start=2):
            if str(row.get('id_user', '')).strip() == str(username).strip():
                self.sheet_user.update_cell(idx, 5, "Offline")
                break

    def ambil_matkul_dosen(self, nip_dosen):
        if not self.sheet_mk:
            return []
        records = self.sheet_mk.get_all_records()
        list_mk = []
        for r in records:
            if str(r.get('nip_dosen', '')).strip() == str(nip_dosen).strip():
                list_mk.append(f"{str(r.get('kode_mk', '')).strip()} - {str(r.get('nama_mk', '')).strip()}")
        return list_mk

    def simpan_sesi_aktif(self, nip_dosen, kode_unik, kode_mk, nama_mk):
        if not self.sheet_sesi:
            return
        records = self.sheet_sesi.get_all_records()
        for idx, r in enumerate(records, start=2):
            if str(r.get('nip_dosen', '')).strip() == str(nip_dosen).strip() and str(r.get('status', '')).strip() == "Aktif":
                self.sheet_sesi.update_cell(idx, 5, "Nonaktif")
        
        self.sheet_sesi.append_row([str(nip_dosen).strip(), str(kode_unik).strip(), str(kode_mk).strip(), str(nama_mk).strip(), "Aktif"])

    def tutup_semua_sesi_dosen(self, nip_dosen):
        if not self.sheet_sesi:
            return
        records = self.sheet_sesi.get_all_records()
        for idx, r in enumerate(records, start=2):
            if str(r.get('nip_dosen', '')).strip() == str(nip_dosen).strip() and str(r.get('status', '')).strip() == "Aktif":
                self.sheet_sesi.update_cell(idx, 5, "Nonaktif")

    def ambil_info_sesi_dari_kode(self, kode_unik):
        if not self.sheet_sesi:
            return None
        records = self.sheet_sesi.get_all_records()
        for r in records:
            if str(r.get('kode_unik', '')).strip().upper() == str(kode_unik).strip().upper() and str(r.get('status', '')).strip() == "Aktif":
                return {
                    "nip_dosen": str(r.get('nip_dosen', '')).strip(),
                    "kode_mk": str(r.get('kode_mk', '')).strip(),
                    "nama_mk": str(r.get('nama_mk', '')).strip()
                }
        return None

    def cek_sudah_absen_sesi(self, nim, kode_sesi):
        if not self.sheet_rekap:
            return False
        records = self.sheet_rekap.get_all_records()
        for row in records:
            if str(row.get('nim', '')).strip() == str(nim).strip() and str(row.get('kode_sesi', '')).strip().upper() == str(kode_sesi).strip().upper():
                return True
        return False

    def simpan_absensi(self, nim, nama_mhs, kode_mk, kode_sesi, status_kehadiran):
        if not self.sheet_rekap:
            return False
        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sheet_rekap.append_row([str(nim).strip(), str(nama_mhs).strip(), str(kode_mk).strip(), str(kode_sesi).strip(), waktu, str(status_kehadiran).strip()])
        
   
        try:
            with open("data/log_aktivitas.txt", "a") as f:
                f.write(f"[{waktu}] Absen tercatat: {nim} - {status_kehadiran}\n")
        except IOError:
            pass

        return True

    def ambil_rekap_sesi(self, kode_sesi):
        if not self.sheet_rekap:
            return []
        records = self.sheet_rekap.get_all_records()
        return [row for row in records if str(row.get('kode_sesi', '')).strip().upper() == str(kode_sesi).strip().upper()]

    def akhiri_sesi_dan_rekap_alpha(self, nip_dosen, kode_sesi, kode_mk, nama_mk):
        if not self.sheet_user or not self.sheet_rekap:
            return 0
        
        all_users = self.sheet_user.get_all_records()
        mahasiswa_list = [u for u in all_users if str(u.get('role', '')).strip().lower() == "mahasiswa"]
        nim_sudah_absen = {str(r.get('nim', '')).strip() for r in self.ambil_rekap_sesi(kode_sesi)}

        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        count_alpha = 0

        for mhs in mahasiswa_list:
            nim_mhs = str(mhs.get('id_user', '')).strip()
            if nim_mhs not in nim_sudah_absen:
                self.sheet_rekap.append_row([nim_mhs, str(mhs.get('nama', '')).strip(), str(kode_mk).strip(), str(kode_sesi).strip(), waktu, "Alpha"])
                count_alpha += 1

        self.tutup_semua_sesi_dosen(nip_dosen)
        return count_alpha

    def cleanup_darurat_semua(self):
        try:
            if self.sheet_user:
                for idx, row in enumerate(self.sheet_user.get_all_records(), start=2):
                    if str(row.get('status_login', '')).strip().lower() == "online":
                        self.sheet_user.update_cell(idx, 5, "Offline")
            if self.sheet_sesi:
                for idx, row in enumerate(self.sheet_sesi.get_all_records(), start=2):
                    if str(row.get('status', '')).strip().lower() == "aktif":
                        self.sheet_sesi.update_cell(idx, 5, "Nonaktif")
        except:
            pass