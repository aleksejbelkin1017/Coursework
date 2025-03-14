from datetime import datetime
import pandas as pd
from file_reader import read_excel_transactions


def convert_date_format(transactions: list) -> list:
    """
    Преобразует формат даты в списке словарей

    Параметры:
    transactions (list): список словарей с операциями

    Возвращает:
    list: список словарей с преобразованными датами
    """
    try:
        # Создаем DataFrame из списка словарей
        df = pd.DataFrame(transactions)

        # Преобразуем столбец 'Дата операции' в datetime
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S')

        # Форматируем даты в нужный формат
        df['Дата операции'] = df['Дата операции'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Возвращаем список словарей с обновленными датами
        return df.to_dict('records')
    except Exception as e:
        print(f"Ошибка при преобразовании дат: {e}")
        return transactions  # Возвращаем исходные данные при ошибке


# Пример использования
# transactions_from_file = read_excel_transactions()
# converted_transactions = convert_date_format(transactions_from_file)
# print(converted_transactions)