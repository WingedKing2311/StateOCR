import os

def display_table(df):
    print("\nExtracted Bank Transactions:\n")
    print(df.to_string(index=False))

def save_csv(df, filename="transactions.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False)
