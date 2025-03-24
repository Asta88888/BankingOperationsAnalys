from src.views import get_main_page_info
from src.reports import spending_by_category
from src.services import profitable_cashback
from src.utils import path_excel
import pandas as pd
from src.services import reader_excel_2
from src.utils import reader_excel


def main():
    df = pd.read_excel(path_excel)
    transactions = reader_excel_2(path_excel)
    # date = "2021-09-11 13:27:52"
    # result_json = get_main_page_info(transactions_df, date)
    # print(result_json)
    # category = "Супермаркеты"
    # df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y").dt.strftime("%Y-%m-%d")
    # report = spending_by_category(df, category, date="2021-12-31")
    # print(report)
    # cashback = profitable_cashback(transactions, 2021, 11)
    # print(cashback)


if __name__ == "__main__":
    main()