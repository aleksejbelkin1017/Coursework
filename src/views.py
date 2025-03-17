from typing import Dict
from utils import (validate_datetime_format, greet_user, read_excel_transactions,
                   convert_date_format, calculate_card_stats, get_top_transactions,
                   filter_transactions_by_date, get_exchange_rates, convert_currency_rates,
                   get_sp500_data, convert_stock_data)

import json


def answer_about_transactions(last_date: str) -> Dict:
    """
    Функция принимает на вход строку с датой и временем
    в формате YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ

    Параметры:
    last_date (str): строка с датой и временем

    Возвращает:
    dict: словарь с ответом
    """
    try:
        # Проверяем формат даты, введенной пользователем на соответствие '%d.%m.%Y %H:%M:%S'
        validate_datetime = validate_datetime_format(last_date)
        # Если формат даты не соответствует '%d.%m.%Y %H:%M:%S', выводится сообщение об ошибке
        if not validate_datetime:
            raise ValueError('Неверный формат даты.')
        # Если формат даты соответствует '%d.%m.%Y %H:%M:%S', функция продолжает исполнение
        else:
            # Обрабатываем Excel файл с исходными данными, получаем список словарей
            operations = read_excel_transactions()
            # Приводим формат даты для ключа 'Дата операции' к формату '%d.%m.%Y %H:%M:%S'
            converted_date_operations = convert_date_format(operations)
            # Фильтрует транзакции за указанный месяц, где дата операции меньше или равна last_date
            filtered_transactions = filter_transactions_by_date(converted_date_operations, last_date)
            # Формируем вывод информации о транзакциях
            responce = {
                "greeting":
                    greet_user(), # Приветствие пользователя в зависимости от времени суток
                "cards":
                    calculate_card_stats(filtered_transactions), # Статистика по картам
                "top_transactions": get_top_transactions(filtered_transactions),
                "currency_rates": convert_currency_rates(get_exchange_rates()),
                "stock_prices": convert_stock_data(get_sp500_data())
            }

            result = json.dumps(responce, ensure_ascii=False, indent=2)

            return result

    except ValueError:
        print('Ошибка: Неверный формат даты.')

# Примеры использования:
print(answer_about_transactions("2018-01-15 20:27:55"))  # Валидный формат
# print(answer_about_transactions("2018.01.02 20:27:55"))  # Невалидный формат
# if __name__ == '__main__':
#     answer_about_transactions()
