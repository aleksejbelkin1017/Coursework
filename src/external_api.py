import os
import requests
import json


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

    Структура сохраняемых данных:
    {
        "Meta Data": {
            "1. Information": "Daily Prices and Volumes Information",
            ...
        },
        "Time Series (Daily)": {
            "2023-03-14": {
                "1. open": "415.25",
                "2. high": "417.98",
                "3. low": "413.25",
                "4. close": "417.50",
                "5. volume": "10000000"
            },
            ...
        }
    }

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

        Пример возвращаемого словаря:
        {
            "USD": {
                "rate": 75.68,
                "date": "2023-03-14T12:00:00Z"
            },
            "EUR": {
                "rate": 82.45,
                "date": "2023-03-14T12:00:00Z"
            }
        }

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
            "rate": round(data["rate"], 2)
        }
        for currency, data in rates_dict.items()
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

    if stock_symbol and previous_close:
        return {
            "stock": stock_symbol,
            "price": float(previous_close)
        }

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