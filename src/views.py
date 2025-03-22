import json

import pandas as pd

from src.utils import (common_cards_info, exchange_rate, get_date, greeting, path_excel, path_json, reader_excel,
                       stock_price, top_five_transactions)


def get_main_page_info(transactions: pd.DataFrame, date: str):
    """Главная функция объединяет все функции из utils и выводит результат
    в формате JSON"""
    cards_info = common_cards_info(transactions).to_dict(orient="records")
    transactions_info = (
        top_five_transactions(transactions)
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
    currency_rates = exchange_rate(path_json)
    stock_prices = stock_price(path_json)

    result = {
        "cards": cards_info,
        "top_transactions": transactions_info,
        "currency_rates": [{"currency": key, "rate": value} for key, value in currency_rates.items()],
        "stock_prices": [{"stock": key, "price": value} for key, value in stock_prices.items()],
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    current_time = get_date()
    greet = greeting(current_time)
    print(greet)
    transactions_df = reader_excel(path_excel)
    date = "2021-09-11"
    result_json = get_main_page_info(transactions_df, date)
    print(result_json)
