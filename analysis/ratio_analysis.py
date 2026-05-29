import pandas as pd

def calculate_ratios(df):

    df = df.copy()

    df["ROEPct"] = df["NetIncome"] / df["TotalEquity"]
    df["ROAPct"] = df["NetIncome"] / df["TotalAssets"]

    return df