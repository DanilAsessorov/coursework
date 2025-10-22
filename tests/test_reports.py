import pytest
import pandas as pd
from datetime import datetime
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday


# Фикстура для создания примерного DataFrame для тестов
@pytest.fixture
def sample_dataframe():
    data = {
        "Дата операции": [
            datetime(2024, 1, 5),
            datetime(2024, 1, 12),
            datetime(2024, 1, 20),
            datetime(2024, 2, 10),
            datetime(2024, 2, 25),
            datetime(2024, 3, 15),
        ],
        "Сумма платежа": [-100, -200, -150, -50, -175, -300],
        "Категория": ["А", "Б", "А", "А", "Б", "А"],
    }
    return pd.DataFrame(data)


# Тест для spending_by_category
def test_spending_by_category(sample_dataframe):
    result = spending_by_category(sample_dataframe, category="А")
    expected_data = {
        "Дата операции": [datetime(2024, 1, 5), datetime(2024, 1, 20), datetime(2024, 2, 25)],
        "Сумма платежа": [100, 150, 175]  # суммы должны быть положительными
    }
    expected_df = pd.DataFrame(expected_data).set_index("Дата операции")
    pd.testing.assert_frame_equal(result.set_index(result.index), expected_df)


# Тест для spending_by_weekday
def test_spending_by_weekday(sample_dataframe):
    result = spending_by_weekday(sample_dataframe)

    # Ожидаемая сумма расходов по дням недели
    expected_data = {
        "День недели": ["пятница", "суббота", "воскресенье"],
        "Сумма платежа": [100, 175, 150]
    }
    expected_df = pd.DataFrame(expected_data).set_index("День недели")
    pd.testing.assert_frame_equal(result.set_index(result.index), expected_df)


# Тест для spending_by_workday
def test_spending_by_workday(sample_dataframe):
    result = spending_by_workday(sample_dataframe)

    # Ожидаемая сумма расходов в рабочий и выходной дни
    expected_data = {
        "Тип дня": ["Рабочий", "Выходной"],
        "Сумма платежа": [150, 275]  # примерные значения
    }
    expected_df = pd.DataFrame(expected_data).set_index("Тип дня")
    pd.testing.assert_frame_equal(result.set_index(result.index), expected_df)
