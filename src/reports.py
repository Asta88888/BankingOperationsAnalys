import pandas as pd
import logging
import os
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")

log_dir = "../logs"
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger("reports.py")
file_handler = logging.FileHandler(os.path.join(log_dir, "reports.log"), encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
logger.debug("Debug message")


def report_to_file(filename=None):
    """Декоратор для записи результата функции-отчета в файл"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            output_filename = filename or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            info_to_write = result.to_dict(orient='records') if isinstance(result, pd.DataFrame) else result

            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(info_to_write, f, ensure_ascii=False, indent=4)

            logger.info(f"Отчет сохранен в {output_filename}")
            return result
        return wrapper
    return decorator


@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца от указанной даты"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    end_date = datetime.strptime(date, '%Y-%m-%d')
    start_date = end_date - pd.DateOffset(months=3)
    logger.debug(f"Фильтруем данные по категории: {category}, с {start_date} по {end_date}")
    filtered_data = transactions[
        (transactions['Категория'] == category) &
        (transactions['Дата платежа'] >= start_date.strftime('%Y-%m-%d')) &
        (transactions['Дата платежа'] <= end_date.strftime('%Y-%m-%d')) &
        (transactions['Сумма операции'] < 0)
        ]
    logger.debug(f"Найдено {len(filtered_data)} записей по категории {category}.")
    return filtered_data


if __name__ == "__main__":
    try:
        df = pd.read_excel(path)
        logger.debug(f"Загружено {len(df)} строк.")
        df['Дата платежа'] = pd.to_datetime(df['Дата платежа'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
        logger.debug(f"Уникальные категории в данных: {df['Категория'].unique()}")
        category = "Супермаркеты"
        if category not in df['Категория'].unique():
            logger.warning(f"Категория '{category}' не найдена в данных.")
        report = spending_by_category(df, category, date="2021-12-31")
        if report.empty:
            logger.warning(f"Отчет по категории '{category}' пуст.")
        else:
            print(report)
    except Exception as e:
        logger.error(f"Ошибка при выполнении скрипта: {e}")
