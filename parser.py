import re
import pandas as pd

def clean_amount(a):
    a = a.replace("_", "").strip()

    # Case: Indian OCR style "30,500,00"
    if a.count(",") == 2 and "." not in a:
        parts = a.split(",")
        a = parts[0] + parts[1] + "." + parts[2]

    # Case: "6450000" where decimal lost
    if a.count(",") == 1 and "." not in a:
        a = a.replace(",", "")[:-2] + "." + a.replace(",", "")[-2:]

    a = a.replace(",", "")

    try:
        return float(a)
    except:
        return None


def structure_data(text):
    rows = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    date_pattern = re.compile(r"\d{2}-\d{2}-\d{4}")
    amount_pattern = re.compile(r"[\d,]+\.?\d{2}")

    current = None
    buffer = []

    for line in lines:
        m = date_pattern.search(line)
        if m:
            if current:
                process_block(current, buffer, rows)
            current = {"Date": m.group()}
            buffer = []
        elif current:
            buffer.append(line)

    if current:
        process_block(current, buffer, rows)

    return pd.DataFrame(rows)

def process_block(current, buffer, rows):
    joined = " ".join(buffer)
    lower = joined.lower()

    if "closing balance" in lower:
        amounts = re.findall(r"[\d,]+\.?\d{2}", joined)
        balance = clean_amount(amounts[-1]) if amounts else None

        rows.append({
            "Date": current["Date"],
            "Description": "Closing Balance",
            "Debit": None,
            "Credit": None,
            "Balance": balance
        })
        return

    # Extract amounts
    amounts = re.findall(r"[\d,]+\.?\d{2}", joined)
    amounts = [clean_amount(a) for a in amounts]

    if not amounts:
        return

    balance = amounts[-1]
    others = amounts[:-1]

    debit = credit = None
    if len(others) == 1:
        debit = others[0]
    elif len(others) >= 2:
        debit, credit = others[0], others[1]

    if debit is not None and credit is not None and balance == credit:
        credit = None

    # Clean description
    description = re.sub(r"\d{2}-\d{2}-\d{4}", "", joined)
    description = re.sub(r"[\d,]+\.?\d{2}", "", description)
    description = re.sub(r"[^\w\s\-]", "", description).strip()

    rows.append({
        "Date": current["Date"],
        "Description": description,
        "Debit": debit,
        "Credit": credit,
        "Balance": balance
    })


'''def infer_debit_credit(df):
    df = df.copy()

    prev_balance = None

    for i in df.index:
        desc = str(df.at[i, "Description"]).lower()
        bal = df.at[i, "Balance"]

        # Skip rows that should NOT infer
        if (
            "opening balance" in desc or
            "closing balance" in desc or
            "interest" in desc
        ):
            df.at[i, "Debit"] = None
            df.at[i, "Credit"] = None
            prev_balance = bal
            continue


        # If OCR already gave something, respect it
        # If OCR gave BOTH debit or credit correctly, respect it
        if not pd.isna(df.at[i, "Debit"]) or not pd.isna(df.at[i, "Credit"]):
            prev_balance = bal
            continue

        if prev_balance is not None and abs(bal - prev_balance) > 1e6:
            prev_balance = bal
            continue

        if prev_balance is not None and not pd.isna(bal):
            delta = bal - prev_balance

            if delta < 0:
                df.at[i, "Debit"] = abs(delta)
                df.at[i, "Credit"] = None
            elif delta > 0:
                df.at[i, "Credit"] = delta
                df.at[i, "Debit"] = None

        prev_balance = bal

    return df'''

