# STREAMLIT DASHBOARD
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# PAGE CONFIG
st.set_page_config(
    page_title="IDX Financial Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data.csv")
    df['Year'] = df['Year'].astype(int)
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    return df

df = load_data()


# SIDEBAR FILTERS (GLOBAL)
st.sidebar.header("📊 Filter Data")
st.sidebar.markdown("### 🔍 Filter Global")

years = sorted(df["Year"].unique())
symbols = sorted(df["symbol"].unique())
accounts = sorted(df["account"].unique())

selected_year = st.sidebar.multiselect("Pilih Tahun", years, default=years)
selected_symbol = st.sidebar.multiselect("Pilih Perusahaan (symbol)", symbols)
selected_account = st.sidebar.multiselect("Pilih Jenis Akun", accounts)

# Menggunakan df_filtered untuk seluruh halaman
df_filtered = df[
    df["Year"].isin(selected_year) &
    df["symbol"].isin(selected_symbol if selected_symbol else symbols) &
    df["account"].isin(selected_account if selected_account else accounts)
]

# MAIN TITLE
st.title("📈 Dashboard Laporan Keuangan Emiten IDX (2020 - 2023)")
st.markdown("Visualisasi data laporan keuangan perusahaan publik Indonesia berdasarkan dataset dari IDX.")

# INFORMASI DATA 
total_companies = df_filtered["symbol"].nunique()
total_accounts = df_filtered["account"].nunique()
total_years = df_filtered["Year"].nunique()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💼 Jumlah Perusahaan", total_companies)
with col2:
    st.metric("📊 Jumlah Jenis Akun", total_accounts)
with col3:
    st.metric("📅 Jumlah Tahun Data", total_years)

st.markdown("---")

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏢 Company Detail", "📈 Comparison", "🔎 Analysis"])


# TAB 1: OVERVIEW 
with tab1:
    st.header("📊 Ikhtisar Keuangan Perusahaan Publik Indonesia (2020-2023)")
    st.markdown("""
    Halaman ini menampilkan tren dan ringkasan utama dari laporan keuangan perusahaan publik di Indonesia 
    berdasarkan data yang diakses dari [Kaggle](https://www.kaggle.com/datasets/kalkulasi/financial-statement-data-idx-2020-2023).
    """)

    # Mengganti df → df_filtered
    symbols_filtered = sorted(df_filtered['symbol'].unique())
    selected_symbol_overview = st.selectbox("🏢 Pilih Perusahaan", options=symbols_filtered)

    df_symbol = df_filtered[df_filtered['symbol'] == selected_symbol_overview]

    top_n = st.slider("Pilih jumlah akun teratas untuk ditampilkan:", 3, 15, 5)
    top_accounts = (
        df_symbol.groupby("account")["Value"]
        .sum()
        .nlargest(top_n)
        .index
    )
    df_top = df_symbol[df_symbol["account"].isin(top_accounts)]

    fig = px.area(
        df_top,
        x="Year",
        y="Value",
        color="account",
        markers=True,
        title=f"Tren Nilai {top_n} Akun Teratas - {selected_symbol_overview}",
    )
    fig.update_layout(
        xaxis_title="Tahun",
        yaxis_title="Nilai (dalam miliar atau satuan asli)",
        legend_title="Akun",
        hovermode="x unified",
        title_x=0.5,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Filter global
    total_value_2023 = df_symbol[df_symbol['Year'] == 2023]['Value'].sum()
    total_value_2020 = df_symbol[df_symbol['Year'] == 2020]['Value'].sum()
    growth = ((total_value_2023 - total_value_2020) / total_value_2020) * 100 if total_value_2020 != 0 else 0

    st.markdown("### 💡 Ringkasan:")
    st.info(
        f"Total nilai akun perusahaan **{selected_symbol_overview}** pada tahun 2023 mencapai **{total_value_2023:,.0f}**, "
        f"mengalami perubahan sebesar **{growth:.2f}%** dibanding tahun 2020."
    )


# TAB 2: COMPANY DETAIL 
with tab2:
    st.subheader("🏢 Detail Perusahaan")

    # Mengambil dari df_filtered
    symbols_filtered = sorted(df_filtered['symbol'].unique())
    company = st.selectbox("Pilih Perusahaan", symbols_filtered)

    df_company = df_filtered[df_filtered["symbol"] == company]

    fig2 = px.line(
        df_company,
        x="Year", y="Value", color="account",
        title=f"Tren Nilai Akun untuk {company}",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

    latest_year = df_company["Year"].max()
    df_latest = df_company[df_company["Year"] == latest_year]

    st.markdown(f"**Nilai Akun pada Tahun {latest_year}:**")
    st.dataframe(df_latest[["account", "Value"]].sort_values(by="Value", ascending=False))


# TAB 3: COMPARISON
with tab3:
    st.subheader("📈 Perbandingan antar Perusahaan")

    # Akun dan tahun dari df_filtered
    accounts_filtered = sorted(df_filtered["account"].unique())
    years_filtered = sorted(df_filtered["Year"].unique())

    comp_account = st.selectbox("Pilih Akun untuk Dibandingkan", accounts_filtered)
    comp_year = st.selectbox("Pilih Tahun", years_filtered)

    df_comp = df_filtered[
        (df_filtered["account"] == comp_account) & (df_filtered["Year"] == comp_year)
    ]

    fig3 = px.bar(
        df_comp.sort_values("Value", ascending=False).head(20),
        x="symbol", y="Value",
        title=f"Perbandingan {comp_account} antar Emiten pada {comp_year}",
        color="symbol"
    )
    st.plotly_chart(fig3, use_container_width=True)


# TAB 4: ANALYSIS
with tab4:
    st.subheader("🔎 Korelasi antar Akun")

    # Menggunkan tahun dari df_filtered
    corr_year = st.selectbox("Pilih Tahun untuk Analisis Korelasi", sorted(df_filtered["Year"].unique()))

    df_corr = df_filtered[df_filtered["Year"] == corr_year]

    df_pivot = df_corr.pivot_table(
        index="symbol", columns="account", values="Value", aggfunc="mean"
    ).fillna(0)

    corr_matrix = df_pivot.corr()

    fig4 = px.imshow(
        corr_matrix,
        text_auto=False,
        aspect="auto",
        title=f"Heatmap Korelasi antar Akun ({corr_year})",
        color_continuous_scale="YlGnBu",
        width=1200,
        height=800
    )

    fig4.update_layout(
        xaxis=dict(tickangle=45, tickfont=dict(size=9), automargin=True),
        yaxis=dict(tickfont=dict(size=9), automargin=True),
        margin=dict(l=120, r=120, t=80, b=150),
        title_x=0.5,
        title_font=dict(size=18)
    )

    st.plotly_chart(fig4, use_container_width=False)


# FOOTER
st.markdown("---")
st.caption("📘 Sumber data: IDX Financial Statement Dataset (Kaggle) | Dibuat dengan Streamlit & Plotly")
