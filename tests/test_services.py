import json
from datetime import datetime

import pandas as pd

from src.services import (
    analyze_cashback_categories,
    investment_bank,
    search_person_transfers,
    search_phone_numbers,
    simple_search,
)


def test_analyze_cashback_categories_simple():
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2025-01-05", "2025-01-10", "2025-02-01"]),
            "Сумма платежа": [-100.0, -200.0, -50.0],
            "Категория": ["Еда", "Еда", "Транспорт"],
        }
    )

    res = analyze_cashback_categories(df, 2025, 1)
    data = json.loads(res)

    # Для категории "Еда" суммарные расходы 300 -> кешбэк 1% = 3.0
    assert "Еда" in data
    assert data["Еда"] == 3.0
    # Категория "Транспорт" в январе отсутствует
    assert "Транспорт" not in data


def test_investment_bank_simple():
    transactions = [
        {"Дата операции": datetime(2025, 1, 5), "Сумма операции": 45},
        {"Дата операции": datetime(2025, 1, 6), "Сумма операции": 120},
        {"Дата операции": datetime(2025, 2, 1), "Сумма операции": 30},
    ]

    # limit = 50: для 45 -> 5, для 120 -> 30, сумма = 35
    res = investment_bank("2025-01", transactions, 50)
    assert res == 35.0


def test_simple_search_found_and_date_format():
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2025-01-05 10:00", "2025-01-06 11:00"]),
            "Дата платежа": pd.to_datetime(["2025-01-05", "2025-01-06"]),
            "Описание": ["Оплата в магазине", "Перевод другу"],
            "Категория": ["Покупки", "Переводы"],
        }
    )

    res = simple_search("перевод", df)
    data = json.loads(res)

    assert len(data) == 1
    assert data[0]["Описание"] == "Перевод другу"
    # Даты должны быть отформатированы в строку вида dd.mm.YYYY
    assert isinstance(data[0]["Дата операции"], str)
    assert "." in data[0]["Дата операции"]


def test_search_phone_numbers_empty_and_find():
    df_empty = pd.DataFrame(columns=["Дата операции", "Дата платежа", "Описание", "Категория"])
    res_empty = search_phone_numbers(df_empty)
    assert json.loads(res_empty) == []

    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "Дата платежа": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "Описание": ["Позвоните +7 (910) 123-45-67", "Без номера"],
            "Категория": ["Связь", "Прочее"],
        }
    )

    res = search_phone_numbers(df)
    data = json.loads(res)
    assert len(data) == 1
    assert "+7" in data[0]["Описание"]


def test_search_person_transfers_empty_and_find():
    df_empty = pd.DataFrame(columns=["Дата операции", "Дата платежа", "Описание", "Категория"])
    res_empty = search_person_transfers(df_empty)
    assert json.loads(res_empty) == []

    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "Дата платежа": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "Описание": ["Перевод Иванов И.", "Перевод ООО Рога и С."],
            "Категория": ["Переводы", "Переводы"],
        }
    )

    res = search_person_transfers(df)
    data = json.loads(res)
    assert len(data) == 1
    assert "Иванов" in data[0]["Описание"]
