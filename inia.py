import streamlit as st
import pandas as pd
import tempfile
from streamlit_option_menu import option_menu
from abc import ABC, abstractmethod

# Kelas Buku yang dimodifikasi untuk menyertakan atribut foto sampul
class Buku(ABC):
    def __init__(self, judul, penulis, tahun_terbit, foto_sampul=None, status="tersedia"):
        self.judul = judul
        self.penulis = penulis
        self.tahun_terbit = tahun_terbit
        self.foto_sampul = foto_sampul
        self.status = status

    @abstractmethod
    def info_buku(self):
        pass

class BukuDigital(Buku):
    def __init__(self, judul, penulis, tahun_terbit, ukuran_file, format_file, foto_sampul=None, status="tersedia"):
        super().__init__(judul, penulis, tahun_terbit, foto_sampul, status)
        self.ukuran_file = ukuran_file
        self.format_file = format_file
    
    def info_buku(self):
        info = f"Judul: {self.judul}\nPenulis: {self.penulis}\nTahun Terbit: {self.tahun_terbit}\nStatus: {self.status}"
        return f"{info}\nUkuran File: {self.ukuran_file}MB\nFormat: {self.format_file}"

class BukuFisik(Buku):
    def __init__(self, judul, penulis, tahun_terbit, jumlah_halaman, berat, foto_sampul=None, status="tersedia"):
        super().__init__(judul, penulis, tahun_terbit, foto_sampul, status)
        self.jumlah_halaman = jumlah_halaman
        self.berat = berat
    
    def info_buku(self):
        info = f"Judul: {self.judul}\nPenulis: {self.penulis}\nTahun Terbit: {self.tahun_terbit}\nStatus: {self.status}"
        return f"{info}\nJumlah Halaman: {self.jumlah_halaman}\nBerat: {self.berat} gram"

class Perpustakaan:
    def __init__(self):
        self.daftar_buku = []
        self.load_data()
    
    def tambah_buku(self, buku):
        self.daftar_buku.append(buku)
        self.simpan_data()
    
    def edit_buku(self, judul, buku_baru):
        for i, buku in enumerate(self.daftar_buku):
            if buku.judul.lower() == judul.lower():
                self.daftar_buku[i] = buku_baru
                self.simpan_data()
                return True
        return False
    
    def cari_buku(self, judul):
        for buku in self.daftar_buku:
            if buku.judul.lower() == judul.lower():
                return buku
        return None
    
    def tampilkan_semua_buku(self):
        return [buku.info_buku() for buku in self.daftar_buku]
    
    def pinjam_buku(self, judul):
        buku = self.cari_buku(judul)
        if buku and buku.status == "tersedia":
            buku.status = "dipinjam"
            self.simpan_data()
            return f"Buku '{judul}' berhasil dipinjam."
        else:
            return f"Buku '{judul}' tidak tersedia untuk dipinjam."
    
    def kembalikan_buku(self, judul):
        buku = self.cari_buku(judul)
        if buku and buku.status == "dipinjam":
            buku.status = "tersedia"
            self.simpan_data()
            return f"Buku '{judul}' berhasil dikembalikan."
        else:
            return f"Buku '{judul}' tidak sedang dipinjam."

    def simpan_data(self):
        data_buku = [{
            'Judul': buku.judul,
            'Penulis': buku.penulis,
            'Tahun Terbit': buku.tahun_terbit,
            'Status': buku.status,
            'Ukuran File (MB)': getattr(buku, 'ukuran_file', None),
            'Format File': getattr(buku, 'format_file', None),
            'Jumlah Halaman': getattr(buku, 'jumlah_halaman', None),
            'Berat (gram)': getattr(buku, 'berat', None),
            'Foto Sampul': buku.foto_sampul
        } for buku in self.daftar_buku]
        
        df_buku = pd.DataFrame(data_buku)
        df_buku.to_excel('data_perpustakaan.xlsx', index=False)

    def load_data(self):
        try:
            df_buku = pd.read_excel('data_perpustakaan.xlsx')
            for _, row in df_buku.iterrows():
                if pd.notna(row['Ukuran File (MB)']):
                    buku = BukuDigital(row['Judul'], row['Penulis'], row['Tahun Terbit'], row['Ukuran File (MB)'], row['Format File'], row['Foto Sampul'], row['Status'])
                else:
                    buku = BukuFisik(row['Judul'], row['Penulis'], row['Tahun Terbit'], row['Jumlah Halaman'], row['Berat (gram)'], row['Foto Sampul'], row['Status'])
                self.daftar_buku.append(buku)
        except FileNotFoundError:
            st.error("File data_perpustakaan.xlsx tidak ditemukan.")

# Inisialisasi perpustakaan
perpustakaan = Perpustakaan()

# Antarmuka Streamlit
st.title("PERPUSTAKAAN")

with st.sidebar:
    st.image("loggg.png", width=180)
    menu = option_menu(
        "Menu",
        ["Tambah Buku", "Tampilkan Semua Buku", "Buku yang Dipinjam"],
        icons=["book", "list", "bookshelf"],
        menu_icon="cast",
        default_index=0,
    )

