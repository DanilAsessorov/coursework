import json
import logging
import re
from typing import Any, Dict, List

import pandas as pd


def analyze_cashback_categories(df: pd.DataFrame, year: int, month: int) -> str:
    """
    Анализирует, какие категории были наиболее выгодными для выбора в качестве
    категорий повышенного кешбэка в указанном месяце года.
    """
    try:
        logging.info(f"Анализ выгодности категорий кешбэка за {year}-{month}")

        # Фильтруем данные по году и месяцу, и только отрицательные суммы (расходы)
        filtered_data = df[
            (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month) & (df["Сумма платежа"] < 0)
        ].copy()

        # Группируем по категориям и суммируем траты
        category_spending = filtered_data.groupby("Категория")["Сумма платежа"].sum().abs()

        # Рассчитываем потенциальный кешбэк (1%)
        category_cashback = category_spending * 0.01

        # Преобразуем в словарь и округляем значения
        cashback_analysis = category_cashback.round().to_dict()

        logging.info("Анализ выполнен успешно.")
        return json.dumps(cashback_analysis, indent=2, ensure_ascii=False)

    except Exception as e:
        logging.exception("Произошла ошибка")
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму, которую удалось бы отложить в «Инвесткопилку».
    """
    try:
        logging.info(f"Расчет суммы для Инвесткопилки за {month} с лимитом {limit}")

        total_savings: float = sum(
            (limit - (transaction["Сумма операции"] % limit)) % limit
            for transaction in transactions
            if transaction["Дата операции"].strftime("%Y-%m") == month
        )

        logging.info(f"Сумма для Инвесткопилки: {total_savings}")
        return round(total_savings, 2)
    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}")
        return 0.0


def simple_search(search_string: str, df: pd.DataFrame) -> str:
    """
    Ищет транзакции, содержащие запрос в описании или категории, и форматирует даты.
    """
    try:
        logging.info(f"Поиск транзакций по запросу: {search_string}")

        # 1. Форматируем столбец "Дата операции" в нужный формат
        df["Дата операции"] = df["Дата операции"].dt.strftime("%d.%m.%Y %H:%M:%S")
        df["Дата платежа"] = df["Дата платежа"].dt.strftime("%d.%m.%Y %H:%M:%S")

        # 2. Выполняем поиск
        search_results = df[
            df["Описание"].str.contains(search_string, case=False, na=False)
            | df["Категория"].str.contains(search_string, case=False, na=False)
        ]

        # 3. Преобразуем в JSON
        results = search_results.to_json(orient="records", force_ascii=False)

        logging.info(f"Найдено {len(search_results)} транзакций.")
        return results
    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}")
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)


def search_phone_numbers(df: pd.DataFrame) -> str:
    """
    Возвращает транзакции, содержащие в описании мобильные номера.
    """
    try:
        logging.info("Поиск транзакций с телефонными номерами.")

        # 1. Проверяем, не пустой ли DataFrame
        if df.empty:
            logging.info("Пустой DataFrame. Возвращаем пустой список.")
            return json.dumps([], indent=2, ensure_ascii=False)

        # 2. Выполняем поиск
        phone_number_pattern = re.compile(r"\+?\d{1,3}\s?\(?\d{3}\)?\s?\d{1,3}[-\s]?\d{2}[-\s]?\d{2}", re.IGNORECASE)
        phone_transactions = df[df["Описание"].str.contains(phone_number_pattern, regex=True, na=False)]

        # 3. Преобразуем в JSON
        results = phone_transactions.to_json(orient="records", force_ascii=False)
        logging.info(f"Найдено {len(phone_transactions)} транзакций с телефонными номерами.")
        return results
    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}")
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)


def search_person_transfers(df: pd.DataFrame) -> str:
    """
    Возвращает транзакции, которые относятся к переводам физлицам.
    """
    try:
        logging.info("Поиск переводов физическим лицам.")

        # 1. Проверяем, не пустой ли DataFrame
        if df.empty:
            logging.info("Пустой DataFrame. Возвращаем пустой список.")
            return json.dumps([], indent=2, ensure_ascii=False)

        # 2. Выполняем поиск
        person_transfer_pattern = re.compile(r"^Перевод\s[А-Я][а-я]+\s[А-Я]\.$")
        person_transfers = df[
            (df["Категория"] == "Переводы")
            & df["Описание"].str.contains(person_transfer_pattern, regex=True, na=False)
        ]

        # 3. Преобразуем в JSON
        results = person_transfers.to_json(orient="records", force_ascii=False)
        logging.info(f"Найдено {len(person_transfers)} переводов физическим лицам.")
        return results
    except Exception as e:
        logging.exception(f"Произошла ошибка: {e}")
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)
