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
# FORMAT HELPERS
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
# LOAD DATA (RAW LAYER)
# -------------------------------------------------
df_raw = fetch_bank_data()

# -------------------------------------------------
# CALCULATION LAYER
# -------------------------------------------------
df_calc = calculate_ratios(df_raw.copy())
df_stress = stress_test(df_calc.copy())
df_peer = compare_banks(df_calc.copy())

# merge stress back into calc for convenience
df_calc["StressedROE"] = df_stress["StressedROE"]

# -------------------------------------------------
# KPI CALCULATIONS (ALWAYS USE RAW NUMBERS)
# -------------------------------------------------
avg_pe = df_calc["PE"].mean()
avg_pb = df_calc["PriceToBook"].mean()
avg_div = df_calc["DividendYield"].mean()
avg_stress = df_calc["StressedROE"].mean()

highest_pe_bank = df_calc.loc[df_calc["PE"].idxmax(), "Bank"]
highest_pe_value = df_calc["PE"].max()

best_stress_bank = df_calc.loc[df_calc["StressedROE"].idxmax(), "Bank"]
best_stress_value = df_calc["StressedROE"].max()

highest_div_bank = df_calc.loc[df_calc["DividendYield"].idxmax(), "Bank"]
highest_div_value = df_calc["DividendYield"].max()

highest_pb_bank = df_calc.loc[df_calc["PriceToBook"].idxmax(), "Bank"]
highest_pb_value = df_calc["PriceToBook"].max()

# -------------------------------------------------
# DISPLAY LAYER (SAFE FORMATTING ONLY)
# -------------------------------------------------

df_display = df_calc.copy()
df_display["Market Cap (SGD)"] = df_display["MarketCap"].apply(format_market_cap)

df_display["PE"] = df_display["PE"].map("{:.2f}".format)
df_display["PriceToBook"] = df_display["PriceToBook"].map("{:.2f}".format)
df_display["DividendYield"] = df_display["DividendYield"].map("{:.2%}".format)

df_ratio_display = df_calc.copy()
df_ratio_display["ROE (%)"] = df_ratio_display["ROEPct"].map("{:.2%}".format)
df_ratio_display["ROA (%)"] = df_ratio_display["ROAPct"].map("{:.2%}".format)

stressed_display = df_calc.copy()
stressed_display["Stressed ROE (%)"] = stressed_display["StressedROE"].map("{:.2%}".format)

peer_display = df_peer.copy()
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
# CREDIT MEMORANDUM
# =================================================
with tab_memo:

    selected_bank = st.selectbox("Select Bank", df_calc["Bank"])

    bank = df_calc[df_calc["Bank"] == selected_bank].iloc[0]

    rating = (
        "strong" if bank["ROEPct"] > 0.10
        else "stable" if bank["ROEPct"] > 0.07
        else "weak"
    )

    color = "#006400" if rating == "strong" else "#FFD700"

    st.markdown(
        f"""
### Executive Summary

**Market cap:** SGD${bank['MarketCap'] / 1e9:.2f}B  
**ROE:** {bank['ROEPct']:.2%}  
**ROA:** {bank['ROAPct']:.2%}  
**P/E:** {bank['PE']:.2f}x  
**P/B:** {bank['PriceToBook']:.2f}x  
**Dividend yield:** {bank['DividendYield']:.2%}  
**Stressed ROE:** {bank['StressedROE']:.2%}

---

### Credit View

This analysis evaluates the company's profitability, valuation, and resilience under stress conditions.

The current credit rating is primarily driven by Return on Equity (ROE) and profitability metrics. However, this is a simplified proxy model and does not yet reflect a full institutional credit assessment.

Future enhancements will incorporate:
- Capital adequacy metrics
- Asset quality indicators (e.g. non-performing loans)
- Liquidity coverage ratios
- Earnings volatility over time
- Macroeconomic sensitivity
- Funding structure and deposit stability

As a result, the current rating should be interpreted as a **preliminary internal score rather than a formal agency rating**.


---

### Final Assessment

Overall, the credit profile is assessed as <span style="color:{color}; font-weight:700">{rating.upper()}</span>, supported by its earnings quality and valuation multiples.
""",


        unsafe_allow_html=True
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
            df_ratio_display[["Bank", "ROE (%)", "ROA (%)"]],
            use_container_width=True,
            hide_index=True
        )

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Stress Test")
        st.dataframe(
            stressed_display[["Bank", "Stressed ROE (%)"]],
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
        st.pyplot(create_roe_chart(df_calc))

    with chart_col2:
        st.markdown("### P/E Comparison")
        st.pyplot(create_pe_chart(df_calc))