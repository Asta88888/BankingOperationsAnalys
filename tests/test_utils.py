import unittest
from unittest import mock
import json
import os
from datetime import datetime
import pandas as pd
import requests
from src.utils import reader_excel, get_date, common_cards_info, top_five_transactions, exchange_rate, stock_price, aggregate_by_last_digits
import pytest

class TestReaderExcel(unittest.TestCase):

    @mock.patch("pandas.read_excel")
    def test_reader_excel_success(self, mock_read_excel):
        mock_df = pd.DataFrame({
            "Номер карты": [1234567890, 9876543210],
            "Сумма операции": [100, 200]
        })
        mock_read_excel.return_value = mock_df
        result = reader_excel("mock_path.xlsx")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Номер карты"], 1234567890)
        self.assertEqual(result[0]["Сумма операции"], 100)

    @mock.patch("pandas.read_excel")
    def test_reader_excel_failure(self, mock_read_excel):
        mock_read_excel.side_effect = Exception("File read error")
        result = reader_excel("mock_path.xlsx")
        self.assertEqual(result, [])


class TestCommonCardsInfo(unittest.TestCase):

    def test_common_cards_info(self):
        transactions = [
            {"Номер карты": 1234567890, "Сумма операции": 100},
            {"Номер карты": 9876543210, "Сумма операции": 200}
        ]
        result = common_cards_info(transactions)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["last_digits"], 1234567890)
        self.assertEqual(result[0]["total_spent"], 100)
        self.assertEqual(result[0]["cashback"], 1.0)


class TopFiveTransactions(unittest.TestCase):

    def test_top_five_transactions(self):
        transactions = [
            {"Сумма платежа": 100, "Дата платежа": "2025-03-16", "Категория": "Food", "Описание": "Lunch"},
            {"Сумма платежа": 200, "Дата платежа": "2025-03-15", "Категория": "Transport", "Описание": "Bus ticket"},
            {"Сумма платежа": 50, "Дата платежа": "2025-03-14", "Категория": "Entertainment", "Описание": "Cinema"}
        ]
        result = top_five_transactions(transactions)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["amount"], 200)
        self.assertEqual(result[2]["amount"], 50)


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


class TestAggregateByLastDigits(unittest.TestCase):

    def test_aggregate_by_last_digits(self):
        transactions = [
            {"last_digits": 1234, "total_spent": 100, "cashback": 1.0},
            {"last_digits": 1234, "total_spent": 200, "cashback": 2.0},
            {"last_digits": 5678, "total_spent": 50, "cashback": 0.5}
        ]
        result = aggregate_by_last_digits(transactions)
        self.assertEqual(result[1234]["total_spent"], 300)
        self.assertEqual(result[5678]["total_spent"], 50)

