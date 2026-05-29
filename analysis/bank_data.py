import pandas as pd

EXCEL_PATH = "data/bank_data.xlsx"

def fetch_bank_data():

    df = pd.read_excel(EXCEL_PATH, sheet_name="banks")

    return df