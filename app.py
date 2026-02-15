import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Dana Sosial Sekolah", layout="wide")

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False

if "kas_dana_sosial" not in st.session_state:
    st.session_state.kas_dana_sosial = []

if "kas_dharma" not in st.session_state:
    st.session_state.kas_dharma = []

if "kas_korpri" not in st.session_state:
    st.session_state.kas_korpri = []

# ================= LOGIN PAGE =================
if not st.session_state.login:

    st.markdown("<h1 style='text-align:center;'>SISTEM PENGELOLAAN KEUANGAN</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>SMK NEGERI 1 CERMEE BONDOWOSO</h3>", unsafe_allow_html=True)

    try:
        st.image("assets/logo.png", width=150)
    except:
        st.warning("Logo tidak ditemukan. Pastikan ada di folder assets/logo.png")

    st.markdown("### Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username atau Password salah")

    st.markdown("---")
    st.markdown("Created by : Admin Smakece")

# ================= MAIN APP =================
else:

    st.sidebar.title("MENU")

    menu = st.sidebar.selectbox("Pilih Menu",[
        "Input Transaksi",
        "Buku Kas Dana Sosial",
        "Buku Kas Dharma Wanita",
        "Buku Kas KORPRI",
        "Laporan",
        "Upload File",
        "Logout"
    ])

    # ========= FUNCTION TAMBAH DATA =========
    def tambah_data(storage, nama):
        st.header(f"INPUT {nama}")

        tanggal = st.date_input("Tanggal Transaksi")
        uraian = st.text_input("Uraian Transaksi")
        debet = st.number_input("Debet (Masuk)",0)
        kredit = st.number_input("Kredit (Keluar)",0)

        if st.button("Simpan"):
            saldo = (storage[-1]["SALDO"] if storage else 0) + debet - kredit

            storage.append({
                "NOMER": len(storage)+1,
                "TANGGAL": tanggal,
                "URAIAN TRANSAKSI": uraian.upper(),
                "DEBET": debet,
                "KREDIT": kredit,
                "SALDO": saldo
            })

            st.success("Data berhasil disimpan")

    # ========= FUNCTION TABEL =========
    def tampil_tabel(storage, nama):
        st.header(nama)

        if storage:
            df = pd.DataFrame(storage)
            st.dataframe(df, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                output = io.BytesIO()
                df.to_excel(output, index=False)
                st.download_button(
                    "Download Excel",
                    output.getvalue(),
                    f"{nama}.xlsx"
                )

            with col2:
                if st.button("Hapus Semua Data"):
                    storage.clear()
                    st.rerun()
        else:
            st.info("Belum ada data")

    # ========= MENU INPUT =========
    if menu == "Input Transaksi":

        jenis = st.selectbox("Pilih Jenis Kas",[
            "Dana Sosial","Dharma Wanita","KORPRI"
        ])

        if jenis == "Dana Sosial":
            tambah_data(st.session_state.kas_dana_sosial,"DANA SOSIAL")

        elif jenis == "Dharma Wanita":
            tambah_data(st.session_state.kas_dharma,"DHARMA WANITA")

        elif jenis == "KORPRI":
            tambah_data(st.session_state.kas_korpri,"KORPRI")

    # ========= BUKU KAS =========
    elif menu == "Buku Kas Dana Sosial":
        tampil_tabel(st.session_state.kas_dana_sosial,"BUKU KAS DANA SOSIAL")

    elif menu == "Buku Kas Dharma Wanita":
        tampil_tabel(st.session_state.kas_dharma,"BUKU KAS DHARMA WANITA")

    elif menu == "Buku Kas KORPRI":
        tampil_tabel(st.session_state.kas_korpri,"BUKU KAS KORPRI")

    # ========= LAPORAN =========
    elif menu == "Laporan":

        st.header("LAPORAN")

        uraian = [
            "SALDO DEBET JANUARI","SALDO DEBET PEBRUARI","SALDO DEBET MARET",
            "SALDO DEBET APRIL","SALDO DEBET MEI","SALDO DEBET JUNI",
            "SALDO DEBET JULI","SALDO DEBET AGUSTUS","SALDO DEBET SEPTEMBER",
            "SALDO DEBET OKTOBER","SALDO DEBET NOVEMBER","SALDO DEBET DESEMBER",
            "SALDO KREDIT JANUARI","SALDO KREDIT PEBRUARI","SALDO KREDIT MARET",
            "SALDO KREDIT APRIL","SALDO KREDIT MEI","SALDO KREDIT JUNI",
            "SALDO KREDIT JULI","SALDO KREDIT AGUSTUS","SALDO KREDIT SEPTEMBER",
            "SALDO KREDIT OKTOBER","SALDO KREDIT NOVEMBER","SALDO KREDIT DESEMBER"
        ]

        df = pd.DataFrame({
            "NOMER": range(1,len(uraian)+1),
            "URAIAN TRANSAKSI": uraian,
            "SALDO AKHIR": [0]*len(uraian)
        })

        edited = st.data_editor(df, use_container_width=True)

        output = io.BytesIO()
        edited.to_excel(output,index=False)

        st.download_button(
            "Download Laporan Excel",
            output.getvalue(),
            "laporan.xlsx"
        )

    # ========= UPLOAD =========
    elif menu == "Upload File":

        st.header("UPLOAD FILE")

        bukti = st.file_uploader("Upload Bukti Transaksi")
        kegiatan = st.file_uploader("Upload Foto Kegiatan")

        if bukti:
            st.success("Bukti transaksi berhasil diupload (simulasi)")

        if kegiatan:
            st.success("Foto kegiatan berhasil diupload (simulasi)")

    # ========= LOGOUT =========
    elif menu == "Logout":
        st.session_state.login = False
        st.rerun()
