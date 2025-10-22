from datetime import time
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests
from pandas import DataFrame

from src.views import get_card_data, get_currency_rates, get_greeting, get_top_transactions

# Тесты для get_greeting


@pytest.mark.parametrize(
    "time_fixture, expected_greeting",
    [
        ("morning_time", "Доброе утро"),
        ("afternoon_time", "Добрый день"),
        ("evening_time", "Добрый вечер"),
        ("night_time", "Доброй ночи"),
    ],
)
def test_get_greeting_with_fixtures(time_fixture: str, expected_greeting: str, request: Any) -> None:
    """
    Тест функции get_greeting с использованием фикстур для времени.
    """
    current_time = request.getfixturevalue(time_fixture)  # Получаем значение фикстуры
    greeting = get_greeting(current_time)
    assert (
        greeting == expected_greeting
    ), f"Для времени {current_time} ожидалось приветствие '{expected_greeting}', но было получено '{greeting}'"


@pytest.mark.parametrize(
    "hour, expected_greeting",
    [
        (6, "Доброе утро"),
        (11, "Доброе утро"),
        (12, "Добрый день"),
        (17, "Добрый день"),
        (18, "Добрый вечер"),
        (22, "Добрый вечер"),
        (23, "Доброй ночи"),
        (5, "Доброй ночи"),
        (0, "Доброй ночи"),
    ],
)
def test_get_greeting_with_hours(hour: int, expected_greeting: str) -> None:
    """
    Тест функции get_greeting с параметризацией по часу.
    """
    current_time = time(hour=hour, minute=0, second=0)
    greeting = get_greeting(current_time)
    assert (
        greeting == expected_greeting
    ), f"Для часа {hour} ожидалось приветствие '{expected_greeting}', но было получено '{greeting}'"


@patch("src.views.time")  # Замените src.utils на фактический путь к модулю
def test_get_greeting_mock_time(mock_time: MagicMock) -> None:
    """
    Тест функции get_greeting с использованием Mock для времени.
    """
    mock_time.return_value.hour = 10  # Устанавливаем час для мокированного времени
    greeting = get_greeting(mock_time.return_value)
    assert greeting == "Доброе утро"


# Тесты для get_card_data

def test_get_card_data_empty_dataframe() -> None:
    """
    Тест для случая, когда DataFrame пустой.
    """
    empty_df = pd.DataFrame({"Номер карты": [], "Сумма платежа": []})
    result = get_card_data(empty_df)
    assert result == [], "Для пустого DataFrame должен возвращаться пустой список"


def test_get_card_data_single_card(sample_dataframe: DataFrame) -> None:
    """
    Тест для случая, когда DataFrame содержит данные только по одной карте.
    """
    single_card_df = sample_dataframe[sample_dataframe["Номер карты"] == "*1234"]
    result = get_card_data(single_card_df)
    assert len(result) == 1, "Должна быть информация только по одной карте"
    assert result[0]["last_digits"] == "*1234", "Неверный номер карты"
    assert result[0]["total_spent"] == -125.0, "Неверная общая сумма расходов"
    assert result[0]["cashback"] == -1.25, "Неверный кешбэк"


def test_get_card_data_multiple_cards(sample_dataframe: DataFrame) -> None:
    """
    Тест для случая, когда DataFrame содержит данные по нескольким картам.
    """
    result = get_card_data(sample_dataframe)
    assert len(result) == 3, "Должна быть информация по трем картам"
    card_numbers = [card["last_digits"] for card in result]
    assert "*1234" in card_numbers, "Номер карты *1234 отсутствует"
    assert "*5678" in card_numbers, "Номер карты *5678 отсутствует"
    assert "*9012" in card_numbers, "Номер карты *9012 отсутствует"

    # Проверка сумм для карты *1234
    card_1234_data = next(card for card in result if card["last_digits"] == "*1234")
    assert card_1234_data["total_spent"] == -125.0, "Неверная общая сумма расходов для карты *1234"
    assert card_1234_data["cashback"] == -1.25, "Неверный кешбэк для карты *1234"


@pytest.mark.parametrize(
    "card_number, expected_total_spent, expected_cashback",
    [
        ("*1234", -125.0, -1.25),
        ("*5678", -60.0, -0.6),
        ("*9012", -75.0, -0.75),
    ],
)
def test_get_card_data_parameterized(
    sample_dataframe: DataFrame,
    card_number: str,
    expected_total_spent: float,
    expected_cashback: float,
) -> None:
    """
    Параметризованный тест для проверки данных по каждой карте.
    """
    result = get_card_data(sample_dataframe)
    card_data = next((card for card in result if card["last_digits"] == card_number), None)
    assert card_data is not None, f"Данные для карты {card_number} не найдены"
    assert card_data["total_spent"] == expected_total_spent, f"Неверная общая сумма расходов для карты {card_number}"
    assert card_data["cashback"] == expected_cashback, f"Неверный кешбэк для карты {card_number}"


