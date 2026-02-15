import streamlit as st
import pandas as pd
import datetime
import os
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# =========================
# KONFIGURASI GOOGLE DRIVE
# =========================

FOLDER_TRANSAKSI = "1AJ2ZjiFLNuTQufuPcEvFbdf-wFMtcr3c"
FOLDER_KEGIATAN = "1W7Yg8VNOQeBhzoX5lVf3WrMDGmt6WDg5"

def connect_drive():
    credentials = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)
    return service

def upload_to_drive(uploaded_file, folder_id):
    service = connect_drive()

    file_metadata = {
        "name": uploaded_file.name,
        "parents": [folder_id]
    }

    media = MediaIoBaseUpload(
        uploaded_file,
        mimetype=uploaded_file.type,
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return file.get("id")

# =========================
# LOGIN SYSTEM
# =========================

if "login" not in st.session_state:
    st.session_state.login = False

def login_page():
    st.image("logo.png", width=150)
    st.title("APLIKASI PENGELOLAAN KEUANGAN")
    st.subheader("SMK NEGERI 1 CERMEE")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
            st.success("Login Berhasil")
        else:
            st.error("Username atau Password salah")

    st.markdown("---")
    st.markdown("Created by : Admin Smakece")

if not st.session_state.login:
    login_page()
    st.stop()

# =========================
# DATABASE SEMENTARA
# =========================

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Tanggal", "Jenis Kas", "Uraian",
        "Debet", "Kredit", "Saldo"
    ])

# =========================
# SIDEBAR MENU
# =========================

menu = st.sidebar.selectbox("Menu", [
    "Dashboard",
    "Input Transaksi",
    "Upload Bukti Kegiatan",
    "Laporan"
])

# =========================
# DASHBOARD
# =========================

if menu == "Dashboard":
    st.title("Buku Kas Umum")

    df = st.session_state.data

    if not df.empty:
        df["No"] = range(1, len(df) + 1)
        df = df[["No","Tanggal","Jenis Kas","Uraian","Debet","Kredit","Saldo"]]

    st.dataframe(df, use_container_width=True)

    # Download Excel
    output = BytesIO()
    df.to_excel(output, index=False)

    st.download_button(
        label="Download Excel",
        data=output.getvalue(),
        file_name="buku_kas.xlsx"
    )

# =========================
# INPUT TRANSAKSI
# =========================

if menu == "Input Transaksi":
    st.title("Input Transaksi")

    tanggal = st.date_input("Tanggal", datetime.date.today())
    jenis_kas = st.selectbox("Jenis Kas", [
        "Dana Sosial", "KORPRI", "Dharma Wanita"
    ])
    uraian = st.text_input("Uraian Transaksi")
    tipe = st.radio("Jenis", ["Masuk", "Keluar"])
    nominal = st.number_input("Nominal", min_value=0)

    bukti = st.file_uploader("Upload Bukti Transaksi")

    if st.button("Simpan"):
        debet = nominal if tipe == "Masuk" else 0
        kredit = nominal if tipe == "Keluar" else 0

        saldo_awal = 0
        if not st.session_state.data.empty:
            saldo_awal = st.session_state.data.iloc[-1]["Saldo"]

        saldo_baru = saldo_awal + debet - kredit

        new_data = pd.DataFrame([{
            "Tanggal": tanggal,
            "Jenis Kas": jenis_kas,
            "Uraian": uraian,
            "Debet": debet,
            "Kredit": kredit,
            "Saldo": saldo_baru
        }])

        st.session_state.data = pd.concat(
            [st.session_state.data, new_data],
            ignore_index=True
        )

        # Upload ke Google Drive
        if bukti is not None:
            upload_to_drive(bukti, FOLDER_TRANSAKSI)
            st.success("Bukti berhasil diupload ke Google Drive")

        st.success("Transaksi berhasil disimpan")

# =========================
# UPLOAD BUKTI KEGIATAN
# =========================

if menu == "Upload Bukti Kegiatan":
    st.title("Upload Bukti Kegiatan")

    file_kegiatan = st.file_uploader("Upload Bukti Kegiatan")

    if st.button("Upload"):
        if file_kegiatan is not None:
            upload_to_drive(file_kegiatan, FOLDER_KEGIATAN)
            st.success("Bukti kegiatan berhasil diupload")

# =========================
# LAPORAN
# =========================

if menu == "Laporan":
    st.title("Laporan Keuangan")

    df = st.session_state.data

    if df.empty:
        st.warning("Belum ada data")
    else:
        total_masuk = df["Debet"].sum()
        total_keluar = df["Kredit"].sum()
        saldo_akhir = total_masuk - total_keluar

        laporan = df.copy()
        laporan["Nominal"] = laporan["Debet"] + laporan["Kredit"]

        laporan["No"] = range(1, len(laporan) + 1)
        laporan = laporan[[
            "No","Tanggal","Uraian","Nominal"
        ]]

        st.dataframe(laporan, use_container_width=True)

        st.write("Total Penerimaan:", total_masuk)
        st.write("Total Pengeluaran:", total_keluar)
        st.write("Saldo Akhir:", saldo_akhir)

        output = BytesIO()
        laporan.to_excel(output, index=False)

        st.download_button(
            label="Download Laporan Excel",
            data=output.getvalue(),
            file_name="laporan_keuangan.xlsx"
        )
