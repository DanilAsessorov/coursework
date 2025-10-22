import argparse
import logging
import pandas as pd
from reports import spending_by_category, spending_by_weekday, spending_by_workday

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def main(transactions_file: str, category: str):
    try:
        # Загрузка данных о транзакциях из CSV файла
        transactions = pd.read_csv(transactions_file)

        # Генерация отчета по категориям расходов
        category_report = spending_by_category(transactions, category)
        logging.info("Отчёт по категориям сформирован.")

        # Вывод отчета по категориям
        print("Отчет по категориям расходов:")
        print(category_report)

        # Генерация отчета по дням недели
        weekday_report = spending_by_weekday(transactions)
        logging.info("Отчёт по дням недели сформирован.")

        # Вывод отчета по дням недели
        print("Отчет по дням недели:")
        print(weekday_report)

        # Генерация отчета по рабочим и выходным дням
        workday_report = spending_by_workday(transactions)
        logging.info("Отчёт по рабочим/выходным дням сформирован.")

        # Вывод отчета по рабочим и выходным дням
        print("Отчет по рабочим и выходным дням:")
        print(workday_report)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генерация финансовых отчетов.")
    parser.add_argument("transactions_file", type=str, help="Путь к файлу транзакций (CSV)")
    parser.add_argument("--category", type=str, help="Категория для отчета по расходам", default="Все")

    args = parser.parse_args()
    main(args.transactions_file, args.category)