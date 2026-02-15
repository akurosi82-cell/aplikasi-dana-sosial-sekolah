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

# ================= STYLE =================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #e3f2fd, #ffffff);
}
.login-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.login-box {
    width: 420px;
    padding: 40px;
    background: white;
    border-radius: 15px;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.2);
    text-align: center;
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
h2,h3 {color:#003366;}
</style>
""", unsafe_allow_html=True)

# ================= BULAN =================
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

# ================= DOWNLOAD =================
def download_excel(df, nama):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    st.download_button("DOWNLOAD EXCEL", output, f"{nama}.xlsx")

# ================= LOGIN =================
if not st.session_state.login:

    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.image("logo.png", width=150)
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

# ================= HALAMAN UTAMA =================
else:

    st.sidebar.title("MENU UTAMA")
    menu = st.sidebar.selectbox("PILIH MENU",[
        "INPUT TRANSAKSI",
        "BUKU KAS DANA SOSIAL",
        "BUKU KAS DHARMA WANITA",
        "BUKU KAS KORPRI",
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

    # ================= BUKU KAS + REKAP BARU =================
    def tampil_buku(df,nama):

        if df.empty:
            st.info("Belum ada data")
            return

        df = df.sort_values("TANGGAL")
        df_show = df.copy()
        df_show.insert(0,"NOMER",range(1,len(df_show)+1))
        df_show["TANGGAL"] = pd.to_datetime(df_show["TANGGAL"]).dt.strftime("%Y-%m-%d")

        st.subheader("BUKU KAS")
        st.dataframe(df_show,use_container_width=True)
        download_excel(df_show,nama)

        # ================= REKAP BARU =================
        st.subheader("REKAP KAS BULANAN")

        df["TANGGAL"] = pd.to_datetime(df["TANGGAL"])
        df["BULAN"] = df["TANGGAL"].dt.month
        df["TAHUN"] = df["TANGGAL"].dt.year

        tahun = df["TAHUN"].max()

        rekap_data = []
        saldo_berjalan = 0

        for bulan in range(1,13):
            df_bulan = df[df["BULAN"]==bulan]

            debet = df_bulan["DEBET"].sum()
            kredit = df_bulan["KREDIT"].sum()
            saldo_berjalan += debet - kredit

            tanggal_akhir = datetime(tahun,bulan,
                            calendar.monthrange(tahun,bulan)[1])

            uraian = f"REKAP BULAN {bulan_indo[bulan]}"

            rekap_data.append([
                bulan,
                tanggal_akhir.strftime("%Y-%m-%d"),
                uraian,
                debet,
                kredit,
                saldo_berjalan
            ])

        df_rekap = pd.DataFrame(rekap_data,
            columns=["NOMER","TANGGAL","URAIAN TRANSAKSI","DEBET","KREDIT","SALDO"])

        st.dataframe(df_rekap,use_container_width=True)
        download_excel(df_rekap,f"REKAP_{nama}")

    if menu=="BUKU KAS DANA SOSIAL":
        tampil_buku(st.session_state["dana"],"DANA_SOSIAL")

    if menu=="BUKU KAS DHARMA WANITA":
        tampil_buku(st.session_state["dharma"],"DHARMA_WANITA")

    if menu=="BUKU KAS KORPRI":
        tampil_buku(st.session_state["korpri"],"KORPRI")

    # ================= LOG OUT =================
    if menu=="LOG OUT":
        st.session_state.login=False
        st.rerun()
