import pandas as pd
from src.definitions import SEARCH_FIELDS
from src.control import controlled_input

def load_rows_from_csv(path: str) -> list[dict]:
    df = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False
    )

    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    rows = []

    for _, row in df.iterrows():
        row_data = {
            key: None if value == "" else str(value)
            for key, value in row.to_dict().items()
        }

        # skip fully empty rows
        if all(value is None for value in row_data.values()):
            continue

        rows.append(row_data)

    return rows


def ask_search_fields(columns: list[str]) -> list[str]:
    print("Available columns:")
    for i, col in enumerate(columns):
        print(f"{i}: {col}")

    raw = controlled_input("Enter column numbers to use as search fields, separated by commas: ")
    indexes = [int(x.strip()) for x in raw.split(",") if x.strip()]

    return [columns[i] for i in indexes]

def ask_extract_fields(available_fields: list[str]) -> list[str]:
    print("Extractable fields:")
    for i, field in enumerate(available_fields):
        print(f"{i}: {field}")

    raw = controlled_input("Enter fields to extract, separated by commas: ")
    indexes = [int(x.strip()) for x in raw.split(",") if x.strip()]

    return [available_fields[i] for i in indexes]


def write_records_to_csv(rows: list[dict], path: str) -> None:
    cleaned_rows = []

    for row in rows:
        cleaned_row = {}

        for key, value in row.items():
            if value is None:
                cleaned_row[key] = ""
            else:
                cleaned_row[key] = str(value)

        cleaned_rows.append(cleaned_row)

    pd.DataFrame(cleaned_rows).to_csv(path, index=False)
