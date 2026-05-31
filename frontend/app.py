```python
import streamlit as st
import pandas as pd

from analysis.bank_data import fetch_bank_data
from analysis.ratio_analysis import calculate_ratios
from analysis.stress_test import stress_test
from analysis.peer_comparison import compare_banks
from analysis.charts import create_roe_chart

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Credit Analysis Dashboard",
    layout="wide"
)

st.title("Personal - Credit Analysis Dashboard")

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

    return f"${value / 1_000_000:.2f}M"


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
df = fetch_bank_data()

df["MarketCapFormatted"] = df["MarketCap"].apply(
    format_market_cap
)

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

best_stress_bank = df.loc[
    df["StressedROE"].idxmax(),
    "Bank"
]
best_stress_value = df["StressedROE"].max()

highest_div_bank = df.loc[
    df["DividendYield"].idxmax(),
    "Bank"
]
highest_div_value = df["DividendYield"].max()

highest_pb_bank = df.loc[
    df["PriceToBook"].idxmax(),
    "Bank"
]
highest_pb_value = df["PriceToBook"].max()

# -------------------------------------------------
# DISPLAY TABLES
# -------------------------------------------------
df_display = df.copy()

df_display = df_display.rename(
    columns={
        "MarketCapFormatted": "Market Cap (SGD)"
    }
)

df_display["PE"] = df_display["PE"].map("{:.2f}".format)
df_display["PriceToBook"] = (
    df_display["PriceToBook"]
    .map("{:.2f}".format)
)

df_display["DividendYield"] = (
    df_display["DividendYield"]
    .map("{:.2%}".format)
)

# Profitability
df_ratio_display = df.copy()

df_ratio_display["ROEPct"] = (
    df_ratio_display["ROEPct"]
    .map("{:.2%}".format)
)

df_ratio_display["ROAPct"] = (
    df_ratio_display["ROAPct"]
    .map("{:.2%}".format)
)

# Stress Test
stressed_display = stressed.copy()

stressed_display["StressedROE"] = (
    stressed_display["StressedROE"]
    .map("{:.2%}".format)
)

# Peer Comparison
peer_display = peer.copy()

peer_display["ROEPct"] = (
    peer_display["ROEPct"]
    .map("{:.2%}".format)
)

peer_display["ROAPct"] = (
    peer_display["ROAPct"]
    .map("{:.2%}".format)
)

peer_display["PE"] = (
    peer_display["PE"]
    .map("{:.2f}".format)
)

peer_display["PriceToBook"] = (
    peer_display["PriceToBook"]
    .map("{:.2f}".format)
)

peer_display["DividendYield"] = (
    peer_display["DividendYield"]
    .map("{:.2%}".format)
)

# -------------------------------------------------
# TABS
# -------------------------------------------------
analysis_tab, memo_tab = st.tabs(
    ["📊 Analysis", "📝 Credit Memorandum"]
)

# =================================================
# ANALYSIS TAB
# =================================================
with analysis_tab:

    st.subheader("Dashboard")

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

    # ROW 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Bank Overview")

        st.dataframe(
            df_display[
                [
                    "Bank",
                    "Market Cap (SGD)",
                    "PE",
                    "PriceToBook",
                    "DividendYield"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.markdown("### Profitability Ratios")

        st.dataframe(
            df_ratio_display[
                [
                    "Bank",
                    "ROEPct",
                    "ROAPct"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    # ROW 2
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Stress Test")

        st.dataframe(
            stressed_display[
                [
                    "Bank",
                    "StressedROE"
                ]
            ],
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

    st.markdown("### 📈 ROE Chart")

    st.image(
        create_roe_chart(df),
        use_container_width=True
    )

# =================================================
# CREDIT MEMORANDUM TAB
# =================================================
with memo_tab:

    st.header("Credit Memorandum")

    selected_bank = st.selectbox(
        "Select Bank",
        df["Bank"]
    )

    bank = (
        df[df["Bank"] == selected_bank]
        .iloc[0]
    )

    st.subheader("Executive Summary")

    st.write(
        f"""
        {bank['Bank']} has a market capitalization of
        {bank['MarketCapFormatted']}.

        The bank generates a Return on Equity (ROE)
        of {bank['ROEPct']:.2%} and a Return on Assets
        (ROA) of {bank['ROAPct']:.2%}.

        The stock currently trades at
        {bank['PE']:.2f}x earnings and
        {bank['PriceToBook']:.2f}x book value.

        Investors receive a dividend yield
        of {bank['DividendYield']:.2%}.
        """
    )

    st.divider()

    st.subheader("Financial Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "ROE",
        f"{bank['ROEPct']:.2%}"
    )

    col2.metric(
        "ROA",
        f"{bank['ROAPct']:.2%}"
    )

    col3.metric(
        "P/E",
        f"{bank['PE']:.2f}"
    )

    col4.metric(
        "Dividend Yield",
        f"{bank['DividendYield']:.2%}"
    )

    st.divider()

    st.subheader("Stress Test Analysis")

    st.write(
        f"""
        Under a severe earnings stress scenario
        where profitability declines by 30%,
        the bank's stressed ROE falls to
        {bank['StressedROE']:.2%}.

        This suggests that the institution
        remains profitable under adverse
        operating conditions.
        """
    )

    st.divider()

    st.subheader("Credit View")

    if bank["ROEPct"] > 0.10:
        recommendation = "Positive"
    elif bank["ROEPct"] > 0.07:
        recommendation = "Stable"
    else:
        recommendation = "Weak"

    st.metric(
        "Credit Assessment",
        recommendation
    )