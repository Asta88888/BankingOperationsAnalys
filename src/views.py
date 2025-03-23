import json
from datetime import datetime
import pandas as pd

from src.utils import (common_cards_info, exchange_rate, get_date, greeting, path_excel, path_json, reader_excel,
                       stock_price, top_five_transactions)


def get_main_page_info(transactions: pd.DataFrame, date_str: str):
    """Главная функция объединяет все функции из utils и выводит результат
    в формате JSON"""
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_of_month = datetime(date.year, date.month, 1, 0, 0, 0)
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y", errors='coerce')
    transactions_filtered = transactions[
        (transactions["Дата платежа"] >= start_of_month) & (transactions["Дата платежа"] <= date)
        ]
    cards_info = common_cards_info(transactions_filtered).to_dict(orient="records")
    transactions_info = (
        top_five_transactions(transactions_filtered)
        .rename(
            columns={
                "Дата платежа": "date",
                "Сумма платежа": "amount",
                "Категория": "category",
                "Описание": "description",
            }
        )
        .to_dict(orient="records")
    )
    for transaction in transactions_info:
        transaction["date"] = transaction["date"].strftime("%Y-%m-%d %H:%M:%S")
    currency_rates = exchange_rate(path_json)
    stock_prices = stock_price(path_json)
    current_time = get_date()
    greet = greeting(current_time)
    result = {
        "greeting": greet,
        "cards": cards_info,
        "top_transactions": transactions_info,
        "currency_rates": [{"currency": key, "rate": value} for key, value in currency_rates.items()],
        "stock_prices": [{"stock": key, "price": value} for key, value in stock_prices.items()],
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    transactions_df = reader_excel(path_excel)
    date = "2021-09-11 13:27:52"
    result_json = get_main_page_info(transactions_df, date)
    print(result_json)
