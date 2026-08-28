import pandas as pd

from settings import SOURCE_EXCEL


def main():
    if not SOURCE_EXCEL.exists():
        raise FileNotFoundError(
            f"ملف Excel غير موجود: {SOURCE_EXCEL}"
        )

    excel_file = pd.ExcelFile(SOURCE_EXCEL)

    print("sheets:", excel_file.sheet_names)
    print("-" * 50)

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(
            SOURCE_EXCEL,
            sheet_name=sheet_name,
        )

        print(f"\nsheet: {sheet_name}")
        print(f"number of rows: {len(df)}")
        print(f"columns: {list(df.columns)}")
        print(df.head(3))
        print("-" * 50)


if __name__ == "__main__":
    main()