@patch("pandas.core.series.Series.unique")
def test_get_card_data_mock_unique(mock_unique: MagicMock, sample_dataframe: DataFrame) -> None:
    """
    Тест с использованием Mock для метода unique.
    """
    # Мокируем возвращаемое значение метода unique для столбца 'Номер карты'
    mock_unique.return_value = ["*1234"]

    # Запускаем тестируемую функцию
    result = get_card_data(sample_dataframe)

    # Проверяем, что метод unique был вызван
    mock_unique.assert_called_once()  # или assert mock_unique.call_count == 1

    # Проверяем результат работы функции
    assert len(result) == 1, "Должна быть информация только по одной карте"
    assert result[0]["last_digits"] == "*1234", "Неверный номер карты"

@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """
    Фикстура, возвращающая пример DataFrame для тестов get_card_data.
    """
    data = {
        "Номер карты": ["*1234", "*5678", "*1234", "*9012", "*5678"],
        "Сумма платежа": [-100.0, -50.0, -25.0, -75.0, -10.0],
    }
    return pd.DataFrame(data)

# Тесты для get_top_transactions


def test_get_top_transactions_empty_dataframe() -> None:
    """
    Тест для случая, когда DataFrame пустой.
    """
    empty_df = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": [], "Описание": []})
    result = get_top_transactions(empty_df)
    assert result == [], "Для пустого DataFrame должен возвращаться пустой список"


def test_get_top_transactions_less_than_5_transactions(sample_dataframe_top_transactions: pd.DataFrame) -> None:
    """
    Тест, когда в DataFrame меньше 5 транзакций.
    """
    df = sample_dataframe_top_transactions.sort_values(by="Сумма платежа", ascending=True).head(
        3
    )  # Сначала сортируем, потом берем 3 строки
    result = get_top_transactions(df)
    assert len(result) == 3, "Должно быть возвращено 3 транзакции"
    assert result[0]["amount"] == -800.00, "Неверная сортировка (первая транзакция)"
    assert result[1]["amount"] == -564.00, "Неверная сортировка (вторая транзакция)"
    assert result[2]["amount"] == -160.89, "Неверная сортировка (третья транзакция)"


def test_get_top_transactions_exactly_5_transactions(sample_dataframe_top_transactions: pd.DataFrame) -> None:
    """
    Тест, когда в DataFrame ровно 5 транзакций.
    """
    df = sample_dataframe_top_transactions.sort_values(by="Сумма платежа", ascending=True).head(5)
    result = get_top_transactions(df)
    assert len(result) == 5, "Должно быть возвращено 5 транзакций"
    assert result[0]["amount"] == -800.00, "Неверная сортировка (первая транзакция)"
    assert result[1]["amount"] == -564.00, "Неверная сортировка (вторая транзакция)"
    assert result[2]["amount"] == -160.89, "Неверная сортировка (третья транзакция)"
    assert result[3]["amount"] == -118.12, "Неверная сортировка (четвертая транзакция)"
    assert result[4]["amount"] == -78.05, "Неверная сортировка (пятая транзакция)"


def test_get_top_transactions_more_than_5_transactions(sample_dataframe_top_transactions: pd.DataFrame) -> None:
    """
    Тест, когда в DataFrame больше 5 транзакций.
    """
    df = sample_dataframe_top_transactions.sort_values(by="Сумма платежа", ascending=True)
    result = get_top_transactions(df)
    assert len(result) == 5, "Должно быть возвращено 5 транзакций"
    assert result[0]["amount"] == -800.00, "Неверная сортировка (первая транзакция)"
    assert result[1]["amount"] == -564.00, "Неверная сортировка (вторая транзакция)"
    assert result[2]["amount"] == -160.89, "Неверная сортировка (третья транзакция)"
    assert result[3]["amount"] == -118.12, "Неверная сортировка (четвертая транзакция)"
    assert result[4]["amount"] == -78.05, "Неверная сортировка (пятая транзакция)"


def test_get_top_transactions_date_format(sample_dataframe_top_transactions: pd.DataFrame) -> None:
    """
    Тест, что дата отформатирована правильно.
    """
    result = get_top_transactions(sample_dataframe_top_transactions)
    for transaction in result:
        assert isinstance(transaction["date"], str), "Дата должна быть строкой"
        assert len(transaction["date"]) == 10, "Длина строки даты должна быть 10 символов"
        assert transaction["date"][2] == ".", "Разделитель в дате должен быть точкой"
        assert transaction["date"][5] == ".", "Разделитель в дате должен быть точкой"

