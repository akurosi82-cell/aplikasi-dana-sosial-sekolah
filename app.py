import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import calendar

# GOOGLE DRIVE
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# =============================
# KONFIGURASI
# =============================
st.set_page_config(page_title="Dana Sosial Sekolah", layout="wide")

# =============================
# GOOGLE DRIVE SETUP
# =============================
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_TRANSAKSI = "1AJ2ZjiFLNuTQufuPcEvFbdf-wFMtcr3c"
FOLDER_KEGIATAN = "1W7Yg8VNOQeBhzoX5lVf3WrMDGmt6WDg5"

def upload_to_drive(uploaded_file, folder_id):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gdrive"], scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': uploaded_file.name,
        'parents': [folder_id]
    }

    media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)

    service.files().create(body=file_metadata, media_body=media).execute()

# =============================
# SESSION
# =============================
if "login" not in st.session_state:
    st.session_state.login = False

def init_df():
    return pd.DataFrame(columns=["TANGGAL","URAIAN","DEBET","KREDIT","SALDO"])

for kas in ["dana","dharma","korpri"]:
    if kas not in st.session_state:
        st.session_state[kas] = init_df()

# =============================
# HITUNG SALDO
# =============================
def hitung_saldo(df):
    df = df.sort_values("TANGGAL")
    saldo = 0
    saldo_list = []
    for i in range(len(df)):
        saldo += df.iloc[i]["DEBET"] - df.iloc[i]["KREDIT"]
        saldo_list.append(saldo)
    df["SALDO"] = saldo_list
    return df

# =============================
# DOWNLOAD EXCEL
# =============================
def download_excel(df, nama):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button("📥 DOWNLOAD EXCEL", output, f"{nama}.xlsx")

# =============================
# LOGIN PAGE
# =============================
if not st.session_state.login:

    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        st.image("logo.png", width=200)
        st.markdown("<h2 style='text-align:center;'>APLIKASI PENGELOLAAN DANA SOSIAL SEKOLAH</h2>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;'>SMK NEGERI 1 CERMEE BONDOWOSO</h3>", unsafe_allow_html=True)

        username = st.text_input("USERNAME")
        password = st.text_input("PASSWORD", type="password")

        if st.button("LOGIN"):
            if username=="admin" and password=="1234":
                st.session_state.login=True
                st.rerun()
            else:
                st.error("Username / Password Salah")

        st.markdown("<center>Created by : Admin Smakece</center>", unsafe_allow_html=True)

