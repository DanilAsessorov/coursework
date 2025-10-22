from datetime import datetime, time
from typing import Any, Dict, Generator, List
from unittest.mock import AsyncMock, mock_open, patch

import pandas as pd
import pytest
from pandas import DataFrame
from tinkoff.invest import Client

REPORTS_DIRECTORY = "reports"
DEFAULT_REPORT_FILENAME = "{}_report_{}.json"


@pytest.fixture
def morning_time() -> time:
    return time(hour=8, minute=0, second=0)


@pytest.fixture
def afternoon_time() -> time:
    return time(hour=14, minute=0, second=0)


@pytest.fixture
def evening_time() -> time:
    return time(hour=20, minute=0, second=0)


@pytest.fixture
def night_time() -> time:
    return time(hour=2, minute=0, second=0)

@pytest.fixture
def mock_response() -> Dict[str, Any]:
    """
    Фикстура, возвращающая пример ответа API (JSON).
    """
    mock_data = {"Valute": {"USD": {"Value": 75.0}, "EUR": {"Value": 85.0}, "GBP": {"Value": 100.0}}}
    return mock_data


@pytest.fixture
def currencies() -> List[str]:
    """
    Фикстура, возвращающая список валют для тестирования.
    """
    return ["USD", "EUR", "GBP", "RUB"]


@pytest.fixture(scope="function")
def mock_client_instruments() -> Client:
    """
    Фикстура для создания мокированного Client для instruments.shares.
    """

    class MockInstrumentsResponse:
        def __init__(self, instruments: Any) -> None:
            self.instruments = instruments

    class MockClient(Client):  # Создаем подкласс Client
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, **kwargs)
            self.instruments = AsyncMock()  # Добавляем instruments в подкласс

    async def mock_shares(instrument_status: Any) -> MockInstrumentsResponse:
        # Пример использования instrument_status
        if instrument_status:
            # Фильтрация или использование по вашему усмотрению
            pass  # здесь может быть ваша логика

        # Создаем DataFrame с инструментами
        instruments_data = [
            {"ticker": "AAPL", "figi": "BBG000B9XRY4"},
            {"ticker": "AMZN", "figi": "BBG000B9XRY5"},
            {"ticker": "GOOG", "figi": "BBG000B9XRY6"},
        ]
        instruments_df = DataFrame(instruments_data)
        return MockInstrumentsResponse(instruments=instruments_df.to_dict("records"))

    # mock_client = Client("test_token")  # Создаем экземпляр Client с фиктивным токеном
    mock_client: MockClient = MockClient("test_token")
    # mock_client.instruments = AsyncMock()
    mock_client.instruments.shares = mock_shares
    return mock_client


@pytest.fixture(scope="function")
def tickers() -> List[str]:
    """
    Фикстура для списка тикеров.
    """
    return ["AAPL", "AMZN"]


