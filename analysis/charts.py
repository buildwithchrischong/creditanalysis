import os
import matplotlib.pyplot as plt

def create_roe_chart(df):

    os.makedirs("exports", exist_ok=True)

    path = "exports/roe_chart.png"

    plt.figure(figsize=(10, 6))
    plt.bar(df["Bank"], df["ROEPct"])

    plt.title("ROE Comparison")
    plt.ylabel("ROE %")

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path