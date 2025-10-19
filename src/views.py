import time
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

# Функции для страницы "Главная"


def get_greeting(current_time: time) -> str:
    """
    Определяет приветствие в зависимости от времени суток.
    """
    if 6 <= current_time.hour < 12:
        return "Доброе утро"
    elif 12 <= current_time.hour < 18:
        return "Добрый день"
    elif 18 <= current_time.hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_card_data(df: pd.DataFrame) -> list:
    """
    Получает данные по каждой карте: последние 4 цифры, общая сумма расходов, кешбэк.
    """
    card_data = []
    for card in df["Номер карты"].unique():
        card_df = df[df["Номер карты"] == card]
        total_spent = card_df["Сумма платежа"].sum()
        cashback = total_spent / 100
        card_data.append(
            {"last_digits": str(card), "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)}
        )
    return card_data


def get_top_transactions(df: pd.DataFrame) -> list:
    """
    Получает топ-5 транзакций по сумме платежа.
    """
    # Сортируем по возрастанию, так как большие отрицательные числа - это большие расходы
    top_transactions = df.sort_values(by="Сумма платежа", ascending=True).head(
        5
    )  # True для фортировки отрицательных значений, False для положительных
    return [
        {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": round(row["Сумма платежа"], 2),
            "category": row["Категория"],
            "description": row["Описание"],
        }
        for index, row in top_transactions.iterrows()
    ]


def get_currency_rates(currencies: List[str]) -> Dict[str, Optional[float]]:
    """
    Получает курсы валют с использованием API.
    """

    currency_data = {}
    for currency in currencies:
        if currency != "RUB":
            try:
                response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js").json()
                currency_data[currency] = response["Valute"][currency]["Value"]  # Обрабат ответ API и извлекает курс
            except Exception as e:
                print(f"Ошибка при получении курса {currency}: {e}")
                currency_data[currency] = None  # Или другое значение по умолчанию
        else:
            continue

    return currency_data