@pytest.fixture
def sample_dataframe_by_month() -> pd.DataFrame:
    """
    Фикстура, возвращающая пример DataFrame с транзакциями.
    """
    data = {
        "Дата операции": [
            datetime(2024, 1, 5),
            datetime(2024, 1, 12),
            datetime(2024, 1, 20),
            datetime(2024, 2, 10),
            datetime(2024, 2, 25),
            datetime(2024, 3, 15),
        ],
        "Сумма платежа": [10, 20, 30, 40, 50, 60],
        "Категория": ["A", "B", "A", "B", "A", "B"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_expenses_dataframe() -> pd.DataFrame:
    """
    Фикстура, возвращающая пример DataFrame с транзакциями расходов.
    """
    data = {
        "Дата операции": [
            datetime(2024, 1, 5),
            datetime(2024, 1, 12),
            datetime(2024, 1, 20),
            datetime(2024, 2, 10),
            datetime(2024, 2, 25),
            datetime(2024, 3, 15, 0, 0, 0, 0),
        ],
        "Сумма платежа": [-10, -20, -30, -40, -50, -60],  # A  # B  # A  # B  # A  # Наличные
        "Категория": ["A", "B", "A", "B", "A", "Наличные"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_income_dataframe() -> pd.DataFrame:
    """
    Фикстура, возвращающая пример DataFrame с транзакциями доходов.
    """
    data = {
        "Дата операции": [
            datetime(2024, 1, 5),
            datetime(2024, 1, 12),
            datetime(2024, 1, 20),
            datetime(2024, 2, 10),
            datetime(2024, 2, 25),
            datetime(2024, 3, 15),
        ],
        "Сумма платежа": [
            100,  # Зарплата
            200,  # Подработка
            300,  # Зарплата
            400,  # Подработка
            500,  # Зарплата
            600,  # Инвестиции
        ],
        "Категория": ["Зарплата", "Подработка", "Зарплата", "Подработка", "Зарплата", "Инвестиции"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_cashback_dataframe() -> pd.DataFrame:
    """
    Фикстура, возвращающая пример DataFrame с транзакциями для анализа кешбэка.
    """
    data = {
        "Дата операции": [
            datetime(2024, 1, 5),
            datetime(2024, 1, 12),
            datetime(2024, 1, 20),
            datetime(2024, 2, 10),
            datetime(2024, 2, 25),
            datetime(2024, 2, 29),
            datetime(2024, 3, 15),
        ],
        "Сумма платежа": [
            -100,  # A
            -200,  # B
            -300,  # A
            -400,  # B
            -500,  # A
            -600,  # C
            100,  # income, not used for cashback
        ],
        "Категория": ["A", "B", "A", "B", "A", "C", "Income"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_search_dataframe() -> pd.DataFrame:
    """
    Фикстура, возвращающая пример DataFrame для поиска.
    """
    data = {
        "Дата операции": [datetime(2024, 1, 5), datetime(2024, 1, 12), datetime(2024, 1, 20), datetime(2024, 2, 10)],
        "Дата платежа": [datetime(2024, 1, 6), datetime(2024, 1, 13), datetime(2024, 1, 21), datetime(2024, 2, 11)],
        "Описание": ["Покупка в магазине ABC", "Оплата услуг XYZ", "Покупка в магазине DEF", "Перевод"],
        "Категория": ["Продукты", "Интернет", "Продукты", "Переводы"],
        "Сумма платежа": [-100, -50, -75, 100],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_phone_dataframe() -> pd.DataFrame:
    """
    Фикстура, возвращающая пример DataFrame для поиска телефонных номеров.
    """
    data = {
        "Дата операции": [datetime(2024, 1, 5), datetime(2024, 1, 12), datetime(2024, 1, 20), datetime(2024, 2, 10)],
        "Дата платежа": [datetime(2024, 1, 6), datetime(2024, 1, 13), datetime(2024, 1, 21), datetime(2024, 2, 11)],
        "Описание": [
            "Оплата по номеру +7 (912) 345-67-89",
            "Перевод другу 8 (903) 123 45 67",
            "Покупка в магазине, номер телефона +1234567890",
            "Обычная покупка",
        ],
        "Категория": ["Переводы", "Переводы", "Продукты", "Продукты"],
        "Сумма платежа": [-100, -50, -75, -20],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_person_transfers_dataframe() -> DataFrame:
    """
    Фикстура, возвращающая пример DataFrame для поиска переводов физлицам.
    """
    data = {
        "Дата операции": [
            datetime(2024, 1, 5),
            datetime(2024, 1, 12),
            datetime(2024, 1, 20),
            datetime(2024, 2, 10),
            datetime(2024, 2, 15),
        ],
        "Дата платежа": [
            datetime(2024, 1, 6),
            datetime(2024, 1, 13),
            datetime(2024, 1, 21),
            datetime(2024, 2, 11),
            datetime(2024, 2, 16),
        ],
        "Описание": [
            "Перевод Иванову И.",
            "Перевод Петрову А.",
            "Оплата услуг",
            "Перевод Сидорову Б.",
            "Перевод Орлову Г.",
        ],
        "Категория": ["Переводы", "Переводы", "Услуги", "Переводы", "Переводы"],
        "Сумма платежа": [-100, -50, -75, -20, -30],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_data() -> Dict[str, Any]:
    return {"key": "value", "number": 123}


@pytest.fixture
def sample_dataframe_by_date() -> pd.DataFrame:
    return pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})


@pytest.fixture
def mock_datetime_now() -> Generator[Any, None, None]:
    with patch("your_module.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 10, 27, 10, 30, 0)  # Set a fixed datetime
        yield mock_datetime


@pytest.fixture
def mock_os_makedirs() -> Generator[Any, None, None]:
    with patch("your_module.os.makedirs") as mock_makedirs:
        yield mock_makedirs


@pytest.fixture
def mock_open_file() -> Generator[Any, None, None]:
    with patch("your_module.open", mock_open()) as mock_file:
        yield mock_file