@pytest.fixture
def sample_dataframe_top_transactions() -> pd.DataFrame:
    """
    Фикстура, возвращающая пример DataFrame для тестов get_top_transactions.
    """
    data = {
        "Отчет по операциям": [
            {
                "Дата операции": "31.12.2021 16:44:00",
                "Дата платежа": "31.12.2021",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -160.89,
                "Валюта операции": "RUB",
                "Сумма платежа": -160.89,
                "Валюта платежа": "RUB",
                "Категория": "Супермаркеты",
                "MCC": 5411,
                "Описание": "Колхоз",
                "Бонусы (включая кэшбэк)": 3,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 160.89,
            },
            {
                "Дата операции": "31.12.2021 16:42:04",
                "Дата платежа": "31.12.2021",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -64,
                "Валюта операции": "RUB",
                "Сумма платежа": -64,
                "Валюта платежа": "RUB",
                "Категория": "Супермаркеты",
                "MCC": 5411,
                "Описание": "Колхоз",
                "Бонусы (включая кэшбэк)": 1,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 64,
            },
            {
                "Дата операции": "31.12.2021 16:39:04",
                "Дата платежа": "31.12.2021",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -118.12,
                "Валюта операции": "RUB",
                "Сумма платежа": -118.12,
                "Валюта платежа": "RUB",
                "Категория": "Супермаркеты",
                "MCC": 5411,
                "Описание": "Магнит",
                "Бонусы (включая кэшбэк)": 2,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 118.12,
            },
            {
                "Дата операции": "31.12.2021 15:44:39",
                "Дата платежа": "31.12.2021",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": -78.05,
                "Валюта операции": "RUB",
                "Сумма платежа": -78.05,
                "Валюта платежа": "RUB",
                "Категория": "Супермаркеты",
                "MCC": 5411,
                "Описание": "Колхоз",
                "Бонусы (включая кэшбэк)": 1,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 78.05,
            },
            {
                "Дата операции": "31.12.2021 01:23:42",
                "Дата платежа": "31.12.2021",
                "Номер карты": "*5091",
                "Статус": "OK",
                "Сумма операции": -564,
                "Валюта операции": "RUB",
                "Сумма платежа": -564,
                "Валюта платежа": "RUB",
                "Категория": "Различные товары",
                "MCC": 5399,
                "Описание": "Ozon.ru",
                "Бонусы (включая кэшбэк)": 5,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 564,
            },
            {
                "Дата операции": "31.12.2021 00:12:53",
                "Дата платежа": "31.12.2021",
                "Статус": "OK",
                "Сумма операции": -800,
                "Валюта операции": "RUB",
                "Сумма платежа": -800,
                "Валюта платежа": "RUB",
                "Категория": "Переводы",
                "Описание": "Константин Л.",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 800,
            },
        ]
    }
    df = pd.DataFrame(data["Отчет по операциям"])
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    return df


# Тесты для get_currency_rates


def test_get_currency_rates_success(currencies: List[str], mock_response: MagicMock) -> None:
    """
    Тест для успешного получения курсов валют.
    """
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        result = get_currency_rates(currencies)
        assert "USD" in result, "USD должен быть в результатах"
        assert "EUR" in result, "EUR должен быть в результатах"
        assert "GBP" in result, "GBP должен быть в результатах"
        assert "RUB" not in result, "RUB не должен быть в результатах"
        assert result["USD"] == 75.0, "Неверный курс USD"
        assert result["EUR"] == 85.0, "Неверный курс EUR"
        assert result["GBP"] == 100.0, "Неверный курс GBP"


def test_get_currency_rates_api_error(currencies: List[str]) -> None:
    """
    Тест для случая, когда API возвращает ошибку.
    """
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        result = get_currency_rates(currencies)
        assert "USD" in result, "USD должен быть в результатах"
        assert "EUR" in result, "EUR должен быть в результатах"
        assert "GBP" in result, "GBP должен быть в результатах"
        assert result["USD"] is None, "Курс USD должен быть None при ошибке API"
        assert result["EUR"] is None, "Курс EUR должен быть None при ошибке API"
        assert result["GBP"] is None, "Курс GBP должен быть None при ошибке API"


def test_get_currency_rates_rub_excluded(currencies: List[str]) -> None:
    """
    Тест, что RUB исключается из запросов к API.
    """
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {}  # Пустой ответ, чтобы тест был минимальным
        result = get_currency_rates(currencies)

        # Проверка количества вызовов
        assert mock_get.call_count == 3, "Должно быть 3 запроса (USD, EUR, GBP)"

        # Проверка URL (чтобы RUB не было в запросах)
        for call in mock_get.call_args_list:
            url = call[0][0]  # Получаем URL из аргументов вызова
            assert "RUB" not in url, f"Запрос к API содержит RUB: {url}"

        # Проверка возвращаемого значения (добавлено)
        assert isinstance(result, dict), "Должен возвращаться словарь"
        assert len(result) == 3, "Должно быть 3 элемента в словаре (USD, EUR, GBP)"
        assert all(key in result for key in ["USD", "EUR", "GBP"]), "Словарь должен содержать ключи USD, EUR, GBP"
        assert all(value is None for value in result.values()), "Значения должны быть None (т.к. ответ пустой)"


@pytest.mark.parametrize(
    "currency, expected_value",
    [
        ("USD", 75.0),
        ("EUR", 85.0),
        ("GBP", 100.0),
    ],
)
def test_get_currency_rates_parameterized(
    currencies: List[str], mock_response: Dict[str, Any], currency: str, expected_value: float
) -> None:
    """
    Параметризованный тест для проверки курса каждой валюты.
    """
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        result = get_currency_rates(currencies)
        assert result[currency] == expected_value, f"Неверный курс для {currency}"
