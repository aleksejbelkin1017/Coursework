import os
import pandas as pd
import requests
import json

from datetime import datetime
from typing import Optional, Dict, List
from greeting_user import validate_datetime_format, greet_user
from file_reader import read_excel_transactions
from operations_transformation import convert_date_format
from filtered_operations import filter_transactions_by_date
from external_api import get_exchange_rates, convert_currency_rates, get_sp500_data, convert_stock_data


def calculate_card_stats(transactions: List[Dict]) -> List[Dict]:
    card_stats = {}

    for transaction in transactions:
        if pd.notna(transaction['Номер карты']):
            last_digits = transaction['Номер карты'][-4:]
            if last_digits not in card_stats:
                card_stats[last_digits] = {
                    'total_spent': 0,
                    'cashback': 0
                }

            card_stats[last_digits]['total_spent'] += abs(transaction['Сумма операции'])
            if pd.notna(transaction['Кэшбэк']):
                card_stats[last_digits]['cashback'] += transaction['Кэшбэк']

    return [
        {
            "last_digits": digits,
            "total_spent": round(stats['total_spent'], 2),
            "cashback": round(stats['cashback'], 2)
        }
        for digits, stats in card_stats.items()
    ]


def get_top_transactions(transactions: List[Dict], n: int = 5) -> List[Dict]:
    # Сортируем по абсолютной величине суммы операции
    sorted_transactions = sorted(
        transactions,
        key=lambda x: abs(x['Сумма операции']),
        reverse=True
    )

    return [
        {
            "date": transaction['Дата операции'].split()[0].replace('-', '.'),
            "amount": round(transaction['Сумма операции'], 2),
            "category": transaction['Категория'],
            "description": transaction['Описание']
        }
        for transaction in sorted_transactions[:n]
    ]


# def generate_response(transactions: List[Dict]) -> Dict:
#     response = {
#         "greeting": "Добрый день",
#         "cards": calculate_card_stats(transactions),
#         "top_transactions": get_top_transactions(transactions),
#         "currency_rates": [
#             {"currency": "USD", "rate": 73.21},
#             {"currency": "EUR", "rate": 87.08}
#         ],
#         "stock_prices": [
#             {"stock": "AAPL", "price": 150.12},
#             {"stock": "AMZN", "price": 3173.18},
#             {"stock": "GOOGL", "price": 2742.39},
#             {"stock": "MSFT", "price": 296.71},
#             {"stock": "TSLA", "price": 1007.08}
#         ]
#     }
#
#     return response


def answer_about_transactions(last_date: str) -> Dict:
    """
    Функция принимает на вход строку с датой и временем
    в формате YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ

    Параметры:
    last_date (str): строка с датой и временем

    Возвращает:
    dict: словарь с ответом
    """
    # Проверяем формат даты, введенной пользователем
    validate_datetime_format(last_date)

    # Здесь можно добавить логику работы с валидной датой
    # Например, получить транзакции до указанной даты и времени

    operations = read_excel_transactions()
    converted_date_operations = convert_date_format(operations)
    filtered_transactions = filter_transactions_by_date(converted_date_operations, last_date)
    card_num = calculate_card_stats(filtered_transactions)
    top_operations = get_top_transactions(filtered_transactions)
    exchange_rates = get_exchange_rates()
    converted_exchange_rates = convert_currency_rates(exchange_rates)

    responce = {
        "greeting": greet_user(),
        "cards": calculate_card_stats(filtered_transactions),
        "top_transactions": get_top_transactions(filtered_transactions),
        "currency_rates": convert_currency_rates(get_exchange_rates()),
        "stock_prices": convert_stock_data(get_sp500_data())
    }

    result = json.dumps(responce, ensure_ascii=False, indent=2)

    return result


# Примеры использования:
print(answer_about_transactions("2018-01-15 20:27:55"))  # Валидный формат
# print(answer_about_transactions("2018.01.02 20:27:55"))  # Невалидный формат



# if __name__ == '__main__':
#     answer_about_transactions()