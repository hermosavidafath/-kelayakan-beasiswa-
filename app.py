import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ─────────────────────────────────────────
#  Konfigurasi halaman
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Kelayakan Beasiswa – ",
    page_icon="🎓",
    layout="centered",
)

# ─────────────────────────────────────────
#  Fungsi keanggotaan (trapesium / segitiga)
# ─────────────────────────────────────────

def tidak_layak(ipk: float) -> float:
    """
    Tidak Layak  : turun dari 1 → 0 antara IPK 1.5 – 2.5
    Domain       : 0.00 – 4.00
    """
    if ipk <= 1.5:
        return 1.0
    elif ipk <= 2.5:
        return (2.5 - ipk) / (2.5 - 1.5)
    else:
        return 0.0


def dipertimbangkan(ipk: float) -> float:
    """
    Dipertimbangkan : segitiga puncak di IPK 2.5
    Naik  1.5 – 2.5, turun 2.5 – 3.5
    """
    if ipk <= 1.5 or ipk >= 3.5:
        return 0.0
    elif ipk <= 2.5:
        return (ipk - 1.5) / (2.5 - 1.5)
    else:  # 2.5 < ipk < 3.5
        return (3.5 - ipk) / (3.5 - 2.5)


def layak(ipk: float) -> float:
    """
    Layak  : naik dari 0 → 1 antara IPK 2.5 – 3.5
    Domain : 0.00 – 4.00
    """
    if ipk <= 2.5:
        return 0.0
    elif ipk <= 3.5:
        return (ipk - 2.5) / (3.5 - 2.5)
    else:
        return 1.0


# ─────────────────────────────────────────
#  Defuzzifikasi – Centroid / Weighted Average
# ─────────────────────────────────────────

def defuzzifikasi(mu_tl: float, mu_dp: float, mu_ly: float) -> float:
    """
    Weighted average sederhana dengan titik representatif setiap himpunan:
      Tidak Layak       → 1.0
      Dipertimbangkan   → 2.5
      Layak             → 4.0
    """
    titik = np.array([1.0, 2.5, 4.0])
    bobot = np.array([mu_tl, mu_dp, mu_ly])
    if bobot.sum() == 0:
        return 0.0
    return float(np.dot(titik, bobot) / bobot.sum())


# ─────────────────────────────────────────
#  Grafik fungsi keanggotaan
# ─────────────────────────────────────────

def plot_keanggotaan(ipk_input: float,
                     mu_tl: float, mu_dp: float, mu_ly: float):
    x = np.linspace(0, 4, 400)

    y_tl = np.array([tidak_layak(v) for v in x])
    y_dp = np.array([dipertimbangkan(v) for v in x])
    y_ly = np.array([layak(v) for v in x])

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(x, y_tl, color="#e74c3c", linewidth=2, label="Tidak Layak")
    ax.plot(x, y_dp, color="#f39c12", linewidth=2, label="Dipertimbangkan")
    ax.plot(x, y_ly, color="#27ae60", linewidth=2, label="Layak")

    # Garis vertikal nilai IPK input
    ax.axvline(ipk_input, color="navy", linestyle="--", linewidth=1.5,
               label=f"IPK = {ipk_input:.2f}")

    # Titik derajat keanggotaan
    ax.scatter([ipk_input] * 3,
               [mu_tl, mu_dp, mu_ly],
               color=["#e74c3c", "#f39c12", "#27ae60"],
               zorder=5, s=60)

    ax.set_xlim(0, 4)
    ax.set_ylim(-0.05, 1.1)
    ax.set_xlabel("IPK", fontsize=12)
    ax.set_ylabel("Derajat Keanggotaan μ(x)", fontsize=12)
    ax.set_title("Fungsi Keanggotaan – Kelayakan Beasiswa", fontsize=13, fontweight="bold")
    ax.legend(loc="upper center", ncol=4, fontsize=9)
    ax.grid(alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)


# ─────────────────────────────────────────
#  Grafik bar derajat keanggotaan
# ─────────────────────────────────────────

def plot_bar(mu_tl: float, mu_dp: float, mu_ly: float):
    labels = ["Tidak Layak", "Dipertimbangkan", "Layak"]
    values = [mu_tl, mu_dp, mu_ly]
    colors = ["#e74c3c", "#f39c12", "#27ae60"]

    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f"{val:.3f}",
                ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylim(0, 1.2)
    ax.set_ylabel("Derajat Keanggotaan")
    ax.set_title("Derajat Keanggotaan per Kategori", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)


# ─────────────────────────────────────────
#  Tentukan label hasil
# ─────────────────────────────────────────

def label_hasil(nilai_defuzz: float) -> tuple[str, str]:
    if nilai_defuzz < 1.75:
        return "Tidak Layak", "#e74c3c"
    elif nilai_defuzz < 3.0:
        return "Dipertimbangkan", "#f39c12"
    else:
        return "Layak", "#27ae60"


