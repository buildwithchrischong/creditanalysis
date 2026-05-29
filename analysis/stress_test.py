import pandas as pd


def stress_test(df):
    df["StressedROE"] = df["ROEPct"] * 0.7

    return df


if __name__ == "__main__":
    df = pd.read_csv("backend/data/bank_data.csv")

    df["ROEPct"] = df["ROE"] * 100

    stressed = stress_test(df)

    print(stressed[["Bank", "ROEPct", "StressedROE"]])