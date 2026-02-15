import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import calendar
import os

# ================= KONFIGURASI =================
st.set_page_config(
    page_title="Aplikasi Dana Sosial SMKN 1 Cermee",
    page_icon="💰",
    layout="wide"
)

# ================= FOLDER UPLOAD =================
os.makedirs("upload_bukti_transaksi", exist_ok=True)
os.makedirs("upload_kegiatan", exist_ok=True)

# ================= STYLE =================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #e3f2fd, #ffffff);
}
.center-box {
    width: 320px;
    margin: auto;
    text-align: center;
    padding-top: 60px;
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
h1,h2,h3 {color:#003366;}
</style>
""", unsafe_allow_html=True)

# ================= BULAN INDONESIA =================
bulan_indo = {
1:"JANUARI",2:"FEBRUARI",3:"MARET",4:"APRIL",
5:"MEI",6:"JUNI",7:"JULI",8:"AGUSTUS",
9:"SEPTEMBER",10:"OKTOBER",11:"NOVEMBER",12:"DESEMBER"
}

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False

def init_df():
    return pd.DataFrame(columns=["TANGGAL","URAIAN","DEBET","KREDIT","SALDO"])

for kas in ["dana","dharma","korpri"]:
    if kas not in st.session_state:
        st.session_state[kas] = init_df()

# ================= HITUNG SALDO =================
def hitung_saldo(df):
    df = df.sort_values("TANGGAL")
    saldo = 0
    saldo_list = []
    for i in range(len(df)):
        saldo += df.iloc[i]["DEBET"] - df.iloc[i]["KREDIT"]
        saldo_list.append(saldo)
    df["SALDO"] = saldo_list
    return df

# ================= DOWNLOAD EXCEL =================
def download_excel(df, nama):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    st.download_button("DOWNLOAD EXCEL", output, f"{nama}.xlsx")

# ================= LOGIN =================
if not st.session_state.login:

    st.markdown('<div class="center-box">', unsafe_allow_html=True)
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

    st.markdown("<br><b>Created by : Admin Smakece</b>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= HALAMAN UTAMA =================
else:

    st.sidebar.title("MENU UTAMA")
    menu = st.sidebar.selectbox("PILIH MENU",[

        "INPUT TRANSAKSI",
        "BUKU KAS DANA SOSIAL",
        "BUKU KAS DHARMA WANITA",
        "BUKU KAS KORPRI",
        "LAPORAN DANA SOSIAL",
        "LAPORAN DHARMA WANITA",
        "LAPORAN KORPRI",
        "UPLOAD BUKTI TRANSAKSI",
        "UPLOAD FOTO KEGIATAN",
        "LOG OUT"
    ])

    # ================= INPUT =================
    if menu == "INPUT TRANSAKSI":

        with st.form("form_transaksi"):
            jenis = st.selectbox("JENIS KAS",
                                 ["DANA SOSIAL","DHARMA WANITA","KORPRI"])
            tanggal = st.date_input("TANGGAL")
            uraian = st.text_input("URAIAN TRANSAKSI")
            debet = st.number_input("DEBET (MASUK)", min_value=0)
            kredit = st.number_input("KREDIT (KELUAR)", min_value=0)

            col1, col2 = st.columns(2)
            simpan = col1.form_submit_button("SIMPAN")
            batal = col2.form_submit_button("BATAL")

        if simpan:
            data = {
                "TANGGAL": tanggal,
                "URAIAN": uraian.upper(),
                "DEBET": debet,
                "KREDIT": kredit,
                "SALDO": 0
            }

            key = "dana" if jenis=="DANA SOSIAL" else \
                  "dharma" if jenis=="DHARMA WANITA" else "korpri"

            df = st.session_state[key]
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            st.session_state[key] = hitung_saldo(df)

            st.success("DATA BERHASIL DISIMPAN")

        if batal:
            st.rerun()

    # ================= UPLOAD BUKTI TRANSAKSI =================
    if menu == "UPLOAD BUKTI TRANSAKSI":

        st.header("UPLOAD BUKTI TRANSAKSI")

        file = st.file_uploader("PILIH FILE BUKTI", type=["jpg","png","pdf"])

        if file is not None:
            file_path = os.path.join("upload_bukti_transaksi", file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            st.success("FILE BERHASIL DIUPLOAD")

        files = os.listdir("upload_bukti_transaksi")
        if files:
            st.subheader("DAFTAR FILE")
            for f in files:
                with open(os.path.join("upload_bukti_transaksi", f), "rb") as file:
                    st.download_button(f"DOWNLOAD {f}", file, f)

    # ================= UPLOAD FOTO KEGIATAN =================
    if menu == "UPLOAD FOTO KEGIATAN":

        st.header("UPLOAD FOTO KEGIATAN")

        file = st.file_uploader("PILIH FOTO", type=["jpg","png"])

        if file is not None:
            file_path = os.path.join("upload_kegiatan", file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            st.success("FOTO BERHASIL DIUPLOAD")

        files = os.listdir("upload_kegiatan")
        if files:
            st.subheader("DAFTAR FOTO")
            for f in files:
                with open(os.path.join("upload_kegiatan", f), "rb") as file:
                    st.download_button(f"DOWNLOAD {f}", file, f)

    # ================= LOG OUT =================
    if menu == "LOG OUT":
        st.session_state.login = False
        st.rerun()