# =============================
# HALAMAN UTAMA
# =============================
else:

    st.sidebar.title("MENU")
    menu = st.sidebar.selectbox("PILIH MENU",[
        "INPUT TRANSAKSI",
        "BUKU KAS DANA SOSIAL",
        "BUKU KAS DHARMA WANITA",
        "BUKU KAS KORPRI",
        "LAPORAN DANA SOSIAL",
        "LAPORAN DHARMA WANITA",
        "LAPORAN KORPRI",
        "UPLOAD FILE",
        "LOGOUT"
    ])

    # =============================
    # INPUT TRANSAKSI
    # =============================
    if menu=="INPUT TRANSAKSI":
        jenis = st.selectbox("JENIS KAS",["DANA SOSIAL","DHARMA WANITA","KORPRI"])
        tanggal = st.date_input("TANGGAL")
        uraian = st.text_input("URAIAN")
        debet = st.number_input("DEBET",min_value=0)
        kredit = st.number_input("KREDIT",min_value=0)

        if st.button("SIMPAN"):
            data={
                "TANGGAL":tanggal,
                "URAIAN":uraian.upper(),
                "DEBET":debet,
                "KREDIT":kredit,
                "SALDO":0
            }

            key="dana" if jenis=="DANA SOSIAL" else "dharma" if jenis=="DHARMA WANITA" else "korpri"
            df=st.session_state[key]
            df=pd.concat([df,pd.DataFrame([data])],ignore_index=True)
            st.session_state[key]=hitung_saldo(df)
            st.success("Data Disimpan")

    # =============================
    # BUKU KAS
    # =============================
    def tampil_buku(df,nama):
        if df.empty:
            st.info("Belum ada data")
            return

        df=df.sort_values("TANGGAL")
        df_show=df.copy()
        df_show.insert(0,"NOMER",range(1,len(df_show)+1))
        df_show["TANGGAL"]=pd.to_datetime(df_show["TANGGAL"]).dt.strftime("%Y-%m-%d")

        st.dataframe(df_show,use_container_width=True)
        download_excel(df_show,nama)

        # REKAP BULANAN
        st.subheader("REKAP KAS BULANAN")
        df["BULAN"]=pd.to_datetime(df["TANGGAL"]).dt.month
        rekap=df.groupby("BULAN")[["DEBET","KREDIT"]].sum().reset_index()
        st.dataframe(rekap,use_container_width=True)

        if st.button("HAPUS DATA"):
            df.drop(df.index,inplace=True)
            st.success("Data Dihapus")
            st.rerun()

    if menu=="BUKU KAS DANA SOSIAL":
        tampil_buku(st.session_state["dana"],"BUKU KAS DANA SOSIAL")

    if menu=="BUKU KAS DHARMA WANITA":
        tampil_buku(st.session_state["dharma"],"BUKU KAS DHARMA WANITA")

    if menu=="BUKU KAS KORPRI":
        tampil_buku(st.session_state["korpri"],"BUKU KAS KORPRI")

    # =============================
    # LAPORAN
    # =============================
    def laporan(df,nama):
        if df.empty:
            st.info("Belum ada data")
            return

        df["TANGGAL"]=pd.to_datetime(df["TANGGAL"])
        tahun=df["TANGGAL"].dt.year.max()
        laporan=[]
        saldo_akhir_tahun=0

        for bulan in range(1,13):
            df_bulan=df[df["TANGGAL"].dt.month==bulan]
            debet=df_bulan["DEBET"].sum()
            kredit=df_bulan["KREDIT"].sum()
            saldo=debet-kredit
            saldo_akhir_tahun+=saldo

            akhir=datetime(tahun,bulan,calendar.monthrange(tahun,bulan)[1]).strftime("%Y-%m-%d")
            uraian=f"SALDO AKHIR {calendar.month_name[bulan].upper()}"
            laporan.append([bulan,akhir,uraian,debet,kredit,saldo])

        laporan.append(["","","SALDO AKHIR TAHUN","","",saldo_akhir_tahun])

        df_laporan=pd.DataFrame(laporan,columns=["NOMER","TANGGAL","URAIAN","DEBET","KREDIT","SALDO"])

        st.dataframe(df_laporan,use_container_width=True)
        download_excel(df_laporan,nama)

        if st.button("HAPUS LAPORAN"):
            st.success("Laporan Akan Dihitung Ulang Otomatis")
            st.rerun()

    if menu=="LAPORAN DANA SOSIAL":
        laporan(st.session_state["dana"].copy(),"LAPORAN DANA SOSIAL")

    if menu=="LAPORAN DHARMA WANITA":
        laporan(st.session_state["dharma"].copy(),"LAPORAN DHARMA WANITA")

    if menu=="LAPORAN KORPRI":
        laporan(st.session_state["korpri"].copy(),"LAPORAN KORPRI")

    # =============================
    # UPLOAD FILE
    # =============================
    if menu=="UPLOAD FILE":
        st.subheader("UPLOAD BUKTI TRANSAKSI")
        file1=st.file_uploader("Upload Bukti Transaksi")
        if file1 and st.button("UPLOAD TRANSAKSI"):
            upload_to_drive(file1,FOLDER_TRANSAKSI)
            st.success("Berhasil Upload")

        st.subheader("UPLOAD FOTO KEGIATAN")
        file2=st.file_uploader("Upload Foto Kegiatan")
        if file2 and st.button("UPLOAD KEGIATAN"):
            upload_to_drive(file2,FOLDER_KEGIATAN)
            st.success("Berhasil Upload")

    # =============================
    # LOGOUT
    # =============================
    if menu=="LOGOUT":
        st.session_state.login=False
        st.rerun()
