from datetime import datetime


def filter_transactions_by_date(transactions: list, valid_date_str: str) -> list:
    """
    Фильтрует транзакции за указанный месяц, где дата операции меньше или равна valid_date

    Параметры:
    transactions (list): список словарей с операциями
    valid_date_str (str): строка с датой в формате YYYY-MM-DD HH:MM:SS

    Возвращает:
    list: отфильтрованный список словарей
    """
    try:
        valid_date = datetime.strptime(valid_date_str, '%Y-%m-%d %H:%M:%S')

        filtered_transactions = [
            transaction
            for transaction in transactions
            if (datetime.strptime(transaction['Дата операции'], '%Y-%m-%d %H:%M:%S') <= valid_date and
                datetime.strptime(transaction['Дата операции'], '%Y-%m-%d %H:%M:%S').month == valid_date.month and
                datetime.strptime(transaction['Дата операции'], '%Y-%m-%d %H:%M:%S').year == valid_date.year)
        ]

        return filtered_transactions
    except ValueError as e:
        print(f"Ошибка при обработке даты: {e}")
        return []


# Пример использования
# converted_date_operations = [
#     {
#         'Дата операции': '2018-01-01 20:27:51',
#         'Дата платежа': '04.01.2018',
#         'Номер карты': '*7197',
#         'Статус': 'OK',
#         'Сумма операции': -316.0,
#         'Валюта операции': 'RUB',
#         'Сумма платежа': -316.0,
#         'Валюта платежа': 'RUB',
#         'Кэшбэк': None,
#         'Категория': 'Красота',
#         'MCC': 5977.0,
#         'Описание': 'OOO Balid',
#         'Бонусы (включая кэшбэк)': 6,
#         'Округление на  инвесткопилку': 0,
#         'Сумма операции с округлением': 316.0},
#     {
#         'Дата операции': '2018-01-01 12:49:53',
#         'Дата платежа': '01.01.2018',
#         'Номер карты': None,
#         'Статус': 'OK',
#         'Сумма операции': -3000.0,
#         'Валюта операции': 'RUB',
#         'Сумма платежа': -3000.0,
#         'Валюта платежа': 'RUB',
#         'Кэшбэк': None,
#         'Категория': 'Переводы',
#         'MCC': None,
#         'Описание': 'Линзомат ТЦ Юность',
#         'Бонусы (включая кэшбэк)': 0,
#         'Округление на инвесткопилку': 0,
#         'Сумма операции с округлением': 3000.0
#     }
# ]
#
# valid_date = '2018-01-01 20:27:55'
#
# filtered_transactions = filter_transactions_by_date(converted_date_operations, valid_date)
# print(filtered_transactions)