if menu == "Tambah Buku":
    st.subheader("Tambah Buku Baru")
    tipe_buku = st.selectbox("Tipe Buku", ["Buku Fisik", "Buku Digital"])
    judul = st.text_input("Judul Buku")
    penulis = st.text_input("Penulis Buku")
    tahun_terbit = st.number_input("Tahun Terbit", min_value=1500, max_value=2024, step=1)
    foto_sampul = st.file_uploader("Unggah Foto Sampul", type=["jpg", "png", "jpeg"])
    
    if foto_sampul is not None:
        foto_sampul_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix=foto_sampul.name)
        foto_sampul_tempfile.write(foto_sampul.getbuffer())
        foto_sampul_path = foto_sampul_tempfile.name
    
    if tipe_buku == "Buku Digital":
        ukuran_file = st.number_input("Ukuran File (MB)", min_value=0.1)
        format_file = st.selectbox("Format File", ["PDF", "EPUB", "MOBI"])
        if st.button("Tambah Buku Digital"):
            buku = BukuDigital(judul, penulis, tahun_terbit, ukuran_file, format_file, foto_sampul_path)
            perpustakaan.tambah_buku(buku)
            st.success(f"Buku digital '{judul}' berhasil ditambahkan.")
    else:
        jumlah_halaman = st.number_input("Jumlah Halaman", min_value=1)
        berat = st.number_input("Berat (gram)", min_value=1)
        if st.button("Tambah Buku Fisik"):
            buku = BukuFisik(judul, penulis, tahun_terbit, jumlah_halaman, berat, foto_sampul_path)
            perpustakaan.tambah_buku(buku)
            st.success(f"Buku fisik '{judul}' berhasil ditambahkan.")
            
elif menu == "Tampilkan Semua Buku":
    st.subheader("Daftar Semua Buku")
    judul_cari = st.text_input("Cari Buku")
    buku_list = perpustakaan.tampilkan_semua_buku()
    
    if judul_cari:
        buku_list = [buku for buku in buku_list if judul_cari.lower() in buku.lower()]

    for buku in buku_list:
        buku_obj = perpustakaan.cari_buku(buku.split("\n")[0].split(":")[1].strip())
        if buku_obj:
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                with col1:
                    if buku_obj.foto_sampul:
                        st.image(buku_obj.foto_sampul, width=100)
                with col2:
                    st.markdown(buku_obj.info_buku().replace("\n", "\n\n"))
                with col3:
                    if st.button(f"Pinjam", key=f"pinjam-{buku_obj.judul}"):
                        pesan = perpustakaan.pinjam_buku(buku_obj.judul)
                        st.write(pesan)
                        st.experimental_rerun()
                with col4:
                    if st.button(f"Edit", key=f"edit-{buku_obj.judul}"):
                        st.session_state['edit_buku'] = buku_obj.judul
                        st.experimental_rerun()
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("---")

if 'edit_buku' in st.session_state:
    buku_edit = perpustakaan.cari_buku(st.session_state['edit_buku'])
    if buku_edit:
        st.subheader(f"Edit Buku: {buku_edit.judul}")
        judul = st.text_input("Judul Buku", value=buku_edit.judul)
        penulis = st.text_input("Penulis Buku", value=buku_edit.penulis)
        tahun_terbit = st.number_input("Tahun Terbit", value=buku_edit.tahun_terbit, min_value=1500, max_value=2024, step=1)
        foto_sampul = st.file_uploader("Unggah Foto Sampul", type=["jpg", "png", "jpeg"], key="edit_foto_sampul")

        if foto_sampul is not None:
            foto_sampul_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix=foto_sampul.name)
            foto_sampul_tempfile.write(foto_sampul.getbuffer())
            foto_sampul_path = foto_sampul_tempfile.name
        else:
            foto_sampul_path = buku_edit.foto_sampul

        if isinstance(buku_edit, BukuDigital):
            ukuran_file = st.number_input("Ukuran File (MB)", value=buku_edit.ukuran_file, min_value=0.1)
            format_file = st.selectbox("Format File", ["PDF", "EPUB", "MOBI"], index=["PDF", "EPUB", "MOBI"].index(buku_edit.format_file))
            if st.button("Simpan Perubahan"):
                buku_baru = BukuDigital(judul, penulis, tahun_terbit, ukuran_file, format_file, foto_sampul_path, buku_edit.status)
                if perpustakaan.edit_buku(buku_edit.judul, buku_baru):
                    st.success(f"Buku '{judul}' berhasil diperbarui.")
                    del st.session_state['edit_buku']
                    st.experimental_rerun()
        else:
            jumlah_halaman = st.number_input("Jumlah Halaman", value=buku_edit.jumlah_halaman, min_value=1)
            berat = st.number_input("Berat (gram)", value=buku_edit.berat, min_value=1)
            if st.button("Simpan Perubahan"):
                buku_baru = BukuFisik(judul, penulis, tahun_terbit, jumlah_halaman, berat, foto_sampul_path, buku_edit.status)
                if perpustakaan.edit_buku(buku_edit.judul, buku_baru):
                    st.success(f"Buku '{judul}' berhasil diperbarui.")
                    del st.session_state['edit_buku']
                    st.experimental_rerun()

elif menu == "Buku yang Dipinjam":
    st.subheader("Buku yang Dipinjam")
    dipinjam_list = [buku for buku in perpustakaan.daftar_buku if buku.status == "dipinjam"]
    
    if dipinjam_list:
        for buku in dipinjam_list:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    if buku.foto_sampul:
                        st.image(buku.foto_sampul, width=100)
                with col2:
                    st.markdown(buku.info_buku().replace("\n", "\n\n"))
                with col3:
                    if st.button(f"Kembalikan Buku {buku.judul}", key=buku.judul):
                        pesan = perpustakaan.kembalikan_buku(buku.judul)
                        st.write(pesan)
                        st.experimental_rerun()
                # Menambahkan jarak antar buku
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("---")
    else:
        st.write("Tidak ada buku yang sedang dipinjam.")
