import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import calendar

# ==============================
# KONFIGURASI HALAMAN
# ==============================
st.set_page_config(
    page_title="Aplikasi Dana Sosial Sekolah",
    page_icon="💰",
    layout="wide"
)

# ==============================
# CSS TAMPILAN ELEGAN
# ==============================
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
h1, h2, h3 {
    color: #003366;
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
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# SESSION STATE
# ==============================
if "login" not in st.session_state:
    st.session_state.login = False

def init_kas():
    return pd.DataFrame(columns=["TANGGAL", "URAIAN", "DEBET", "KREDIT", "SALDO"])

if "dana_sosial" not in st.session_state:
    st.session_state.dana_sosial = init_kas()

if "dharma_wanita" not in st.session_state:
    st.session_state.dharma_wanita = init_kas()

if "korpri" not in st.session_state:
    st.session_state.korpri = init_kas()

# ==============================
# FUNGSI HITUNG SALDO
# ==============================
def hitung_saldo(df):
    saldo = 0
    saldo_list = []
    for i in range(len(df)):
        saldo += df.loc[i, "DEBET"] - df.loc[i, "KREDIT"]
        saldo_list.append(saldo)
    df["SALDO"] = saldo_list
    return df

# ==============================
# FUNGSI DOWNLOAD EXCEL
# ==============================
def download_excel(df, nama_file):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        "📥 DOWNLOAD EXCEL",
        data=output,
        file_name=f"{nama_file}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==============================
# LOGIN PAGE
# ==============================
if not st.session_state.login:

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.image("logo.png", width=180)

        st.markdown("<h2 style='text-align:center;'>APLIKASI PENGELOLAAN DANA SOSIAL SEKOLAH</h2>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;'>SMK NEGERI 1 CERMEE BONDOWOSO</h3>", unsafe_allow_html=True)

        st.markdown("---")

        username = st.text_input("USERNAME")
        password = st.text_input("PASSWORD", type="password")

        if st.button("LOGIN"):
            if username == "admin" and password == "1234":
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Username atau Password Salah")

        st.markdown("<br><center><b>Created by : Admin Smakece</b></center>", unsafe_allow_html=True)

# ==============================
# HALAMAN UTAMA
# ==============================
else:

    st.sidebar.title("📂 MENU")
    menu = st.sidebar.selectbox("PILIH MENU", [
        "INPUT TRANSAKSI",
        "BUKU KAS DANA SOSIAL",
        "BUKU KAS DHARMA WANITA",
        "BUKU KAS KORPRI",
        "LAPORAN DANA SOSIAL",
        "LAPORAN DHARMA WANITA",
        "LAPORAN KORPRI",
        "LOGOUT"
    ])

    # ==============================
    # INPUT TRANSAKSI
    # ==============================
    if menu == "INPUT TRANSAKSI":

        st.header("INPUT TRANSAKSI")

        jenis = st.selectbox("JENIS KAS", ["DANA SOSIAL", "DHARMA WANITA", "KORPRI"])
        tanggal = st.date_input("TANGGAL")
        uraian = st.text_input("URAIAN TRANSAKSI")
        debet = st.number_input("DEBET (MASUK)", min_value=0)
        kredit = st.number_input("KREDIT (KELUAR)", min_value=0)

        if st.button("SIMPAN DATA"):
            data = {
                "TANGGAL": tanggal.strftime("%Y-%m-%d"),
                "URAIAN": uraian.upper(),
                "DEBET": debet,
                "KREDIT": kredit,
                "SALDO": 0
            }

            if jenis == "DANA SOSIAL":
                df = st.session_state.dana_sosial
                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
                st.session_state.dana_sosial = hitung_saldo(df)

            elif jenis == "DHARMA WANITA":
                df = st.session_state.dharma_wanita
                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
                st.session_state.dharma_wanita = hitung_saldo(df)

            else:
                df = st.session_state.korpri
                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
                st.session_state.korpri = hitung_saldo(df)

            st.success("✅ Data berhasil disimpan")

    # ==============================
    # TAMPILKAN BUKU KAS
    # ==============================
    def tampilkan_buku(df, nama):
        st.header(nama)

        if df.empty:
            st.info("Belum ada data")
            return

        df_display = df.copy()
        df_display.insert(0, "NOMER", range(1, len(df_display)+1))

        st.dataframe(df_display, use_container_width=True)

        download_excel(df_display, nama)

        if st.button("🗑 HAPUS SEMUA DATA"):
            df.drop(df.index, inplace=True)
            st.success("Data berhasil dihapus")
            st.rerun()

    if menu == "BUKU KAS DANA SOSIAL":
        tampilkan_buku(st.session_state.dana_sosial, "BUKU KAS DANA SOSIAL")

    if menu == "BUKU KAS DHARMA WANITA":
        tampilkan_buku(st.session_state.dharma_wanita, "BUKU KAS DHARMA WANITA")

    if menu == "BUKU KAS KORPRI":
        tampilkan_buku(st.session_state.korpri, "BUKU KAS KORPRI")

    # ==============================
    # LAPORAN BULANAN
    # ==============================
    def laporan(df, nama):
        st.header(nama)

        if df.empty:
            st.info("Belum ada data")
            return

        df["TANGGAL"] = pd.to_datetime(df["TANGGAL"])
        tahun = df["TANGGAL"].dt.year.max()

        laporan_data = []

        for bulan in range(1, 13):
            df_bulan = df[df["TANGGAL"].dt.month == bulan]
            debet = df_bulan["DEBET"].sum()
            kredit = df_bulan["KREDIT"].sum()
            saldo = debet - kredit
            akhir = datetime(tahun, bulan, calendar.monthrange(tahun, bulan)[1]).strftime("%Y-%m-%d")

            laporan_data.append([bulan, akhir, debet, kredit, saldo])

        df_laporan = pd.DataFrame(
            laporan_data,
            columns=["NOMER", "TANGGAL", "DEBET", "KREDIT", "SALDO"]
        )

        st.dataframe(df_laporan, use_container_width=True)

        download_excel(df_laporan, nama)

    if menu == "LAPORAN DANA SOSIAL":
        laporan(st.session_state.dana_sosial.copy(), "LAPORAN DANA SOSIAL")

    if menu == "LAPORAN DHARMA WANITA":
        laporan(st.session_state.dharma_wanita.copy(), "LAPORAN DHARMA WANITA")

    if menu == "LAPORAN KORPRI":
        laporan(st.session_state.korpri.copy(), "LAPORAN KORPRI")

    # ==============================
    # LOGOUT
    # ==============================
    if menu == "LOGOUT":
        st.session_state.login = False
        st.rerun()
