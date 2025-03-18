import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import requests

logger = logging.getLogger('utils.py')
file_handler = logging.FileHandler('utils.log', encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s:\n%(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def validate_datetime_format(date_string: str) -> Optional[datetime]:
    """
    Проверяет строку на соответствие формату даты и времени YYYY-MM-DD HH:MM:SS

    Параметры:
    date_string (str): строка с датой и временем

    Возвращает:
    datetime: объект datetime, если формат верный
    None: если формат неверный
    """
    logger.info('Запущена функция "validate_datetime_format".')
    try:
        # Проверяем формат YYYY-MM-DD HH:MM:SS
        logger.info('Выполнение функции "validate_datetime_format" успешно завершено.')
        return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        logger.error(f'Неверный формат даты. Ожидается формат "YYYY-MM-DD HH:MM:SS". Вы ввели {date_string}.')
        raise ValueError('Неверный формат даты. '
                         'Ожидается формат "YYYY-MM-DD HH:MM:SS". '
                         f'Вы ввели {date_string}')


def greet_user() -> str:
    """ Функция выводит строку приветствия в зависимости от времени суток """
    logger.info('Запущена функция "greet_user".')
    # Получаем текущее время
    current_time = datetime.now().time()
    logger.info(f'Получено текущее время: {current_time}')

    # Определяем временные интервалы
    logger.info('Определяем временные интервалы.')
    morning_start = datetime.strptime("06:00", "%H:%M").time()
    afternoon_start = datetime.strptime("12:00", "%H:%M").time()
    evening_start = datetime.strptime("18:00", "%H:%M").time()
    night_start = datetime.strptime("23:00", "%H:%M").time()

    # Определяем приветствие в зависимости от времени
    if morning_start <= current_time < afternoon_start:
        logger.info('Определено приветствие: Доброе утро!')
        logger.info('Выполнение функции "greet_user" успешно завершено.')
        return "Доброе утро!"
    elif afternoon_start <= current_time < evening_start:
        logger.info('Определено приветствие: Добрый день!')
        logger.info('Выполнение функции "greet_user" успешно завершено.')
        return "Добрый день!"
    elif evening_start <= current_time < night_start:
        logger.info('Определено приветствие: Добрый вечер!')
        logger.info('Выполнение функции "greet_user" успешно завершено.')
        return "Добрый вечер!"
    else:
        logger.info('Определено приветствие: Доброй ночи!')
        logger.info('Выполнение функции "greet_user" успешно завершено.')
        return "Доброй ночи!"


def read_excel_transactions(file_path: str = 'data/operations.xlsx') -> Optional[list[dict]]:
    """ Функция считывает финансовые операции из excel-файла """
    logger.info('Запущена функция "read_excel_transactions".')
    try:
        df = pd.read_excel(file_path)
        logger.info('EXCEL-файл с транзакциями прочитан.')
        logger.info('Выполнение функции "read_excel_transactions" успешно завершено.')
        return df.to_dict('records')
    except FileNotFoundError:
        logger.warning(f'Файл по пути "{file_path}" не найден')
        print(f'Файл по пути "{file_path}" не найден')
        return None


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
    logger.info('Запущена функция "calculate_card_stats".')
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

    logger.info('Выполнение функции "calculate_card_stats" успешно завершено.')
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
    logger.info('Запущена функция "get_top_transactions".')
    # Сортируем по абсолютной величине суммы операции
    sorted_transactions = sorted(
        transactions,
        key=lambda x: abs(x['Сумма операции']),
        reverse=True
    )

    logger.info('Выполнение функции "get_top_transactions" успешно завершено.')
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
    logger.info('Запущена функция "convert_date_format".')
    try:
        logger.info('Создан DataFrame из списка словарей.')
        # Создаем DataFrame из списка словарей
        df = pd.DataFrame(transactions)

        logger.info('Преобразован столбец "Дата операции" в datetime.')
        # Преобразуем столбец 'Дата операции' в datetime
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S')

        logger.info('Даты приведены к формату "%Y-%m-%d %H:%M:%S"')
        # Форматируем даты в нужный формат
        df['Дата операции'] = df['Дата операции'].dt.strftime('%Y-%m-%d %H:%M:%S')

        logger.info('Список словарей сформирован.')
        logger.info('Выполнение функции "convert_date_format" успешно завершено.')
        # Возвращаем список словарей с обновленными датами
        return df.to_dict('records')
    except Exception as e:
        logger.error(f'Ошибка при преобразовании дат: {e}')
        print(f"Ошибка при преобразовании дат: {e}")
        return transactions  # Возвращаем исходные данные при ошибке


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
    logger.info('Запущена функция "get_sp500_data".')
    try:
        api_key = os.getenv('API_KEY_alphavantage')
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}'

        logger.info('Сформирован и направлен API-запрос.')
        response = requests.get(url)

        if response.status_code != 200:
            logger.error(f'Ошибка HTTP: {response.text}')
            print("Ошибка HTTP:", response.text)
            return

        data = response.json()

        if not data:
            logger.error('Получен пустой ответ.')
            print("Получен пустой ответ")
            return

        # Записываем данные в файл
        with open('data/sp500_data.json', 'w') as json_file:
            json.dump(data, json_file, indent=2)
            logger.info('Данные успешно сохранены в файл "data/sp500_data.json".')

        # print("Данные успешно сохранены в файл sp500_data.json")
        logger.info('Выполнение функции "get_sp500_data" успешно завершено.')
        return data

    except requests.RequestException as e:
        logger.error(f'Ошибка при запросе: {e}')
        print(f"Ошибка при запросе: {e}")
    except ValueError as e:
        logger.error(f'Ошибка при парсинге JSON: {e}')
        print(f"Ошибка при парсинге JSON: {e}")
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')
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
    logger.info('Запущена функция "get_exchange_rates".')
    api_key = os.getenv('API_KEY_exchangerate')
    # Проверяем существование файла настроек
    logger.info('Проверка существования файла настроек.')
    if not os.path.exists('user_settings.json'):
        logger.warning('Файл настроек не найден.')
        print("Файл настроек не найден")
        return {}

    # Читаем настройки пользователя
    logger.info('Выполняется чтение файла настроек.')
    with open('user_settings.json', 'r') as file:
        user_settings = json.load(file)

    # Получаем список интересующих валют
    logger.info('Формируется список интересующих валют.')
    currencies = user_settings.get('user_currencies', [])

    # Словарь для хранения результатов
    logger.info('Подготовлен пустой словарь для хранения результатов.')
    rates = {}

    # Для каждой валюты делаем запрос
    logger.info('Запускаем цикл запросов по валютам из списка.')
    for currency in currencies:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{currency}/RUB/1"

        try:
            response = requests.get(url)
            logger.info('Сформирован и направлен API-запрос по валюте из списка.')
            response.raise_for_status()  # Проверяем успешность запроса

            data = response.json()
            if data.get('result') == 'success':
                logger.info('Получен положительный ответ.')
                rates[currency] = {
                    'rate': data['conversion_rate'],
                    'date': data['time_last_update_utc']
                }
            else:
                logger.error(f'Ошибка получения курса для {currency}: {data['error_type']}')
                print(f"Ошибка получения курса для {currency}: {data['error_type']}")

        except requests.RequestException as e:
            print(f"Ошибка при запросе курса для {currency}: {e}")

    # Создаем директорию для сохранения, если её нет
    logger.info('Проверяем наличие директории "data" и создаём её при необходимости.')
    if not os.path.exists('data'):
        os.makedirs('data')

    # Сохраняем результаты в файл
    with open('data/exchange_rates.json', 'w') as file:
        json.dump(rates, file, indent=2)

    logger.info('Данные успешно сохранены в файл "data/exchange_rates.json".')
    logger.info('Выполнение функции "get_exchange_rates" успешно завершено.')
    return rates


def convert_currency_rates(rates_dict: dict) -> list:
    """
    Преобразует словарь курсов валют в список словарей

    Параметры:
    rates_dict (dict): словарь с курсами валют

    Возвращает:
    list: список словарей с полями "currency" и "rate"
    """
    logger.info('Запущена функция "convert_currency_rates".')
    logger.info('Выполнение функции "convert_currency_rates" успешно завершено.')
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
    logger.info('Запущена функция "convert_stock_data".')
    global_quote = stock_info.get("Global Quote", {})

    stock_symbol = global_quote.get("01. symbol")
    previous_close = global_quote.get("08. previous close")

    try:
        if stock_symbol and previous_close:
            logger.info('Выполнение функции "convert_stock_data" успешно завершено.')
            return {
                "stock": stock_symbol,
                "price": float(previous_close)
            }
    except (ValueError, TypeError):
        logger.error('Выполнение функции "convert_stock_data" завершено с ошибкой.')
        return {}

    return {}


def filter_transactions_by_date(transactions: list, valid_date_str: str) -> list:
    """
    Фильтрует транзакции за указанный месяц, где дата операции меньше или равна valid_date

    Параметры:
    transactions (list): список словарей с операциями
    valid_date_str (str): строка с датой в формате YYYY-MM-DD HH:MM:SS

    Возвращает:
    list: отфильтрованный список словарей
    """
    logger.info('Запущена функция "filter_transactions_by_date".')
    try:
        logger.info('Преобразуем строку "valid_date_str" с датой в объект datetime.')
        valid_date = datetime.strptime(valid_date_str, '%Y-%m-%d %H:%M:%S')

        filtered_transactions = [
            transaction
            for transaction in transactions
            if (datetime.strptime(transaction['Дата операции'], '%Y-%m-%d %H:%M:%S')
                <= valid_date and
                datetime.strptime(transaction['Дата операции'], '%Y-%m-%d %H:%M:%S').month
                == valid_date.month and
                datetime.strptime(transaction['Дата операции'], '%Y-%m-%d %H:%M:%S').year
                == valid_date.year)
        ]
        logger.info('Создан новый список "filtered_transactions", '
                    '\nкоторый содержит только те транзакции, '
                    '\nкоторые удовлетворяют заданным условиям.')
        logger.error('Выполнение функции "filter_transactions_by_date" успешно завершено.')
        return filtered_transactions
    except ValueError as e:
        logger.error(f'Ошибка при обработке даты: {e}')
        print(f"Ошибка при обработке даты: {e}")
        return []
