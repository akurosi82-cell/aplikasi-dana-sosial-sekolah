import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO
import os

# ================== KONFIGURASI HALAMAN ==================
st.set_page_config(page_title="Keuangan Dana Sosial", layout="wide")

# ================== DATABASE ==================
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    kategori TEXT,
    uraian TEXT,
    jenis TEXT,
    nominal REAL
)
''')
conn.commit()

# ================== FUNGSI DOWNLOAD EXCEL ==================
def download_excel(df, nama_file):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="⬇ Download Excel",
        data=output,
        file_name=nama_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ================== LOGIN ==================
def login():

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
        else:
            st.warning("File logo.png belum ada di folder utama")

        st.markdown("<h2 style='text-align:center;'>SMK NEGERI 1 CERMEE</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center;'>APLIKASI PENGELOLAAN DANA SOSIAL SEKOLAH</h4>", unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "admin" and password == "1234":
                st.session_state["login"] = True
                st.rerun()
            else:
                st.error("Username atau Password salah")

        st.markdown("<p style='text-align:center;'>Created by : Admin Smakece</p>", unsafe_allow_html=True)

# ================== DASHBOARD ==================
def dashboard():

    st.sidebar.title("MENU")
    menu = st.sidebar.selectbox("Pilih Menu", [
        "Buku Kas Umum",
        "Kas KORPRI",
        "Kas Dharma Wanita",
        "Input Transaksi",
        "Laporan"
    ])

    # ================== INPUT TRANSAKSI ==================
    if menu == "Input Transaksi":
        st.header("Input Transaksi")

        tanggal = st.date_input("Tanggal Transaksi")
        kategori = st.selectbox("Kategori", ["Dana Sosial", "KORPRI", "Dharma Wanita"])
        uraian = st.text_input("Uraian / Nama Transaksi")
        jenis = st.radio("Jenis", ["Masuk", "Keluar"])
        nominal = st.number_input("Nominal", min_value=0.0)

        if st.button("Simpan Transaksi"):
            c.execute("INSERT INTO transaksi (tanggal,kategori,uraian,jenis,nominal) VALUES (?,?,?,?,?)",
                      (str(tanggal), kategori, uraian, jenis, nominal))
            conn.commit()
            st.success("Transaksi berhasil disimpan")

    # ================== FUNGSI TAMPIL KAS ==================
    def tampil_kas(filter_kategori=None):
        if filter_kategori:
            df = pd.read_sql(f"SELECT * FROM transaksi WHERE kategori='{filter_kategori}'", conn)
        else:
            df = pd.read_sql("SELECT * FROM transaksi", conn)

        if not df.empty:
            df["Debet"] = df.apply(lambda x: x["nominal"] if x["jenis"]=="Masuk" else 0, axis=1)
            df["Kredit"] = df.apply(lambda x: x["nominal"] if x["jenis"]=="Keluar" else 0, axis=1)
            df["Saldo"] = df["Debet"].cumsum() - df["Kredit"].cumsum()

            df_view = df[["id","tanggal","uraian","Debet","Kredit","Saldo"]]
            st.dataframe(df_view, use_container_width=True)

            download_excel(df_view, "buku_kas.xlsx")
        else:
            st.info("Belum ada transaksi")

    # ================== MENU BUKU KAS ==================
    elif menu == "Buku Kas Umum":
        st.header("Buku Kas Umum (Semua Dana)")
        tampil_kas()

    elif menu == "Kas KORPRI":
        st.header("Kas Khusus KORPRI")
        tampil_kas("KORPRI")

    elif menu == "Kas Dharma Wanita":
        st.header("Kas Khusus Dharma Wanita")
        tampil_kas("Dharma Wanita")

    # ================== LAPORAN ==================
    elif menu == "Laporan":
        st.header("Laporan Keuangan")

        df = pd.read_sql("SELECT * FROM transaksi", conn)

        if not df.empty:
            total_masuk = df[df["jenis"]=="Masuk"]["nominal"].sum()
            total_keluar = df[df["jenis"]=="Keluar"]["nominal"].sum()
            saldo = total_masuk - total_keluar

            st.metric("Total Penerimaan", f"Rp {total_masuk:,.0f}")
            st.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
            st.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

            download_excel(df, "laporan_keuangan.xlsx")
        else:
            st.info("Belum ada data laporan")

# ================== MAIN ==================
if "login" not in st.session_state:
    st.session_state["login"] = False

if not st.session_state["login"]:
    login()
else:
    dashboard()
