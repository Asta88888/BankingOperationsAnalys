import os
import pandas as pd
from datetime import datetime
import json
import requests
from dotenv import load_dotenv
import logging
from typing import Any
from collections import defaultdict


log_dir = "../logs"
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger("utils.py")
file_handler = logging.FileHandler(os.path.join(log_dir, "utils.log"), encoding="utf-8", mode="w")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)
logger.debug("Debug message")

load_dotenv()
API_KEY_currency = os.getenv("API_KEY_currency")
API_KEY_stocks = os.getenv("API_KEY_stocks")

path_excel = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")
path_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_settings.json")


def reader_excel(path: str) -> list[dict[Any, Any]] | list[Any]:
    """Функция считывает данные excel файла и возвращает
    список словарей с транзакциями"""
    logger.info("Выполняется чтение данных о транзакциях Excel-файла")
    try:
        df = pd.read_excel(path)
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel-файла: {e}")
        return []


def get_date() -> str:
    """Функция возвращает текущее время"""
    logger.info("Получение текущего времени")
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_date


def common_cards_info(transactions_list: list[dict]) -> list[dict]:
    """Функция выдает общую информацию(последние 4 цифры карты;
    общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей))
    по каждой карте"""
    logger.info("Получение информации по каждой карте")
    cards = []
    for transaction in transactions_list:
        try:
            result = {
                "last_digits": transaction["Номер карты"],
                "total_spent": transaction["Сумма операции"],
                "cashback": round(transaction["Сумма операции"] / 100, 2),
            }
            cards.append(result)
        except KeyError as e:
            logger.error(f"Отсутствует ключ в данных транзакции: {e}")
    logger.info("Получена информация по каждой карте")
    return cards


def top_five_transactions(transactions_list: list[dict]) -> list[dict]:  # добавить трай эксепт
    """Функция возвращает Топ-5 транзакций по сумме платежа"""
    top_five_list = []
    logger.info("Получение 5 транзакций по наибольшей сумме")
    try:
        sorted_transactions = sorted(transactions_list, key=lambda x: abs(x["Сумма платежа"]), reverse=True)
        for transaction in sorted_transactions:
            result = {
                "date": transaction["Дата платежа"],
                "amount": transaction["Сумма платежа"],
                "category": transaction["Категория"],
                "description": transaction["Описание"],
            }
            top_five_list.append(result)
            if len(top_five_list) == 5:
                break
    except KeyError as e:
        logger.error(f"Ошибка в данных транзакций {e}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при обработке транзакций {e}")
        return []
    logger.info("Получены 5 транзакций по наибольшей сумме")
    return top_five_list


def exchange_rate(file_path: str) -> dict:
    """Функция считывает JSON-файл, обращается к стороннему сайту и показывает
    курс валют к заданной валюте"""
    logger.info("Открытие JSON-файла с транзакциями")
    logger.info("Обращение к стороннему сервису по ключу API за информацией по курсу валют")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            user_settings = json.load(f)
        currencies = user_settings.get("user_currencies")

        result = {}
        amount = 100
        url = "https://api.apilayer.com/exchangerates_data/convert"

        for currency in currencies:
            params = {"from": currency, "to": "RUB", "amount": amount}
            headers = {"apikey": f"{API_KEY_currency}"}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            result[currency] = data["result"]
        logger.info("Получены курсы валют")
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении курса валют: {e}")
        return {}


def stock_price(file_path: str) -> dict:
    """Функция считывает JSON-файл и получает актуальные цены акций со
    стороннего сервиса"""
    logger.info("Открытие JSON-файла с транзакциями")
    logger.info("Обращение к стороннему сервису по ключу API за информацией по ценам на акции")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            user_settings = json.load(f)
        stocks = user_settings.get("user_stocks")
        result = {}

        for stock in stocks:
            response = requests.get(f"https://api.twelvedata.com/price?symbol={stock}&apikey={API_KEY_stocks}")
            data = response.json()
            price = data.get("price")
            result[stock] = price
        logger.info("Получены цены акций")
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {e}")
        return {}


def aggregate_by_last_digits(transactions):
    """Функция дополняет функцию common_cards_info формируя группировку по картам
    и общей сумме и кэшбэку"""
    result = defaultdict(lambda: {"total_spent": 0, "cashback": 0})

    for transaction in transactions:
        last_digits = transaction["last_digits"]
        result[last_digits]["total_spent"] += transaction["total_spent"]
        result[last_digits]["cashback"] += transaction["cashback"]
    return dict(result)


# transactions = reader_excel(path_excel)
# data = common_cards_info(transactions)
# result = aggregate_by_last_digits(data)
# print(result)
# print(reader_excel(path_excel))
# print(get_date())
# print(common_cards_info(transactions))
# print(top_five_transactions(transactions))
# print(exchange_rate(path_json))
# print(stock_price(path_json))
# data = common_cards_info(transactions)

