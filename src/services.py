import json
from collections import defaultdict
from datetime import datetime
import math
from functools import reduce
from typing import Any, Callable, Never, DefaultDict
from src.utils import reader_excel, path_excel
import logging
import os

log_dir = "../logs"
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger("services.py")
file_handler = logging.FileHandler(os.path.join(log_dir, "services.log"), encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
logger.debug("Debug message")


def profitable_cashback(transactions_list: list[dict[str, Any]], year: int, month: int) -> list[dict[str, Any]]:
    """Функция фильтрует транзакции по заданному периоду"""
    logger.info(f"Фильтрация транзакций за {month}/{year}")
    filtered_by_date = []
    try:
        for transaction in transactions_list:
            date_value = transaction.get("Дата платежа")
            if (
                date_value is None
                or (isinstance(date_value, float) and math.isnan(date_value))
                or str(date_value).strip().lower() == "nan"
            ):
                continue
            transaction_date = datetime.strptime(str(date_value).strip(), "%d.%m.%Y")
            if transaction_date.year == year and transaction_date.month == month:
                filtered_by_date.append(transaction)
        logger.info("Транзакции отфильтрованы")
        return filtered_by_date
    except Exception as e:
        logger.error(f"Ошибка при фильтрации транзакций {e}")
        return []


def accumulate_expenses(category_totals: dict[str, int], transaction: dict[str, Any]) -> dict[str, int]:
    """Функция суммирует расходы по категориям"""
    logger.info("Получение суммы транзакций по категориям")
    try:
        category = transaction["Категория"]
        amount = abs(transaction["Сумма платежа"])
        category_totals[category] += amount
        logger.info("Получены суммы транзакций по категориям")
        return category_totals
    except KeyError as e:
        logger.error(f"Ошибка в ключе транзакций {e}")
        return category_totals


def calculate_cashback(filtered_transactions: list[dict[str, Any]]) -> str | dict[Any, Any]:
    """Функция рассчитывает кэшбэк по каждой категории в размере 1%"""
    logger.info("Получение кэшбэка по категориям")
    try:
        total_expenses_by_category = reduce(accumulate_expenses, transactions, defaultdict(int))
        cashback_by_category = {
            category: round(amount * 0.01) for category, amount in total_expenses_by_category.items()
        }
        sorted_cashback = dict(sorted(cashback_by_category.items(), key=lambda item: item[1], reverse=True))
        logger.info("Получен кэшбэк по категориям")
        return json.dumps(sorted_cashback, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при расчете кэшбэка: {e}")
        return {}


transactions = reader_excel(path_excel)
# filtered_by_date = profitable_cashback(transactions, 2018, 1)
# cashback = calculate_cashback(filtered_by_date)
# print(cashback)
