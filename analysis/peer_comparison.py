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

    # Ensure missing columns don't crash the app
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    comparison = df[required_cols]

    return comparison