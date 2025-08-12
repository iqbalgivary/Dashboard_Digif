
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Digif", layout="wide")

Dashboard_digif = pd.read_pickle("data.pkl")
Dashboard_digif["Tanggal"]   = pd.to_datetime(Dashboard_digif["Tanggal"], errors="coerce")
Dashboard_digif["Transaksi"] = pd.to_numeric(Dashboard_digif["Transaksi"], errors="coerce").fillna(0)
Dashboard_digif = Dashboard_digif.dropna(subset=["Tanggal"]).sort_values("Tanggal")

# =======================
# FILTER (KANAN ATAS)
# =======================
min_tgl, max_tgl = Dashboard_digif["Tanggal"].min(), Dashboard_digif["Tanggal"].max()
cflt_left, cflt_right = st.columns([3,1])
with cflt_right:
    tgl_awal, tgl_akhir = st.date_input(
        "Filter Tanggal",
        value=(min_tgl.date(), max_tgl.date()),
        min_value=min_tgl.date(),
        max_value=max_tgl.date()
    )

mask = (Dashboard_digif["Tanggal"].dt.date >= tgl_awal) & (Dashboard_digif["Tanggal"].dt.date <= tgl_akhir)
D = Dashboard_digif.loc[mask].copy()

if D.empty:
    st.warning("Tidak ada data pada rentang tanggal yang dipilih.")
    st.stop()

# =======================
# BARIS 1: KPI
# =======================
total_transaksi = D["Transaksi"].sum()
count_transaksi_ex_infaq = D.loc[D["Program"] != "Infaq Bundling", "Transaksi"].count()
unique_donatur = D["ID_Donatur"].nunique()

k1, k2, k3 = st.columns(3)
k1.metric("Total Nominal", f"{total_transaksi:,.0f}")
k2.metric("Total Transaksi", f"{count_transaksi_ex_infaq:,}")
k3.metric("Total Donatur", f"{unique_donatur:,}")

# =======================
# BARIS 2: CHARTS
# =======================
sum_transaksi_per_tgl = D.groupby("Tanggal", dropna=False)["Transaksi"].sum().reset_index()
count_transaksi_per_tgl_ex_infaq = (
    D[D["Program"] != "Infaq Bundling"]
    .groupby("Tanggal", dropna=False)["Transaksi"].count().reset_index(name="Count_Transaksi")
)
unique_donatur_per_tgl = D.groupby("Tanggal", dropna=False)["ID_Donatur"].nunique().reset_index(name="Unique_Donatur")

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Total Nominal")
    st.line_chart(sum_transaksi_per_tgl.set_index("Tanggal"))
with c2:
    st.subheader("Total Transaksi")
    st.line_chart(count_transaksi_per_tgl_ex_infaq.set_index("Tanggal"))
with c3:
    st.subheader("Jumlah Donatur")
    st.line_chart(unique_donatur_per_tgl.set_index("Tanggal"))

# =======================
# PIE CHART: MEDIA ADS & PROGRAM (TOP 4 + OTHER) — EXCLUDE INFAQ BUNDLING
# =======================
col_pie1, col_pie2 = st.columns(2)

D_no_infaq = D[D["Program"] != "Infaq Bundling"].copy()

# PIE 1: Media Ads
with col_pie1:
    st.subheader("Distribusi Nominal per Media Ads (Top 4 + Other)")
    media_sum = (
        D_no_infaq.assign(**{"Media Ads": D_no_infaq["Media Ads"].astype(str).str.strip().fillna("Unknown")})
        .groupby("Media Ads", dropna=False)["Transaksi"]
        .sum()
        .sort_values(ascending=False)
    )
    top4 = media_sum.head(4)
    other_sum = media_sum.iloc[4:].sum()

    labels = list(top4.index.astype(str))
    values = list(top4.values)
    if other_sum > 0:
        labels.append("Other")
        values.append(other_sum)

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

# PIE 2: Program
with col_pie2:
    st.subheader("Distribusi Nominal per Program (Top 4 + Other)")
    program_sum = (
        D_no_infaq.assign(Program=D_no_infaq["Program"].astype(str).str.strip().fillna("Unknown"))
        .groupby("Program", dropna=False)["Transaksi"]
        .sum()
        .sort_values(ascending=False)
    )
    top4_prog = program_sum.head(4)
    other_sum_prog = program_sum.iloc[4:].sum()

    labels_prog = list(top4_prog.index.astype(str))
    values_prog = list(top4_prog.values)
    if other_sum_prog > 0:
        labels_prog.append("Other")
        values_prog.append(other_sum_prog)

    fig2, ax2 = plt.subplots()
    ax2.pie(values_prog, labels=labels_prog, autopct="%1.1f%%", startangle=90)
    ax2.axis("equal")
    st.pyplot(fig2)

st.caption("Filter tanggal di kanan atas mempengaruhi KPI, line chart, dan kedua pie chart (Infaq Bundling dikecualikan pada pie).")
