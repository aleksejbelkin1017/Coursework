import json
from typing import Dict

from src.utils import (calculate_card_stats, convert_currency_rates, convert_date_format, convert_stock_data,
                       filter_transactions_by_date, get_exchange_rates, get_sp500_data, get_top_transactions, greet_user,
                       read_excel_transactions, validate_datetime_format)


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
                    # Приветствие пользователя в зависимости от времени суток
                    greet_user(),
                "cards":
                    # Статистика по картам
                    calculate_card_stats(filtered_transactions),
                "top_transactions":
                    # Возвращает список самых крупных транзакций по абсолютной величине суммы
                    get_top_transactions(filtered_transactions),
                "currency_rates":
                    # Преобразует словарь курсов валют в список словарей
                    # Получает курсы валют для указанных в настройках валют относительно RUB
                    convert_currency_rates(get_exchange_rates()),
                "stock_prices":
                    # Получает актуальные данные об индексе S&P 500 через API сервиса Alpha Vantage
                    # Преобразует информацию о цене акции в требуемый формат
                    convert_stock_data(get_sp500_data())
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
