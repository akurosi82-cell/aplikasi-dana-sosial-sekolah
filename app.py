import streamlit as st
import pandas as pd
import datetime
import os
from io import BytesIO
from openpyxl import Workbook
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ================= LOGIN ==================
if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.image("logo.png", width=150)
    st.title("APLIKASI PENGELOLAAN KEUANGAN")
    st.subheader("SMK NEGERI 1 CERMEE")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
            st.success("Login berhasil")
        else:
            st.error("Username atau Password salah")

    st.markdown("Created by : Admin Smakece")

if not st.session_state.login:
    login()
    st.stop()

# ================= DATA ==================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Tanggal", "Jenis Kas", "Uraian",
        "Debet", "Kredit", "Saldo"
    ])

# ================= SIDEBAR ==================
menu = st.sidebar.selectbox("Menu", [
    "Dashboard",
    "Input Transaksi",
    "Laporan"
])

# ================= DASHBOARD ==================
if menu == "Dashboard":
    st.title("Buku Kas Umum")

    df = st.session_state.data

    st.dataframe(df)

    # Download Excel
    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button(
        label="Download Excel",
        data=output.getvalue(),
        file_name="buku_kas.xlsx"
    )

# ================= INPUT ==================
if menu == "Input Transaksi":
    st.title("Input Transaksi")

    tanggal = st.date_input("Tanggal", datetime.date.today())
    jenis_kas = st.selectbox("Jenis Kas", [
        "Dana Sosial", "KORPRI", "Dharma Wanita"
    ])
    uraian = st.text_input("Uraian")
    tipe = st.radio("Jenis Transaksi", ["Masuk", "Keluar"])
    nominal = st.number_input("Nominal", min_value=0)

    bukti = st.file_uploader("Upload Bukti Transaksi")

    if st.button("Simpan"):
        debet = nominal if tipe == "Masuk" else 0
        kredit = nominal if tipe == "Keluar" else 0

        saldo_sebelumnya = 0
        if not st.session_state.data.empty:
            saldo_sebelumnya = st.session_state.data.iloc[-1]["Saldo"]

        saldo_baru = saldo_sebelumnya + debet - kredit

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

        st.success("Data berhasil disimpan")

# ================= LAPORAN ==================
if menu == "Laporan":
    st.title("Laporan Keuangan")

    df = st.session_state.data

    total_masuk = df["Debet"].sum()
    total_keluar = df["Kredit"].sum()
    saldo_akhir = total_masuk - total_keluar

    laporan = df.copy()
    laporan["Nominal"] = laporan["Debet"] + laporan["Kredit"]

    st.dataframe(laporan)

    st.write("Total Penerimaan:", total_masuk)
    st.write("Total Pengeluaran:", total_keluar)
    st.write("Saldo Akhir:", saldo_akhir)

    output = BytesIO()
    laporan.to_excel(output, index=False)
    st.download_button(
        label="Download Laporan Excel",
        data=output.getvalue(),
        file_name="laporan.xlsx"
    )
