import matplotlib.pyplot as plt

def create_roe_chart(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(df["Bank"], df["ROEPct"] * 100)  # convert for display only
    ax.set_title("ROE Comparison")
    ax.set_ylabel("ROE (%)")

    return fig


def create_pe_chart(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(df["Bank"], df["PE"])
    ax.set_title("P/E Ratio Comparison")
    ax.set_ylabel("P/E Ratio")

    return fig