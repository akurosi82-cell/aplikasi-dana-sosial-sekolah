import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# =====================================
# KONFIGURASI HALAMAN
# =====================================
st.set_page_config(
    page_title="Aplikasi Dana Sosial Sekolah",
    page_icon="💰",
    layout="wide"
)

# =====================================
# STYLE
# =====================================
st.markdown("""
<style>
.main {background-color: #f4f6f9;}
.center-box {
    width: 420px;
    margin: auto;
    text-align: center;
    padding-top: 60px;
}
.stButton>button {
    background-color: #003366;
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
}
.stButton>button:hover {
    background-color: #0055aa;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# BULAN INDONESIA
# =====================================
bulan_indo = {
    1:"JANUARI",2:"FEBRUARI",3:"MARET",4:"APRIL",
    5:"MEI",6:"JUNI",7:"JULI",8:"AGUSTUS",
    9:"SEPTEMBER",10:"OKTOBER",11:"NOVEMBER",12:"DESEMBER"
}

# =====================================
# SESSION
# =====================================
if "login" not in st.session_state:
    st.session_state.login = False

def init_df():
    return pd.DataFrame(columns=["TANGGAL","URAIAN","DEBET","KREDIT","SALDO"])

for kas in ["dana","dharma","korpri"]:
    if kas not in st.session_state:
        st.session_state[kas] = init_df()

# =====================================
# HITUNG SALDO
# =====================================
def hitung_saldo(df):
    df = df.sort_values("TANGGAL")
    saldo = 0
    saldo_list = []
    for i in range(len(df)):
        saldo += df.iloc[i]["DEBET"] - df.iloc[i]["KREDIT"]
        saldo_list.append(saldo)
    df["SALDO"] = saldo_list
    return df

# =====================================
# DOWNLOAD EXCEL
# =====================================
def download_excel(df, nama):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    st.download_button("📥 DOWNLOAD EXCEL", output, f"{nama}.xlsx")

# =====================================
# LOGIN
# =====================================
if not st.session_state.login:

    st.markdown('<div class="center-box">', unsafe_allow_html=True)

    st.image("logo.png", width=180)
    st.markdown("<h2>APLIKASI PENGELOLAAN DANA SOSIAL SEKOLAH</h2>", unsafe_allow_html=True)
    st.markdown("<h3>SMK NEGERI 1 CERMEE BONDOWOSO</h3>", unsafe_allow_html=True)

    username = st.text_input("USERNAME")
    password = st.text_input("PASSWORD", type="password")

    if st.button("LOGIN"):
        if username == "admin" and password == "1234":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username / Password Salah")

    st.markdown("<br><b>Created by : Admin Smakece</b>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =====================================
# HALAMAN UTAMA
# =====================================
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
        "LOGOUT"
    ])

    # =====================================
    # INPUT TRANSAKSI
    # =====================================
    if menu == "INPUT TRANSAKSI":
        jenis = st.selectbox("JENIS KAS",["DANA SOSIAL","DHARMA WANITA","KORPRI"])
        tanggal = st.date_input("TANGGAL")
        uraian = st.text_input("URAIAN TRANSAKSI")
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

    # =====================================
    # BUKU KAS + REKAP DETAIL PER BULAN
    # =====================================
    def tampil_buku(df,nama):

        if df.empty:
            st.info("Belum ada data")
            return

        df=df.sort_values("TANGGAL")
        df_show=df.copy()
        df_show.insert(0,"NOMER",range(1,len(df_show)+1))
        df_show["TANGGAL"]=pd.to_datetime(df_show["TANGGAL"]).dt.strftime("%Y-%m-%d")

        st.subheader("BUKU KAS")
        st.dataframe(df_show,use_container_width=True)
        download_excel(df_show,nama)

        if st.button("🗑 HAPUS DATA BUKU KAS"):
            df.drop(df.index,inplace=True)
            st.success("Data Buku Kas Dihapus")
            st.rerun()

        # =====================================
        # REKAP PER BULAN DETAIL
        # =====================================
        st.subheader("REKAP KAS PER BULAN (DETAIL TRANSAKSI)")

        bulan_pilih = st.selectbox("PILIH BULAN", list(bulan_indo.values()))

        bulan_index = list(bulan_indo.values()).index(bulan_pilih) + 1

        df["BULAN"]=pd.to_datetime(df["TANGGAL"]).dt.month
        df_bulan=df[df["BULAN"]==bulan_index].copy()

        if df_bulan.empty:
            st.info("Tidak ada transaksi bulan ini")
        else:
            df_bulan.insert(0,"NOMER",range(1,len(df_bulan)+1))
            df_bulan=df_bulan[["NOMER","URAIAN","DEBET","KREDIT","SALDO"]]
            df_bulan.columns=["NOMER","URAIAN TRANSAKSI","DEBET","KREDIT","SALDO"]

            st.dataframe(df_bulan,use_container_width=True)

    if menu=="BUKU KAS DANA SOSIAL":
        tampil_buku(st.session_state["dana"],"BUKU KAS DANA SOSIAL")

    if menu=="BUKU KAS DHARMA WANITA":
        tampil_buku(st.session_state["dharma"],"BUKU KAS DHARMA WANITA")

    if menu=="BUKU KAS KORPRI":
        tampil_buku(st.session_state["korpri"],"BUKU KAS KORPRI")

    # =====================================
    # LAPORAN BULANAN
    # =====================================
    def laporan(df,nama):

        if df.empty:
            st.info("Belum ada data")
            return

        df["TANGGAL"]=pd.to_datetime(df["TANGGAL"])
        laporan=[]
        saldo_akhir_tahun=0

        for bulan in range(1,13):
            df_bulan=df[df["TANGGAL"].dt.month==bulan]
            debet=df_bulan["DEBET"].sum()
            kredit=df_bulan["KREDIT"].sum()
            saldo=debet-kredit
            saldo_akhir_tahun+=saldo

            uraian=f"SALDO AKHIR {bulan_indo[bulan]}"
            laporan.append([bulan,uraian,debet,kredit,saldo])

        laporan.append(["","SALDO AKHIR TAHUN","","",saldo_akhir_tahun])

        df_laporan=pd.DataFrame(laporan,
            columns=["NOMER","URAIAN","DEBET","KREDIT","SALDO"])

        st.dataframe(df_laporan,use_container_width=True)
        download_excel(df_laporan,nama)

        if st.button("🗑 HAPUS LAPORAN"):
            st.success("Laporan Akan Dihitung Ulang Otomatis")
            st.rerun()

    if menu=="LAPORAN DANA SOSIAL":
        laporan(st.session_state["dana"].copy(),"LAPORAN DANA SOSIAL")

    if menu=="LAPORAN DHARMA WANITA":
        laporan(st.session_state["dharma"].copy(),"LAPORAN DHARMA WANITA")

    if menu=="LAPORAN KORPRI":
        laporan(st.session_state["korpri"].copy(),"LAPORAN KORPRI")

    # =====================================
    # LOGOUT
    # =====================================
    if menu=="LOGOUT":
        st.session_state.login=False
        st.rerun()
