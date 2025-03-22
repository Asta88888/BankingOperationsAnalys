import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

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


def reader_excel(path: str) -> pd.DataFrame:
    """Функция считывает данные excel файла и возвращает
    список словарей с транзакциями"""
    logger.info("Выполняется чтение данных о транзакциях Excel-файла")
    try:
        df = pd.read_excel(path)
        return df
    except Exception as e:
        logger.error(f"Ошибка при чтении Excel-файла: {e}")
        return pd.DataFrame()


def get_date() -> str:
    """Функция возвращает текущее время"""
    logger.info("Получение текущего времени")
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_date


def greeting(time_str: str) -> str:
    """Функция приветствует пользователя, выбирая «Доброе утро» /
    «Добрый день» / «Добрый вечер» / «Доброй ночи» в зависимости
    от текущего времени"""
    try:
        parsed_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        hour = parsed_time.hour
        if 5 <= hour <= 12:
            return "Доброе утро"
        elif 13 <= hour <= 18:
            return "Добрый день"
        elif 19 <= hour <= 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except ValueError:
        return "Ошибка: неверный формат даты и времени"


def common_cards_info(df: pd.DataFrame) -> pd.DataFrame:
    """Функция выдает общую информацию(последние 4 цифры карты;
    общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей))
    по каждой карте"""
    logger.info("Получение информации по каждой карте")
    try:
        df["cashback"] = df["Сумма операции"] / 100
        grouped = df.groupby("Номер карты", as_index=False).agg(
            total_spent=("Сумма операции", "sum"),
            cashback=("cashback", "sum"),
        )
        grouped.rename(columns={"Номер карты": "last_digits"}, inplace=True)
        return grouped
    except KeyError as e:
        logger.error(f"Отсутствует ключ в данных транзакции: {e}")
    logger.info("Получена информация по каждой карте")
    return pd.DataFrame()


def top_five_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Функция возвращает Топ-5 транзакций по сумме платежа"""
    logger.info("Получение 5 транзакций по наибольшей сумме")
    try:
        top_five = df.sort_values(by="Сумма платежа", key=abs, ascending=False).head(5)
        logger.info("Получены 5 транзакций по наибольшей сумме")
        return top_five[["Дата платежа", "Сумма платежа", "Категория", "Описание"]]
    except KeyError as e:
        logger.error(f"Ошибка в данных транзакций {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Ошибка при обработке транзакций {e}")
        return pd.DataFrame()


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


# current_time = get_date()
# print(greeting(current_time))
# df = reader_excel(path_excel)
# data_c = common_cards_info(df)
# data_t = top_five_transactions(df)
# print(reader_excel(path_excel))
# print(get_date())
# print(data_c)
# print(data_t)
# print(exchange_rate(path_json))
# print(stock_price(path_json))
