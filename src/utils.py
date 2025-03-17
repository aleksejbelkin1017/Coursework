from datetime import datetime
from typing import Dict, List, Optional

import os
import requests
import json
import pandas as pd


def validate_datetime_format(date_string: str) -> Optional[datetime]:
    """
    Проверяет строку на соответствие формату даты и времени YYYY-MM-DD HH:MM:SS

    Параметры:
    date_string (str): строка с датой и временем

    Возвращает:
    datetime: объект datetime, если формат верный
    None: если формат неверный
    """
    try:
        # Проверяем формат YYYY-MM-DD HH:MM:SS
        return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError('Неверный формат даты. '
                         'Ожидается формат YYYY-MM-DD HH:MM:SS. '
                         f'Вы ввели {date_string}')


def greet_user() -> str:
    """ Функция выводит строку приветствия в зависимости от времени суток """
    # Получаем текущее время
    current_time = datetime.now().time()

    # Определяем временные интервалы
    morning_start = datetime.strptime("06:00", "%H:%M").time()
    afternoon_start = datetime.strptime("12:00", "%H:%M").time()
    evening_start = datetime.strptime("18:00", "%H:%M").time()
    night_start = datetime.strptime("23:00", "%H:%M").time()

    # Определяем приветствие в зависимости от времени
    if morning_start <= current_time < afternoon_start:
        return "Доброе утро!"
    elif afternoon_start <= current_time < evening_start:
        return "Добрый день!"
    elif evening_start <= current_time < night_start:
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"


# Пример использования:
# print(date_and_time_now())
# Вывод будет выглядеть примерно так: "2025-03-13 17:30:50"
# Пример использования
# print(greet_user())


def read_excel_transactions(file_path: str='data/operations.xlsx') -> Optional[list[dict]]:
    """ Функция считывает финансовые операции из excel-файла """
    try:
        df = pd.read_excel(file_path)
        return df.to_dict('records')
    except FileNotFoundError:
        print(f'Файл по пути "{file_path}" не найден')
        return None


# if __name__ == "__main__":
#     transactions = read_excel_transactions()
#     if transactions:
#         print(transactions)


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


