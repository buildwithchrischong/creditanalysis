import streamlit as st
import pandas as pd
import sys
import os

# -------------------------------------------------
# PATH FIX
# -------------------------------------------------
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from analysis.bank_data import fetch_bank_data
from analysis.ratio_analysis import calculate_ratios
from analysis.stress_test import stress_test
from analysis.peer_comparison import compare_banks
from analysis.charts import create_roe_chart, create_pe_chart

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Credit Analysis Dashboard",
    layout="wide"
)

st.title("Personal - Credit Analysis Dashboard")
st.divider()

# -------------------------------------------------
# FORMAT FUNCTION
# -------------------------------------------------
def format_market_cap(value):
    if value is None:
        return "N/A"

    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    else:
        return f"${value / 1_000_000:.2f}M"

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
df = fetch_bank_data()
df["MarketCapFormatted"] = df["MarketCap"].apply(format_market_cap)

df = calculate_ratios(df)
stressed = stress_test(df)
peer = compare_banks(df)

# -------------------------------------------------
# KPI METRICS
# -------------------------------------------------
avg_pe = df["PE"].mean()
avg_pb = df["PriceToBook"].mean()
avg_div = df["DividendYield"].mean()
avg_stress = df["StressedROE"].mean()

highest_pe_bank = df.loc[df["PE"].idxmax(), "Bank"]
highest_pe_value = df["PE"].max()

best_stress_bank = df.loc[df["StressedROE"].idxmax(), "Bank"]
best_stress_value = df["StressedROE"].max()

highest_div_bank = df.loc[df["DividendYield"].idxmax(), "Bank"]
highest_div_value = df["DividendYield"].max()

highest_pb_bank = df.loc[df["PriceToBook"].idxmax(), "Bank"]
highest_pb_value = df["PriceToBook"].max()

# -------------------------------------------------
# FORMATTED TABLES
# -------------------------------------------------
df_display = df.copy()
df_display = df_display.rename(
    columns={"MarketCapFormatted": "Market Cap (SGD)"}
)

df_display["PE"] = df_display["PE"].map("{:.2f}".format)
df_display["PriceToBook"] = df_display["PriceToBook"].map("{:.2f}".format)
df_display["DividendYield"] = df_display["DividendYield"].map("{:.2%}".format)

df_ratio_display = df.copy()
df_ratio_display["ROEPct"] = df_ratio_display["ROEPct"].map("{:.2%}".format)
df_ratio_display["ROAPct"] = df_ratio_display["ROAPct"].map("{:.2%}".format)

stressed_display = stressed.copy()
stressed_display["StressedROE"] = stressed_display["StressedROE"].map("{:.2%}".format)

peer_display = peer.copy()
peer_display["ROEPct"] = peer_display["ROEPct"].map("{:.2%}".format)
peer_display["ROAPct"] = peer_display["ROAPct"].map("{:.2%}".format)
peer_display["PE"] = peer_display["PE"].map("{:.2f}".format)
peer_display["PriceToBook"] = peer_display["PriceToBook"].map("{:.2f}".format)
peer_display["DividendYield"] = peer_display["DividendYield"].map("{:.2%}".format)

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab_memo, tab_analysis = st.tabs(
    ["📝 Credit Memorandum", "📊 Analysis"]
)

# =================================================
# CREDIT MEMORANDUM TAB
# =================================================
with tab_memo:

    selected_bank = st.selectbox(
        "Select Bank",
        df["Bank"]
    )

    bank = df[df["Bank"] == selected_bank].iloc[0]

    # -------------------------------------------------
    # METRICS
    # -------------------------------------------------

    st.markdown(
        f"""
### Executive Summary

**Market cap of:** SGD${bank['MarketCap'] / 1e9:.2f}B  
**ROE:** {bank['ROEPct']:.2%}  
**ROA:** {bank['ROAPct']:.2%}  
**P/E:** {bank['PE']:.2f}x  
**P/B:** {bank['PriceToBook']:.2f}x  
**Dividend yield:** {bank['DividendYield']:.2%}  
**Stressed ROE:** {bank['StressedROE']:.2%}  

---

**Credit Rating:** {"Strong" if bank["ROEPct"] > 0.10 else "Stable" if bank["ROEPct"] > 0.07 else "Weak"}

---

### Credit View

This analysis evaluates the bank’s profitability, valuation, and resilience under stress conditions.

The bank demonstrates:
- Stable earnings power through ROE consistency
- Moderate leverage reflected in ROA
- Resilience under a 30% earnings stress scenario

Overall, the credit profile is assessed as **{"strong" if bank["ROEPct"] > 0.10 else "stable" if bank["ROEPct"] > 0.07 else "weak"}**, supported by its earnings quality and valuation multiples.
"""
    )

# =================================================
# ANALYSIS TAB
# =================================================
with tab_analysis:

    st.subheader("Dashboard Overview")

    # KPI ROW
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Highest PE",
            f"{highest_pe_value:.2f}",
            delta=f"{highest_pe_bank} | Avg {avg_pe:.2f}"
        )

    with col2:
        st.metric(
            "Best Stress ROE",
            f"{best_stress_value:.2%}",
            delta=f"{best_stress_bank} | Avg {avg_stress:.2%}"
        )

    with col3:
        st.metric(
            "Highest Dividend Yield",
            f"{highest_div_value:.2%}",
            delta=f"{highest_div_bank} | Avg {avg_div:.2%}"
        )

    with col4:
        st.metric(
            "Highest P/B Ratio",
            f"{highest_pb_value:.2f}",
            delta=f"{highest_pb_bank} | Avg {avg_pb:.2f}"
        )

    st.divider()

    # TABLES
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Bank Overview")
        st.dataframe(
            df_display[
                ["Bank", "Market Cap (SGD)", "PE", "PriceToBook", "DividendYield"]
            ],
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown("### Profitability Ratios")
        st.dataframe(
            df_ratio_display[["Bank", "ROEPct", "ROAPct"]],
            use_container_width=True,
            hide_index=True
        )

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Stress Test")
        st.dataframe(
            stressed_display[["Bank", "StressedROE"]],
            use_container_width=True,
            hide_index=True
        )

    with col4:
        st.markdown("### Peer Comparison")
        st.dataframe(
            peer_display,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # CHARTS
    st.markdown("### 📈 Performance Charts")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### ROE Comparison")
        st.pyplot(create_roe_chart(df))

    with chart_col2:
        st.markdown("### P/E Comparison")
        st.pyplot(create_pe_chart(df))