# ═══════════════════════════════════════════
#  TAMPILAN UTAMA STREAMLIT
# ═══════════════════════════════════════════

# Header
st.markdown("""
<div style="background: linear-gradient(135deg,#1a1a2e,#16213e);
            padding:20px 30px; border-radius:12px; text-align:center; margin-bottom:20px">
  <h1 style="color:#f0c040; margin:0; font-size:1.8rem">🎓 Sistem Kelayakan Beasiswa</h1>
  
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────
st.sidebar.header("⚙️ Parameter Input")
st.sidebar.markdown("Masukkan nilai **IPK** mahasiswa (0.00 – 4.00)")

ipk = st.sidebar.slider(
    "IPK Mahasiswa",
    min_value=0.00, max_value=4.00,
    value=2.75, step=0.01,
    format="%.2f"
)

ipk_manual = st.sidebar.number_input(
    "Atau ketik langsung:",
    min_value=0.00, max_value=4.00,
    value=ipk, step=0.01, format="%.2f"
)

# Sinkronisasi: input manual menang
ipk = float(ipk_manual)
ipk = max(0.0, min(4.0, ipk))

st.sidebar.markdown("---")
st.sidebar.info(
    "**Domain:** 0.00 – 4.00\n\n"
    "**Himpunan Fuzzy:**\n"
    "- 🔴 Tidak Layak\n"
    "- 🟡 Dipertimbangkan\n"
    "- 🟢 Layak"
)

# ── Hitung fuzzifikasi ─────────────────────
mu_tl = tidak_layak(ipk)
mu_dp = dipertimbangkan(ipk)
mu_ly = layak(ipk)
nilai_crisp = defuzzifikasi(mu_tl, mu_dp, mu_ly)
label, warna = label_hasil(nilai_crisp)

# ── Tampilkan hasil utama ──────────────────
st.subheader("📊 Hasil Inferensi Fuzzy")

col1, col2, col3, col4 = st.columns(4)
col1.metric("IPK Input", f"{ipk:.2f}")
col2.metric("Tidak Layak", f"{mu_tl:.3f}")
col3.metric("Dipertimbangkan", f"{mu_dp:.3f}")
col4.metric("Layak", f"{mu_ly:.3f}")

st.markdown(f"""
<div style="background-color:{warna}22; border-left:6px solid {warna};
            padding:16px 20px; border-radius:8px; margin:16px 0">
  <h2 style="color:{warna}; margin:0">
      Keputusan: {label}
  </h2>
  <p style="margin:6px 0 0 0; color:#555">
      Nilai Defuzzifikasi (Weighted Average): <strong>{nilai_crisp:.4f}</strong>
  </p>
</div>
""", unsafe_allow_html=True)

# ── Grafik fungsi keanggotaan ──────────────
st.subheader("📈 Grafik Fungsi Keanggotaan")
plot_keanggotaan(ipk, mu_tl, mu_dp, mu_ly)

# ── Grafik bar ─────────────────────────────
st.subheader("📉 Derajat Keanggotaan per Kategori")
plot_bar(mu_tl, mu_dp, mu_ly)

# ── Tabel detail perhitungan ───────────────
st.subheader("🧮 Detail Perhitungan")

with st.expander("Lihat langkah-langkah perhitungan", expanded=True):

    st.markdown("### 1️⃣  Fuzzifikasi")
    st.markdown(f"""
| Himpunan Fuzzy | Fungsi Keanggotaan | Nilai μ |
|---|---|---|
| Tidak Layak | Bahu kiri (1.5 - 2.5) | **{mu_tl:.4f}** |
| Dipertimbangkan | Segitiga (1.5 - 2.5 - 3.5) | **{mu_dp:.4f}** |
| Layak | Bahu kanan (2.5 - 3.5) | **{mu_ly:.4f}** |
""")

    st.markdown("### 2️⃣  Derajat Keanggotaan")
    st.markdown(f"""
- μ (Tidak Layak)       = **{mu_tl:.4f}**
- μ (Dipertimbangkan)   = **{mu_dp:.4f}**
- μ (Layak)             = **{mu_ly:.4f}**
""")

    st.markdown("### 3️⃣  Defuzzifikasi (Weighted Average)")
    st.latex(r"""
    z^* = \frac{\mu_{TL} \cdot c_{TL} + \mu_{DP} \cdot c_{DP} + \mu_{LY} \cdot c_{LY}}
               {\mu_{TL} + \mu_{DP} + \mu_{LY}}
    """)

    denom = mu_tl + mu_dp + mu_ly
    if denom > 0:
        st.latex(
            rf"z^* = \frac{{({mu_tl:.4f} \times 1.0) + ({mu_dp:.4f} \times 2.5) + ({mu_ly:.4f} \times 4.0)}}{{{denom:.4f}}} = {nilai_crisp:.4f}"
        )

    st.markdown("### 4️⃣  Keputusan Akhir")
    st.success(f"**{label}** (nilai crisp = {nilai_crisp:.4f})")


