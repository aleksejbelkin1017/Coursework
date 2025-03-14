from datetime import datetime
from typing import Dict, List
import pandas as pd
from file_reader import read_excel_transactions


def calculate_card_stats(transactions: List[Dict]) -> List[Dict]:
    """
    Рассчитывает статистику по картам на основе списка транзакций

    Параметры:
    transactions (List[Dict]): список словарей с транзакциями, где каждая транзакция содержит:
    - 'Номер карты': номер карты (строка с символом маскировки, например, '*1234')
    - 'Сумма операции': сумма операции (число с плавающей точкой)
    - 'Кэшбэк': кэшбэк за операцию (число с плавающей точкой или NaN, если отсутствует)

    Возвращает:
    List[Dict]: список словарей со статистикой по каждой карте, где каждый элемент содержит:
    - "last_digits": последние 4 цифры номера карты (строка)
    - "total_spent": общая сумма потраченных средств (число с плавающей точкой, округленное до 2 знаков)
    - "cashback": общая сумма полученного кэшбэка (число с плавающей точкой, округленное до 2 знаков)

    Примечания:
    - Игнорируются транзакции с отсутствующим номером карты
    - Если кэшбэк отсутствует (NaN), он не учитывается в общей сумме
    - Суммы округляются до 2 знаков после запятой
    """
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
    """
    Возвращает список самых крупных транзакций по абсолютной величине суммы

    Параметры:
    transactions (List[Dict]): список словарей с транзакциями, где каждая транзакция содержит:
        - 'Дата операции': дата и время операции (строка в формате 'YYYY-MM-DD HH:MM:SS')
        - 'Сумма операции': сумма операции (число с плавающей точкой)
        - 'Категория': категория транзакции (строка)
        - 'Описание': описание транзакции (строка)
    n (int, optional): количество возвращаемых транзакций. По умолчанию 5.

    Возвращает:
    List[Dict]: список словарей с информацией о топ транзакциях, где каждый элемент содержит:
        - "date": дата операции (строка в формате 'DD.MM.YYYY')
        - "amount": сумма операции (число с плавающей точкой, округленное до 2 знаков)
        - "category": категория транзакции (строка)
        - "description": описание транзакции (строка)

    Примечания:
    - Транзакции сортируются по абсолютной величине суммы операции
    - Дата преобразуется из формата 'YYYY.MM.DD HH:MM:SS' в 'YYYY-MM-DD HH:MM:SS'
    - Сумма округляется до 2 знаков после запятой
    - Если транзакций меньше чем n, возвращаются все доступные
    """
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