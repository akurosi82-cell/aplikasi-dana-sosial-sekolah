import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import calendar

# ================= KONFIGURASI =================
st.set_page_config(
    page_title="Aplikasi Dana Sosial SMKN 1 Cermee",
    page_icon="💰",
    layout="wide"
)

# ================= CSS TENGAH SEMPURNA =================
st.markdown("""
<style>

/* Hilangkan sidebar saat login */
section[data-testid="stSidebar"] {
    display: none;
}

/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #e3f2fd, #ffffff);
}

/* Container tengah */
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

/* Box login */
.login-box {
    width: 420px;
    padding: 40px;
    background-color: white;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    text-align: center;
}

/* Judul */
.login-title {
    color: #003366;
    font-size: 22px;
    font-weight: bold;
}

.login-school {
    color: #003366;
    font-size: 18px;
    margin-bottom: 20px;
}

.stButton>button {
    background-color: #003366;
    color: white;
    border-radius: 8px;
    height: 40px;
    width: 100%;
}

.stButton>button:hover {
    background-color: #0055aa;
}

</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False

# ================= LOGIN PAGE =================
if not st.session_state.login:

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.image("logo.png", width=150)

    st.markdown('<div class="login-title">APLIKASI PENGELOLAAN KEUANGAN</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-school">SMK NEGERI 1 CERMEE BONDOWOSO</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("LOGIN"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username atau Password Salah")

    st.markdown("<br><small>Created by : Admin Smakece</small>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ================= HALAMAN UTAMA =================
else:

    st.sidebar.title("MENU UTAMA")
    menu = st.sidebar.selectbox("PILIH MENU", [
        "INPUT TRANSAKSI",
        "BUKU KAS",
        "LOG OUT"
    ])

    if menu == "INPUT TRANSAKSI":
        st.title("INPUT TRANSAKSI")
        tanggal = st.date_input("Tanggal")
        uraian = st.text_input("Uraian")
        debet = st.number_input("Debet", min_value=0)
        kredit = st.number_input("Kredit", min_value=0)

        if st.button("SIMPAN"):
            st.success("Data tersimpan (contoh tampilan)")

    if menu == "BUKU KAS":
        st.title("BUKU KAS")
        st.info("Contoh tampilan buku kas")

    if menu == "LOG OUT":
        st.session_state.login = False
        st.rerun()
