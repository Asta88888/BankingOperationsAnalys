import pytest
import unittest
import json
import requests
import pandas as pd
from unittest import mock
from unittest.mock import patch
from src.utils import reader_excel, greeting, common_cards_info, top_five_transactions, exchange_rate, stock_price


@pytest.fixture
def sample_dataframe():
    data = {
        "Номер карты": ["1234", "5678", "1234", "5678"],
        "Сумма операции": [1000, 2000, 1500, 500],
        "Сумма платежа": [500, 200, 1000, 700],
        "Дата платежа": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"],
        "Категория": ["Еда", "Транспорт", "Одежда", "Развлечения"],
        "Описание": ["Обед", "Метро", "Футболка", "Кино"]
    }
    return pd.DataFrame(data)

@pytest.mark.parametrize("input_time, expected", [
    ("2025-01-01 06:00:00", "Доброе утро"),
    ("2025-01-01 14:00:00", "Добрый день"),
    ("2025-01-01 20:00:00", "Добрый вечер"),
    ("2025-01-01 02:00:00", "Доброй ночи"),
    ("invalid_time", "Ошибка: неверный формат даты и времени"),
])
def test_greeting(input_time, expected):
    assert greeting(input_time) == expected

@patch("pandas.read_excel")
def test_reader_excel(mock_read_excel):
    mock_read_excel.return_value = pd.DataFrame({"test": [1, 2, 3]})
    df = reader_excel("fake_path.xlsx")
    assert not df.empty
    assert "test" in df.columns

def test_common_cards_info(sample_dataframe):
    result = common_cards_info(sample_dataframe)
    assert not result.empty
    assert "cashback" in result.columns
    assert "total_spent" in result.columns

def test_top_five_transactions(sample_dataframe):
    result = top_five_transactions(sample_dataframe)
    assert len(result) <= 5
    assert "Сумма платежа" in result.columns


class TestExchangeRate(unittest.TestCase):

    @mock.patch("requests.get")
    def test_exchange_rate(self, mock_get):
        mock_response = mock.Mock()
        mock_response.json.return_value = {"result": 75.0}
        mock_get.return_value = mock_response
        mock_user_settings = {
            "user_currencies": ["USD", "EUR"]
        }
        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_user_settings))):
            result = exchange_rate("mock_path.json")
        self.assertEqual(result["USD"], 75.0)
        self.assertEqual(result["EUR"], 75.0)


class TestStockPrice(unittest.TestCase):

    @mock.patch("requests.get")
    def test_stock_price(self, mock_get):
        mock_response = mock.Mock()
        mock_response.json.return_value = {"price": 150.0}
        mock_get.return_value = mock_response
        mock_user_settings = {
            "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        }
        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(mock_user_settings))):
            result = stock_price("mock_path.json")
        self.assertEqual(result["AAPL"], 150.0)
        self.assertEqual(result["AMZN"], 150.0)
        self.assertEqual(result["GOOGL"], 150.0)
        self.assertEqual(result["MSFT"], 150.0)
        self.assertEqual(result["TSLA"], 150.0)


