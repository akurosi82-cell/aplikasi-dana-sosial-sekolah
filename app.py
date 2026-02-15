import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Dana Sosial Sekolah", layout="wide")

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False

if "data" not in st.session_state:
    st.session_state.data = {
        "Dana Sosial": [],
        "Dharma Wanita": [],
        "KORPRI": []
    }

# ================= STYLE =================
st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #e3f2fd, #ffffff);
}

/* LOGIN STANDAR */
.login-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 80px;
}

.login-content {
    width: 320px;
    text-align: center;
}

/* Tombol */
.stButton>button {
    background-color: #003366;
    color: white;
    border-radius: 6px;
    height: 38px;
    width: 100%;
}

.stButton>button:hover {
    background-color: #0055aa;
}

h2,h3 {color:#003366;}

</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
if not st.session_state.login:

    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-content">', unsafe_allow_html=True)

    st.image("logo.png", width=120)
    st.markdown("<h2>APLIKASI PENGELOLAAN KEUANGAN</h2>", unsafe_allow_html=True)
    st.markdown("<h3>SMK NEGERI 1 CERMEE BONDOWOSO</h3>", unsafe_allow_html=True)

    username = st.text_input("USERNAME")
    password = st.text_input("PASSWORD", type="password")

    if st.button("LOGIN"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username atau Password Salah")

    st.markdown("<br><small>Created by : Admin Smakece</small>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

# ================= MENU UTAMA =================
else:

    st.sidebar.title("MENU")
    menu = st.sidebar.selectbox("Pilih Menu", [
        "Input Transaksi",
        "Buku Kas",
        "Rekap Kas Bulanan",
        "Laporan Tahunan",
        "Upload File"
    ])

    if st.sidebar.button("LOG OUT"):
        st.session_state.login = False
        st.rerun()

    # ================= INPUT TRANSAKSI =================
    if menu == "Input Transaksi":

        st.header("INPUT TRANSAKSI")

        jenis = st.selectbox("Pilih Buku Kas", ["Dana Sosial", "Dharma Wanita", "KORPRI"])
        tanggal = st.date_input("Tanggal Transaksi")
        uraian = st.text_input("Uraian Transaksi")
        debet = st.number_input("Debet (Masuk)", min_value=0)
        kredit = st.number_input("Kredit (Keluar)", min_value=0)

        col1, col2 = st.columns(2)

        if col1.button("SIMPAN"):
            saldo_sebelumnya = sum([d["debet"] - d["kredit"] for d in st.session_state.data[jenis]])
            saldo_baru = saldo_sebelumnya + debet - kredit

            st.session_state.data[jenis].append({
                "tanggal": tanggal,
                "uraian": uraian,
                "debet": debet,
                "kredit": kredit,
                "saldo": saldo_baru
            })

            st.success("Transaksi berhasil disimpan")

        if col2.button("BATAL"):
            st.rerun()

    # ================= BUKU KAS =================
    elif menu == "Buku Kas":

        st.header("BUKU KAS")
        jenis = st.selectbox("Pilih Buku Kas", ["Dana Sosial", "Dharma Wanita", "KORPRI"])

        data = st.session_state.data[jenis]

        if data:
            df = pd.DataFrame(data)
            df.insert(0, "NOMER", range(1, len(df)+1))
            df.columns = ["NOMER", "TANGGAL", "URAIAN TRANSAKSI", "DEBET", "KREDIT", "SALDO"]
            st.dataframe(df, use_container_width=True)

            # Hapus data
            nomor_hapus = st.number_input("Masukkan Nomor untuk Hapus", min_value=1, max_value=len(df))
            if st.button("HAPUS"):
                del st.session_state.data[jenis][nomor_hapus-1]
                st.success("Data berhasil dihapus")
                st.rerun()

            # Download Excel
            df.to_excel("buku_kas.xlsx", index=False)
            with open("buku_kas.xlsx", "rb") as file:
                st.download_button("Download Excel", file, file_name="buku_kas.xlsx")
        else:
            st.info("Belum ada data")

    # ================= REKAP BULANAN =================
    elif menu == "Rekap Kas Bulanan":

        st.header("REKAP KAS BULANAN")
        jenis = st.selectbox("Pilih Buku Kas", ["Dana Sosial", "Dharma Wanita", "KORPRI"])

        data = st.session_state.data[jenis]

        if data:
            df = pd.DataFrame(data)
            df.insert(0, "NOMER", range(1, len(df)+1))
            df.columns = ["NOMER", "TANGGAL", "URAIAN TRANSAKSI", "DEBET", "KREDIT", "SALDO"]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Belum ada data")

    # ================= LAPORAN =================
    elif menu == "Laporan Tahunan":

        st.header("LAPORAN TAHUNAN")

        jenis = st.selectbox("Pilih Buku Kas", ["Dana Sosial", "Dharma Wanita", "KORPRI"])

        bulan = ["Januari","Februari","Maret","April","Mei","Juni",
                 "Juli","Agustus","September","Oktober","November","Desember"]

        laporan = []
        for i, b in enumerate(bulan):
            laporan.append({
                "NOMER": i+1,
                "TANGGAL": b,
                "URAIAN": f"SALDO AKHIR {b.upper()}",
                "DEBET": 0,
                "KREDIT": 0,
                "SALDO": 0
            })

        df = pd.DataFrame(laporan)
        st.dataframe(df, use_container_width=True)

        df.to_excel("laporan_tahunan.xlsx", index=False)
        with open("laporan_tahunan.xlsx", "rb") as file:
            st.download_button("Download Laporan Excel", file, file_name="laporan_tahunan.xlsx")

    # ================= UPLOAD =================
    elif menu == "Upload File":

        st.header("UPLOAD FILE")

        bukti = st.file_uploader("Upload Bukti Transaksi")
        kegiatan = st.file_uploader("Upload Foto Kegiatan")

        if bukti:
            st.success("Bukti Transaksi berhasil diupload")

        if kegiatan:
            st.success("Foto Kegiatan berhasil diupload")
