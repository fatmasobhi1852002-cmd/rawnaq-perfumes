import pandas as pd

from settings import SOURCE_EXCEL, CLEAN_EXCEL


DEFAULT_VALUES = {
    "النوع": "يناسب الجميع",
    "الموسم": "يصلح لكل المواسم",
    "التصنيف العطري": "تصنيف متنوع",
    "درجة الحلاوة": "على حسب اختيار العميل",
    "النوتات الرئيسية": "النوتات حسب اختيار العميل",
}


def is_incomplete(value):
    if pd.isna(value):
        return True

    text = str(value).strip()

    return (
        not text
        or text == "غير محدد"
        or "يحتاج" in text
    )


def clean_column(dataframe, column):
    default = DEFAULT_VALUES[column]

    dataframe[column] = dataframe[column].apply(
        lambda value:
            default
            if is_incomplete(value)
            else value
    )

    return dataframe


def build_embedding_text(row):
    parts = [
        str(row["اسم_المنتج"]),
        str(row["النوع"]),
        str(row["الموسم"]),
        str(row["التصنيف العطري"]),
        str(row["النوتات الرئيسية"]),
        str(row["درجة الحلاوة"]),
    ]

    return " ".join(parts)


def main():
    if not SOURCE_EXCEL.exists():
        raise FileNotFoundError(
            f"ملف الكتالوج غير موجود:\n{SOURCE_EXCEL}\n"
            "ضع ملف Excel داخل backend/data بنفس الاسم."
        )

    catalog = pd.read_excel(
        SOURCE_EXCEL,
        sheet_name="كتالوج البيع",
    )

    perfumes = pd.read_excel(
        SOURCE_EXCEL,
        sheet_name="البرفانات والمسكات",
    )

    catalog = catalog.rename(
        columns={"المنتج": "اسم_المنتج"}
    )

    perfumes = perfumes.rename(
        columns={"الاسم": "اسم_المنتج"}
    )

    required_catalog = {
        "اسم_المنتج",
        "النوع",
        "الموسم",
        "التصنيف العطري",
        "النوتات الرئيسية",
    }

    required_perfumes = {
        "اسم_المنتج",
        "درجة الحلاوة",
        "ملاحظات",
    }

    missing_catalog = (
        required_catalog - set(catalog.columns)
    )

    missing_perfumes = (
        required_perfumes - set(perfumes.columns)
    )

    if missing_catalog:
        raise ValueError(
            "أعمدة ناقصة في شيت كتالوج البيع: "
            + ", ".join(sorted(missing_catalog))
        )

    if missing_perfumes:
        raise ValueError(
            "أعمدة ناقصة في شيت البرفانات والمسكات: "
            + ", ".join(sorted(missing_perfumes))
        )

    perfumes_extra = perfumes[
        [
            "اسم_المنتج",
            "درجة الحلاوة",
            "ملاحظات",
        ]
    ]

    df = catalog.merge(
        perfumes_extra,
        on="اسم_المنتج",
        how="left",
    )

    print(
        f"عدد المنتجات بعد الدمج: {len(df)}"
    )

    for column in DEFAULT_VALUES:
        df = clean_column(df, column)

    df["نص_البحث"] = df.apply(
        build_embedding_text,
        axis=1,
    )

    df.to_excel(
        CLEAN_EXCEL,
        index=False,
    )

    print(
        f"تم حفظ الملف النظيف: {CLEAN_EXCEL}"
    )


if __name__ == "__main__":
    main()
