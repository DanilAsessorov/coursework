from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import pytest

from src.utils import (
    filter_transactions_by_date_range,
    filter_transactions_by_month,
    get_date_range,
    get_expenses_data,
    get_income_data,
)

# Тесты для get_stock_data


# Тесты для filter_transactions_by_month


def test_filter_transactions_by_month_empty_dataframe() -> None:
    """
    Тест для случая, когда DataFrame пустой.
    """
    empty_df = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": []})
    date = datetime(2024, 1, 15)
    result = filter_transactions_by_month(empty_df, date)
    assert result.empty, "Для пустого DataFrame должен возвращаться пустой DataFrame"


def test_filter_transactions_by_month_single_month(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест для фильтрации транзакций в пределах одного месяца.
    """
    date = datetime(2024, 1, 15)
    result = filter_transactions_by_month(sample_dataframe_by_month, date)
    assert len(result) == 2, "Должно быть возвращено 2 транзакции"
    assert (result["Дата операции"] <= date).all(), "Все даты должны быть до указанной даты"
    assert (result["Дата операции"] >= datetime(2024, 1, 1)).all(), "Все даты должны быть в январе"


def test_filter_transactions_by_month_same_date_as_transaction(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест, когда указанная дата совпадает с датой одной из транзакций.
    """
    date = datetime(2024, 1, 20)
    result = filter_transactions_by_month(sample_dataframe_by_month, date)
    assert len(result) == 3, "Должно быть возвращено 3 транзакции"
    assert date in result["Дата операции"].tolist(), "Должна быть транзакция за 20 января"


def test_filter_transactions_by_month_date_at_start_of_month(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест, когда указана дата в начале месяца.
    """
    date = datetime(2024, 1, 1)
    result = filter_transactions_by_month(sample_dataframe_by_month, date)
    assert len(result) == 0, "Должно быть возвращено 0 транзакций, так как ни одна дата меньше 1 января"


def test_filter_transactions_by_month_date_at_end_of_month(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест, когда указана дата в конце месяца.
    """
    date = datetime(2024, 1, 31)  # Предполагаем, что в sample_dataframe нет данных за январь
    result = filter_transactions_by_month(sample_dataframe_by_month, date)
    assert len(result) == 3, "Должно быть возвращено 3 транзакции (январь)"
    assert (result["Дата операции"] <= date).all(), "Все даты должны быть до указанной даты"
    assert (result["Дата операции"] >= datetime(2024, 1, 1)).any(), "Должна быть хотя бы одна дата в январе"


# Тесты для get_date_range


def test_get_date_range_week() -> None:
    """
    Тест для диапазона дат "неделя".
    """
    date = datetime(2024, 2, 20)  # Вторник
    start_date, end_date = get_date_range(date, data_range="W")
    assert start_date == datetime(2024, 2, 19), "Начало недели должно быть 19 февраля"
    assert end_date == datetime(2024, 2, 25), "Конец недели должен быть 25 февраля"


def test_get_date_range_month() -> None:
    """
    Тест для диапазона дат "месяц".
    """
    date = datetime(2024, 2, 20)
    start_date, end_date = get_date_range(date, data_range="M")
    assert start_date == datetime(2024, 2, 1), "Начало месяца должно быть 1 февраля"
    assert end_date == datetime(2024, 2, 20), "Конец месяца должен быть 20 февраля"


def test_get_date_range_year() -> None:
    """
    Тест для диапазона дат "год".
    """
    date = datetime(2024, 2, 20)
    start_date, end_date = get_date_range(date, data_range="Y")
    assert start_date == datetime(2024, 1, 1), "Начало года должно быть 1 января"
    assert end_date == datetime(2024, 2, 20), "Конец года должен быть 20 февраля"


def test_get_date_range_all() -> None:
    """
    Тест для диапазона дат "все данные".
    """
    date = datetime(2024, 2, 20)
    start_date, end_date = get_date_range(date, data_range="ALL")
    assert start_date == datetime.min, "Начало периода должно быть min datetime"
    assert end_date == datetime(2024, 2, 20), "Конец периода должен быть 20 февраля"


def test_get_date_range_default() -> None:
    """
    Тест для диапазона дат по умолчанию ("месяц").
    """
    date = datetime(2024, 2, 20)
    start_date, end_date = get_date_range(date)
    assert start_date == datetime(2024, 2, 1), "Начало месяца должно быть 1 февраля"
    assert end_date == datetime(2024, 2, 20), "Конец месяца должен быть 20 февраля"


def test_get_date_range_invalid_range() -> None:
    """
    Тест для неверного диапазона дат.
    """
    date = datetime(2024, 2, 20)
    with pytest.raises(ValueError, match="Неверный диапазон данных. Допустимые значения: W, M, Y, ALL"):
        get_date_range(date, data_range="INVALID")


def test_get_date_range_week_start_of_week() -> None:
    """
    Тест для диапазона дат "неделя", когда дата приходится на начало недели.
    """
    date = datetime(2024, 2, 19)  # Понедельник
    start_date, end_date = get_date_range(date, data_range="W")
    assert start_date == datetime(2024, 2, 19), "Начало недели должно быть 19 февраля"
    assert end_date == datetime(2024, 2, 25), "Конец недели должен быть 25 февраля"


def test_get_date_range_week_end_of_week() -> None:
    """
    Тест для диапазона дат "неделя", когда дата приходится на конец недели.
    """
    date = datetime(2024, 2, 25)  # Воскресенье
    start_date, end_date = get_date_range(date, data_range="W")
    assert start_date == datetime(2024, 2, 19), "Начало недели должно быть 19 февраля"
    assert end_date == datetime(2024, 2, 25), "Конец недели должен быть 25 февраля"


# Тесты для filter_transactions_by_date_range


def test_filter_transactions_by_date_range_empty_dataframe() -> None:
    """
    Тест для случая, когда DataFrame пустой.
    """
    empty_df = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": []})
    start_date = datetime(2024, 1, 10)
    end_date = datetime(2024, 1, 20)
    result = filter_transactions_by_date_range(empty_df, start_date, end_date)
    assert result.empty, "Для пустого DataFrame должен возвращаться пустой DataFrame"


def test_filter_transactions_by_date_range_within_range(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест для фильтрации по датам, находящимся внутри диапазона.
    """
    start_date = datetime(2024, 1, 10)
    end_date = datetime(2024, 1, 20)
    result = filter_transactions_by_date_range(sample_dataframe_by_month, start_date, end_date)
    assert len(result) == 2, "Должно быть возвращено 2 транзакции"
    assert (result["Дата операции"] >= start_date).all(), "Все даты должны быть больше или равны start_date"
    assert (result["Дата операции"] <= end_date).all(), "Все даты должны быть меньше или равны end_date"


def test_filter_transactions_by_date_range_end_date_at_end(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест, когда end_date совпадает с датой транзакции.
    """
    start_date = datetime(2024, 1, 12)
    end_date = datetime(2024, 1, 20)
    result = filter_transactions_by_date_range(sample_dataframe_by_month, start_date, end_date)
    assert len(result) == 2, "Должно быть возвращено 2 транзакции"
    assert (result["Дата операции"] >= start_date).all(), "Все даты должны быть больше или равны start_date"
    assert (result["Дата операции"] <= end_date).all(), "Все даты должны быть меньше или равны end_date"
    end_date_np = np.datetime64(end_date)  # Преобразуем datetime в datetime64
    assert end_date_np in result["Дата операции"].values, "Должна быть транзакция за 20 января"


def test_filter_transactions_by_date_range_range_covers_multiple_months(
    sample_dataframe_by_month: pd.DataFrame,
) -> None:
    """
    Тест, когда диапазон дат охватывает несколько месяцев.
    """
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 2, 28)
    result = filter_transactions_by_date_range(sample_dataframe_by_month, start_date, end_date)
    assert len(result) == 5, "Должно быть возвращено 5 транзакций"
    assert (result["Дата операции"] >= start_date).all(), "Все даты должны быть больше или равны start_date"
    assert (result["Дата операции"] <= end_date).all(), "Все даты должны быть меньше или равны end_date"
    assert (
        result["Дата операции"].dt.month <= 2
    ).all(), "Все месяцы должны быть январь или февраль"  # Дополнительная проверка


def test_filter_transactions_by_date_range_no_matches(sample_dataframe_by_month: pd.DataFrame) -> None:
    """
    Тест, когда нет транзакций в указанном диапазоне.
    """
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    result = filter_transactions_by_date_range(sample_dataframe_by_month, start_date, end_date)
    assert result.empty, "Должен вернуться пустой DataFrame, так как нет совпадений"


def test_filter_transactions_by_date_range_start_date_greater_than_end_date(
    sample_dataframe_by_month: pd.DataFrame,
) -> None:
    """
    Тест для случая, когда start_date больше end_date (должен вернуть пустой DataFrame).
    """
    start_date = datetime(2024, 1, 20)
    end_date = datetime(2024, 1, 10)
    result = filter_transactions_by_date_range(sample_dataframe_by_month, start_date, end_date)
    assert result.empty, "Должен вернуться пустой DataFrame"


# Тесты для get_expenses_data


def test_get_expenses_data_empty_dataframe() -> None:
    """
    Тест для случая, когда DataFrame пустой.
    """
    empty_df = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": []})
    result = get_expenses_data(empty_df)
    assert result["total_amount"] == 0, "Общая сумма должна быть 0 для пустого DataFrame"
    assert len(result["main"]) == 1, "Должен быть только элемент 'Остальное' в main"
    assert result["main"][0]["category"] == "Остальное", "Категория должна быть 'Остальное'"
    assert result["main"][0]["amount"] == 0, "Сумма в 'Остальное' должна быть 0"
    assert len(result["transfers_and_cash"]) == 2, "Должно быть два элемента в transfers_and_cash"
    assert result["transfers_and_cash"][0]["category"] == "Наличные"
    assert result["transfers_and_cash"][0]["amount"] == 0
    assert result["transfers_and_cash"][1]["category"] == "Переводы"
    assert result["transfers_and_cash"][1]["amount"] == 0


def test_get_expenses_data_basic(sample_expenses_dataframe: pd.DataFrame) -> None:
    """
    Тест для базового случая с расходами по разным категориям.
    """
    result = get_expenses_data(sample_expenses_dataframe)
    assert result["total_amount"] == -210, "Общая сумма расходов должна быть -210"

    # Проверяем main
    assert len(result["main"]) == 3, "Должно быть 2 категории + 'Остальное'"
    assert result["main"][0]["category"] == "A", "Первая категория должна быть A"
    assert result["main"][0]["amount"] == 90, "Сумма для A должна быть 90"
    assert result["main"][1]["category"] == "B", "Вторая категория должна быть B"
    assert result["main"][1]["amount"] == 60, "Сумма для B должна быть 60"
    assert result["main"][2]["category"] == "Остальное", "Последняя категория должна быть 'Остальное'"
    assert result["main"][2]["amount"] == 0, "Сумма для 'Остальное' должна быть 0"

    # Проверяем transfers_and_cash
    assert len(result["transfers_and_cash"]) == 2, "Должно быть два элемента в transfers_and_cash"
    assert result["transfers_and_cash"][0]["category"] == "Наличные", "Первая категория должна быть 'Наличные'"
    assert result["transfers_and_cash"][0]["amount"] == 60, "Сумма для 'Наличные' должна быть 60"
    assert result["transfers_and_cash"][1]["category"] == "Переводы", "Вторая категория должна быть 'Переводы'"
    assert result["transfers_and_cash"][1]["amount"] == 0, "Сумма для 'Переводы' должна быть 0"


def test_get_expenses_data_only_positive_amounts(sample_expenses_dataframe: pd.DataFrame) -> None:
    """
    Тест для случая, когда в DataFrame только положительные суммы (доходы).
    """
    positive_df = sample_expenses_dataframe.copy()
    positive_df["Сумма платежа"] = positive_df["Сумма платежа"].abs()  # делаем все суммы положительными
    result = get_expenses_data(positive_df)
    assert result["total_amount"] == 0, "Общая сумма должна быть 0, если нет расходов"
    assert len(result["main"]) == 1, "Должен быть только 'Остальное', если нет расходов"
    assert result["transfers_and_cash"][0]["amount"] == 0, "Суммы должны быть нулевыми"
    assert result["transfers_and_cash"][1]["amount"] == 0, "Суммы должны быть нулевыми"


def test_get_expenses_data_transfers_and_cash_categories(sample_expenses_dataframe: pd.DataFrame) -> None:
    """
    Тест для проверки правильности расчета сумм для категорий "Наличные" и "Переводы".
    """
    # Добавляем переводы
    transfers_data = {"Дата операции": [datetime(2024, 1, 2)], "Сумма платежа": [-25], "Категория": ["Переводы"]}
    transfers_df = pd.DataFrame(transfers_data)
    df = pd.concat([sample_expenses_dataframe, transfers_df], ignore_index=True)

    result = get_expenses_data(df)

    assert result["transfers_and_cash"][0]["category"] == "Наличные", "Первая категория должна быть 'Наличные'"
    assert result["transfers_and_cash"][0]["amount"] == 60, "Сумма для 'Наличные' должна быть 60"
    assert result["transfers_and_cash"][1]["category"] == "Переводы", "Вторая категория должна быть 'Переводы'"
    assert result["transfers_and_cash"][1]["amount"] == 25, "Сумма для 'Переводы' должна быть 25"


def test_get_expenses_data_top_categories_limit(sample_expenses_dataframe: pd.DataFrame) -> None:
    """
    Тест для проверки, что возвращаются только топ-7 категорий + "Остальное".
    """
    # Создаем DataFrame с более чем 7 категориями (чтобы проверить лимит)
    data: Dict[str, List[Any]] = {"Дата операции": [], "Сумма платежа": [], "Категория": []}
    for i in range(10):
        data["Дата операции"].append(datetime(2024, 1, i + 1))
        data["Сумма платежа"].append(-i * 10)
        data["Категория"].append(f"Категория {i}")

    many_categories_df = pd.DataFrame(data)
    result = get_expenses_data(many_categories_df)
    assert len(result["main"]) == 8, "Должно быть 7 топ-категорий + 'Остальное'"
    assert result["main"][-1]["category"] == "Остальное", "'Остальное' должно быть последней категорией"


def test_get_expenses_data_no_transfers_or_cash(sample_expenses_dataframe: pd.DataFrame) -> None:
    """
    Тест для случая, когда в DataFrame нет категорий "Наличные" и "Переводы".
    """
    no_transfers_df = sample_expenses_dataframe[sample_expenses_dataframe["Категория"] != "Наличные"].copy()
    result = get_expenses_data(no_transfers_df)
    assert result["transfers_and_cash"][0]["amount"] == 0, "Сумма для 'Наличные' должна быть 0"
    assert result["transfers_and_cash"][1]["amount"] == 0, "Сумма для 'Переводы' должна быть 0"


def test_get_expenses_data_same_category_name(sample_expenses_dataframe: pd.DataFrame) -> None:
    """
    Тест для случая, когда категория "Остальное" уже есть в данных
    """
    new_data = {"Дата операции": [datetime(2024, 1, 1)], "Сумма платежа": [-50], "Категория": ["Остальное"]}
    new_df = pd.DataFrame(new_data)
    combined_df = pd.concat([sample_expenses_dataframe, new_df], ignore_index=True)

    result = get_expenses_data(combined_df)
    assert "Остальное" in [cat["category"] for cat in result["main"]], "Должна быть категория 'Остальное'"


# Тесты для get_income_data


def test_get_income_data_empty_dataframe() -> None:
    """
    Тест для случая, когда DataFrame пустой.
    """
    empty_df = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": []})
    result = get_income_data(empty_df)
    assert result["total_amount"] == 0, "Общая сумма должна быть 0 для пустого DataFrame"
    assert len(result["main"]) == 0, "Список категорий должен быть пустым для пустого DataFrame"


def test_get_income_data_basic(sample_income_dataframe: pd.DataFrame) -> None:
    """
    Тест для базового случая с доходами по разным категориям.
    """
    result = get_income_data(sample_income_dataframe)
    assert result["total_amount"] == 2100, "Общая сумма доходов должна быть 2100"
    assert len(result["main"]) == 3, "Должно быть 3 категории доходов"

    # Проверяем порядок и суммы категорий (учитываем сортировку)
    assert result["main"][0]["category"] == "Зарплата", "Первая категория должна быть Зарплата"
    assert result["main"][0]["amount"] == 900, "Сумма для Зарплаты должна быть 900"
    assert result["main"][1]["category"] == "Инвестиции", "Вторая категория должна быть Инвестиции"
    assert result["main"][1]["amount"] == 600, "Сумма для Инвестиций должна быть 600"
    assert result["main"][2]["category"] == "Подработка", "Третья категория должна быть Подработка"
    assert result["main"][2]["amount"] == 600, "Сумма для Подработки должна быть 600"  # Раньше была ошибка


def test_get_income_data_only_negative_amounts(sample_income_dataframe: pd.DataFrame) -> None:
    """
    Тест для случая, когда в DataFrame только отрицательные суммы (расходы).
    """
    negative_df = sample_income_dataframe.copy()
    negative_df["Сумма платежа"] = -negative_df["Сумма платежа"]  # делаем все суммы отрицательными
    result = get_income_data(negative_df)
    assert result["total_amount"] == 0, "Общая сумма должна быть 0, если нет доходов"
    assert len(result["main"]) == 0, "Список категорий должен быть пустым, если нет доходов"


def test_get_income_data_single_category(sample_income_dataframe: pd.DataFrame) -> None:
    """
    Тест для случая, когда все доходы относятся к одной категории.
    """
    single_category_df = sample_income_dataframe.copy()
    single_category_df["Категория"] = "Единственный доход"
    result = get_income_data(single_category_df)
    assert result["total_amount"] == 2100, "Общая сумма должна быть 2100"
    assert len(result["main"]) == 1, "Должна быть только одна категория"
    assert result["main"][0]["category"] == "Единственный доход", "Категория должна быть 'Единственный доход'"
    assert result["main"][0]["amount"] == 2100, "Сумма для 'Единственный доход' должна быть 2100"


def test_get_income_data_zero_amounts(sample_income_dataframe: pd.DataFrame) -> None:
    """
    Тест для случая, когда в DataFrame есть нулевые суммы (они должны игнорироваться).
    """
    zero_amounts_data = {"Дата операции": [datetime(2024, 1, 1)], "Сумма платежа": [0], "Категория": ["Не учитывать"]}
    zero_amounts_df = pd.DataFrame(zero_amounts_data)
    df = pd.concat([sample_income_dataframe, zero_amounts_df], ignore_index=True)  # добавляем нулевые суммы
    result = get_income_data(df)
    assert result["total_amount"] == 2100, "Общая сумма должна быть 2100 (нули игнорируются)"
    # Проверяем, что категория "Не учитывать" отсутствует:
    category_names = [item["category"] for item in result["main"]]
    assert "Не учитывать" not in category_names


def test_get_income_data_empty_categories(sample_income_dataframe: pd.DataFrame) -> None:
    """
    Тест для случая, когда в DataFrame есть пустые категории
    """
    empty_category_data = {"Дата операции": [datetime(2024, 1, 1)], "Сумма платежа": [100], "Категория": [""]}
    empty_category_df = pd.DataFrame(empty_category_data)
    df = pd.concat([sample_income_dataframe, empty_category_df], ignore_index=True)
    result = get_income_data(df)
    assert "" in [item["category"] for item in result["main"]], "Пустая категория должна присутствовать"
