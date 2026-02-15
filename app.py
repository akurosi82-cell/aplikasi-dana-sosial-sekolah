import streamlit as st
import pandas as pd
import sqlite3
import datetime
import calendar
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

st.set_page_config(page_title="KEUANGAN SMK", layout="wide")

# ================= DATABASE =================
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS transaksi
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              tanggal TEXT,
              jenis_kas TEXT,
              uraian TEXT,
              debet REAL,
              kredit REAL,
              saldo REAL)''')
conn.commit()

# ================= GOOGLE DRIVE =================
FOLDER_TRANSAKSI = "1AJ2ZjiFLNuTQufuPcEvFbdf-wFMtcr3c"
FOLDER_KEGIATAN = "1W7Yg8VNOQeBhzoX5lVf3WrMDGmt6WDg5"

def connect_drive():
    credentials = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)

def upload_drive(file, folder_id):
    service = connect_drive()
    file_metadata = {"name": file.name, "parents": [folder_id]}
    media = MediaIoBaseUpload(file, mimetype=file.type)
    service.files().create(body=file_metadata, media_body=media).execute()

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

def login_page():
    st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
    st.image("logo.png", width=150)
    st.title("APLIKASI PENGELOLAAN KEUANGAN")
    st.subheader("SMK NEGERI 1 CERMEE BONDOWOSO")
    st.markdown("</div>", unsafe_allow_html=True)

    user = st.text_input("USERNAME")
    pwd = st.text_input("PASSWORD", type="password")

    if st.button("LOGIN"):
        if user == "admin" and pwd == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("USERNAME / PASSWORD SALAH")

    st.markdown("<center>Created by : Admin Smakece</center>", unsafe_allow_html=True)

if not st.session_state.login:
    login_page()
    st.stop()

# ================= LOGOUT =================
if st.sidebar.button("LOG OUT"):
    st.session_state.login = False
    st.rerun()

# ================= MENU =================
menu = st.sidebar.selectbox("MENU", [
    "INPUT TRANSAKSI",
    "BUKU KAS",
    "LAPORAN",
    "UPLOAD FILE"
])

# ================= INPUT =================
if menu == "INPUT TRANSAKSI":
    st.header("INPUT TRANSAKSI")

    tanggal = st.date_input("TANGGAL", datetime.date.today())
    jenis = st.selectbox("JENIS KAS", ["DANA SOSIAL","DHARMA WANITA","KORPRI"])
    uraian = st.text_input("URAIAN")
    tipe = st.radio("JENIS", ["MASUK","KELUAR"])
    nominal = st.number_input("NOMINAL", min_value=0)

    if st.button("SIMPAN"):
        c.execute("SELECT saldo FROM transaksi WHERE jenis_kas=? ORDER BY id DESC LIMIT 1",(jenis,))
        last = c.fetchone()
        saldo_awal = last[0] if last else 0

        debet = nominal if tipe=="MASUK" else 0
        kredit = nominal if tipe=="KELUAR" else 0
        saldo_baru = saldo_awal + debet - kredit

        c.execute("INSERT INTO transaksi (tanggal,jenis_kas,uraian,debet,kredit,saldo) VALUES (?,?,?,?,?,?)",
                  (str(tanggal),jenis,uraian,debet,kredit,saldo_baru))
        conn.commit()
        st.success("DATA BERHASIL DISIMPAN")

# ================= BUKU KAS =================
if menu == "BUKU KAS":
    jenis = st.selectbox("PILIH BUKU KAS", ["DANA SOSIAL","DHARMA WANITA","KORPRI"])
    df = pd.read_sql_query("SELECT * FROM transaksi WHERE jenis_kas=?", conn, params=(jenis,))

    if not df.empty:
        df["NOMER"] = range(1,len(df)+1)
        df = df[["id","NOMER","tanggal","uraian","debet","kredit","saldo"]]
        df.columns = ["ID","NOMER","TANGGAL","URAIAN","DEBET","KREDIT","SALDO"]

        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)

        id_hapus = st.number_input("MASUKKAN ID YANG AKAN DIHAPUS", min_value=0)
        if st.button("HAPUS DATA"):
            c.execute("DELETE FROM transaksi WHERE id=?", (id_hapus,))
            conn.commit()
            st.warning("DATA DIHAPUS")

        output = BytesIO()
        df.drop(columns=["ID"]).to_excel(output,index=False)
        st.download_button("DOWNLOAD EXCEL",output.getvalue(),file_name=f"BUKU_KAS_{jenis}.xlsx")

# ================= LAPORAN =================
if menu == "LAPORAN":
    jenis = st.selectbox("PILIH LAPORAN", ["DANA SOSIAL","DHARMA WANITA","KORPRI"])
    df = pd.read_sql_query("SELECT * FROM transaksi WHERE jenis_kas=?", conn, params=(jenis,))

    if not df.empty:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        laporan_list = []

        for bulan in range(1,13):
            akhir_bulan = datetime.date(datetime.date.today().year, bulan, calendar.monthrange(datetime.date.today().year, bulan)[1])
            debet = df[df["tanggal"].dt.month==bulan]["debet"].sum()
            kredit = df[df["tanggal"].dt.month==bulan]["kredit"].sum()
            saldo = debet - kredit
            laporan_list.append([bulan, akhir_bulan, debet, kr_]()_
