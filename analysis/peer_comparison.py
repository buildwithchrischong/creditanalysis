import pandas as pd

def compare_banks(df):
    df = df.copy()

    required_cols = [
        "Bank",
        "ROEPct",
        "ROAPct",
        "PE",
        "DividendYield",
        "PriceToBook"
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df[required_cols].copy()