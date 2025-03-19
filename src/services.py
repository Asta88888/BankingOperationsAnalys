import json
from collections import defaultdict
from datetime import datetime
import math
from functools import reduce
from typing import Any
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


def profitable_cashback(transactions: list[dict[str, Any]], year: int, month: int) -> str | dict[Any, Any]:
    """Фильтрует транзакции по заданному периоду, исключает приходные операции и рассчитывает кэшбэк."""
    logger.info(f"Обработка транзакций за {month}/{year}")
    try:
        filtered_transactions = []
        for transaction in transactions:
            date_value = transaction.get("Дата платежа")
            amount = transaction.get("Сумма платежа")
            if not date_value or (isinstance(date_value, float) and math.isnan(date_value)):
                continue
            try:
                transaction_date = datetime.strptime(str(date_value).strip(), "%d.%m.%Y")
            except ValueError:
                logger.warning(f"Неверный формат даты: {date_value}")
                continue
            if transaction_date.year == year and transaction_date.month == month and amount < 0:
                filtered_transactions.append(transaction)
        if not filtered_transactions:
            logger.warning("Нет подходящих транзакций для расчета кэшбэка")
            return {}


        def accumulate_expenses(category_totals: dict[str, int], transaction: dict[str, Any]) -> dict[str, int]:
            category = transaction.get("Категория", "Прочее")
            amount = abs(transaction.get("Сумма платежа", 0))
            category_totals[category] += amount
            return category_totals
        total_expenses_by_category = reduce(accumulate_expenses, filtered_transactions, defaultdict(int))
        cashback_by_category = {category: round(amount * 0.01) for category, amount in
                                total_expenses_by_category.items()}
        sorted_cashback = dict(sorted(cashback_by_category.items(), key=lambda item: item[1], reverse=True))
        logger.info("Кэшбэк успешно рассчитан")
        return json.dumps(sorted_cashback, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при обработке транзакций: {e}")
        return {}


transactions = reader_excel(path_excel)
cashback = profitable_cashback(transactions, 2021, 11)
print(cashback)