def get_sp500_data() -> dict:
    """
    Получает актуальные данные об индексе S&P 500 через API сервиса Alpha Vantage
    и сохраняет их в JSON файл.

    Описание:
    Функция делает HTTP-запрос к API Alpha Vantage для получения ежедневных
    данных по тикеру SPY (ETF, отслеживающий S&P 500). Полученные данные
    сохраняются в файл 'data/sp500_data.json'.

    Требования:
    - Необходимо установить переменную окружения API_KEY_alphavantage
    - Требуется установленный модуль requests

    Параметры:
    Нет

    Возвращаемое значение:
    None

    Побочные эффекты:
    - Создает директорию 'data' если она не существует
    - Записывает данные в файл 'data/sp500_data.json'
    - Выводит сообщения об успехе/ошибке в консоль

    Обрабатываемые ошибки:
    - requests.RequestException: ошибки сетевого соединения
    - ValueError: ошибки при парсинге JSON
    - Общие исключения

    Примечания:
    - Частота обновления данных: ежедневно
    - Для использования необходимо получить API ключ на сайте Alpha Vantage
    - Данные включают информацию об открытии, максимуме, минимуме, закрытии
      и объеме торгов за каждый день
    """
    try:
        api_key = os.getenv('API_KEY_alphavantage')
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}'

        response = requests.get(url)

        if response.status_code != 200:
            print("Ошибка HTTP:", response.text)
            return

        data = response.json()

        if not data:
            print("Получен пустой ответ")
            return

        # Записываем данные в файл
        with open('data/sp500_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=2)

        # print("Данные успешно сохранены в файл sp500_data.json")
        return data

    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
    except ValueError as e:
        print(f"Ошибка при парсинге JSON: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def get_exchange_rates() -> dict:
    """
        Получает курсы валют для указанных в настройках валют относительно RUB
        и сохраняет результаты в файл.

        Параметры:
        Нет

        Возвращает:
        dict: Словарь с курсами валют, где ключ - код валюты,
              а значение - словарь с полями 'rate' (курс) и 'date' (дата обновления)

        Побочные эффекты:
        - Создает директорию 'data' если она не существует
        - Сохраняет результаты в файл 'data/exchange_rates.json'
        - Читает настройки из файла 'user_settings.json'

        Обрабатываемые ошибки:
        - Отсутствие файла настроек
        - Проблемы с сетевым подключением
        - Ошибки API
        - Неудачные запросы
        """
    api_key = os.getenv('API_KEY_exchangerate')
    # Проверяем существование файла настроек
    if not os.path.exists('user_settings.json'):
        print("Файл настроек не найден")
        return {}

    # Читаем настройки пользователя
    with open('user_settings.json', 'r') as file:
        user_settings = json.load(file)

    # Получаем список интересующих валют
    currencies = user_settings.get('user_currencies', [])

    # Словарь для хранения результатов
    rates = {}

    # Для каждой валюты делаем запрос
    for currency in currencies:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{currency}/RUB/1"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверяем успешность запроса

            data = response.json()
            if data.get('result') == 'success':
                rates[currency] = {
                    'rate': data['conversion_rate'],
                    'date': data['time_last_update_utc']
                }
            else:
                print(f"Ошибка получения курса для {currency}: {data['error_type']}")

        except requests.RequestException as e:
            print(f"Ошибка при запросе курса для {currency}: {e}")

    # Создаем директорию для сохранения, если её нет
    if not os.path.exists('data'):
        os.makedirs('data')

    # Сохраняем результаты в файл
    with open('data/exchange_rates.json', 'w') as file:
        json.dump(rates, file, indent=2)

    # print("Данные успешно сохранены в файл exchange_rates.json")
    return rates


def convert_currency_rates(rates_dict: dict) -> list:
    """
    Преобразует словарь курсов валют в список словарей

    Параметры:
    rates_dict (dict): словарь с курсами валют

    Возвращает:
    list: список словарей с полями "currency" и "rate"
    """
    return [
        {
            "currency": currency,
            "rate": round(data.get("rate", 0), 2) if isinstance(data.get("rate"), (float, int)) else None
        }
        for currency, data in rates_dict.items()
        if isinstance(data.get("rate"), (float, int))
    ]


def convert_stock_data(stock_info: dict) -> dict:
    """
    Преобразует информацию о цене акции в требуемый формат

    Параметры:
    stock_info (dict): словарь с информацией об акции

    Возвращает:
    dict: словарь с полями "stock" и "price"
    """
    global_quote = stock_info.get("Global Quote", {})

    stock_symbol = global_quote.get("01. symbol")
    previous_close = global_quote.get("08. previous close")

    try:
        if stock_symbol and previous_close:
            return {
                "stock": stock_symbol,
                "price": float(previous_close)
            }
    except (ValueError, TypeError):
        return {}

    return {}


# Пример использования
# input_data = {
#     "Global Quote": {
#         "01. symbol": "SPY",
#         "02. open": "558.4900",
#         "03. high": "559.1050",
#         "04. low": "549.6800",
#         "05. price": "551.4200",
#         "06. volume": "74079414",
#         "07. latest trading day": "2025-03-13",
#         "08. previous close": "558.8700",
#         "09. change": "-7.4500",
#         "10. change percent": "-1.3330%"
#     }
# }
#
# result = convert_stock_data(input_data)
# print(json.dumps(result, ensure_ascii=False, indent=2))


# if __name__ == "__main__":
    # get_sp500_data()
    # convert_stock_data(get_sp500_data())
    # get_exchange_rates()
    # convert_currency_rates(x)


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
