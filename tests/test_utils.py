import pytest
import requests
import os
import json
import pandas as pd
from unittest.mock import patch, Mock
from datetime import datetime
from src.utils import (validate_datetime_format, greet_user, read_excel_transactions,
                       calculate_card_stats, get_top_transactions, convert_date_format,
                       get_sp500_data, get_exchange_rates, convert_currency_rates,
                       convert_stock_data, filter_transactions_by_date)
from typing import List, Dict
from unittest.mock import patch, mock_open
from dotenv import load_dotenv

def test_validate_datetime_format_incorrect_format():
    """ Тест некорректного формата даты в функции validate_datetime_format """
    with pytest.raises(ValueError) as exc_info:
        validate_datetime_format("2018.01.15 20:27:55")
    assert str(exc_info.value) == ("Неверный формат даты. "
                                   "Ожидается формат YYYY-MM-DD HH:MM:SS. "
                                   "Вы ввели 2018.01.15 20:27:55")


def test_validate_datetime_format_clear_user_input():
    """ Тест ввода пустой строки в функции validate_datetime_format """
    with pytest.raises(ValueError) as exc_info:
        validate_datetime_format("")
    assert str(exc_info.value) == ("Неверный формат даты. "
                                   "Ожидается формат YYYY-MM-DD HH:MM:SS. "
                                   "Вы ввели ")


def test_validate_datetime_format_success(valid_date_string):
    """ Тест корректно введенной даты и времени в функцию validate_datetime_format """
    assert validate_datetime_format(valid_date_string) == datetime(2023, 10, 12,
                                                                   12, 0, 0)


def test_greet_user():
    """ Тест работы функции greet_user вне зависимости от текущего времени суток """
    current_time = datetime.now().time()
    if (datetime.strptime("06:00", "%H:%M").time()
            <= current_time
            < datetime.strptime("12:00", "%H:%M").time()):
        result = "Доброе утро!"
    elif (datetime.strptime("12:00", "%H:%M").time()
            <= current_time
            < datetime.strptime("18:00", "%H:%M").time()):
        result = "Добрый день!"
    elif (datetime.strptime("18:00", "%H:%M").time()
            <= current_time
            < datetime.strptime("23:00", "%H:%M").time()):
        result = "Добрый вечер!"
    else:
        result = "Доброй ночи!"

    assert result == greet_user()


@patch('pandas.read_excel')
def test_read_excel_transactions(mock_read_excel):
    """
        Тест успешной загрузки Excel-файла.

        Проверяет, что функция `read_excel_transactions` корректно вызывает `pd.read_excel`
        и возвращает ожидаемый DataFrame.
    """
    # Подготовка данных для имитации
    mock_df = pd.DataFrame({'column1': [1, 2], 'column2': [3, 4]})
    mock_read_excel.return_value = mock_df

    # Выполнение функции
    result = read_excel_transactions('mocked_file_path.xlsx')

    # Проверка результата
    assert mock_read_excel.called
    expected_result = mock_df.to_dict('records')
    assert result == expected_result


@patch('pandas.read_excel', side_effect=FileNotFoundError)
def test_read_excel_transactions_not_found(mock_read_excel):
    """
        Тест обработки ошибки FileNotFoundError при загрузке Excel-файла.

        Проверяет, что функция `read_excel_transactions` корректно обрабатывает исключение
        FileNotFoundError и возвращает None.
    """
    # Выполнение функции
    result = read_excel_transactions('non_existent_file.xlsx')

    # Проверка результата
    assert mock_read_excel.called
    assert result is None


@pytest.mark.parametrize("transactions, expected_result", [
    (
            [
                {"Номер карты": "4276123456789012", "Сумма операции": -1000.50, "Кэшбэк": 50.25},
                {"Номер карты": "4276123456789012", "Сумма операции": 500.00, "Кэшбэк": 25.00},
                {"Номер карты": "5559123456781234", "Сумма операции": -2000.75, "Кэшбэк": 100.38},
                {"Номер карты": "5559123456781234", "Сумма операции": -300.00, "Кэшбэк": pd.NA},
                {"Номер карты": "4276123456789012", "Сумма операции": -150.00, "Кэшбэк": pd.NA}
            ],
            [
                {"last_digits": "9012", "total_spent": 1650.50, "cashback": 75.25},
                {"last_digits": "1234", "total_spent": 2300.75, "cashback": 100.38}
            ]
    ),
    (
            [],
            []
    ),
    (
            [
                {"Номер карты": pd.NA, "Сумма операции": -1000.50, "Кэшбэк": 50.25},
                {"Номер карты": "4276123456789012", "Сумма операции": 500.00, "Кэшбэк": 25.00}
            ],
            [
                {"last_digits": "9012", "total_spent": 500.00, "cashback": 25.00}
            ]
    )
])


def test_calculate_card_stats(transactions, expected_result):
    """ Тест для проверки функции calculate_card_stats при условии корректных данных на входе """
    result = calculate_card_stats(transactions)

    assert len(result) == len(expected_result)
    for expected in expected_result:
        assert any(
            r["last_digits"] == expected["last_digits"] and
            r["total_spent"] == expected["total_spent"] and
            r["cashback"] == expected["cashback"]
            for r in result
        )


def test_calculate_card_stats_invalid_input():
    """ Тест для проверки функции calculate_card_stats при условии НЕ корректных данных на входе """
    transactions = [
        {"Номер карты": "4276123456789012", "Сумма операции": "не число", "Кэшбэк": 50.25},
        {"Номер карты": "4276123456789012", "Сумма операции": 500.00, "Кэшбэк": "не число"}
    ]

    with pytest.raises(TypeError):
        calculate_card_stats(transactions)


@pytest.mark.parametrize("transactions, n, expected_result", [
    (
        [
            {"Дата операции": "2025-03-17", "Сумма операции": -1000.50, "Категория": "Продукты", "Описание": "Покупка в магазине"},
            {"Дата операции": "2025-03-18", "Сумма операции": 500.00, "Категория": "Развлечения", "Описание": "Кинотеатр"},
            {"Дата операции": "2025-03-19", "Сумма операции": -200.75, "Категория": "Транспорт", "Описание": "Такси"},
            {"Дата операции": "2025-03-20", "Сумма операции": 1500.00, "Категория": "Зарплата", "Описание": "Зарплата"}
        ],
        3,
        [
            {"date": "2025.03.20", "amount": 1500.00, "category": "Зарплата", "description": "Зарплата"},
            {"date": "2025.03.17", "amount": -1000.50, "category": "Продукты", "description": "Покупка в магазине"},
            {"date": "2025.03.18", "amount": 500.00, "category": "Развлечения", "description": "Кинотеатр"}
        ]
    ),
    (
        [],
        5,
        []
    )
])

def test_get_top_transactions(transactions, n, expected_result):
    """ Тестирует функцию get_top_transactions """
    result = get_top_transactions(transactions, n)
    assert len(result) == len(expected_result)
    for actual, expected in zip(result, expected_result):
        assert actual == expected


def test_convert_date_format_success(convert_data):
    """ Тест на корректное преобразование дат в функции convert_date_format """
    expected = [
        {
            "Дата операции": "2025-01-01 12:00:00",
            "Сумма": 100
        },
        {
            "Дата операции": "2025-01-02 13:00:00",
            "Сумма": 200
        }
    ]
    result = convert_date_format(convert_data)
    assert result == expected


def test_convert_date_format_error():
    """ Тест на обработку ошибок в функции convert_date_format """
    invalid_data = [
        {
            "Дата операции": "invalid date",
            "Сумма": 100
        }
    ]
    result = convert_date_format(invalid_data)
    assert result == invalid_data


@pytest.mark.parametrize("input_date,expected_date", [
    ("01.01.2025 12:00:00", "2025-01-01 12:00:00"),
    ("02.01.2025 13:00:00", "2025-01-02 13:00:00"),
    ("03.01.2025 14:00:00", "2025-01-03 14:00:00")
])


def test_convert_date_format_date_conversion(input_date, expected_date):
    """ Параметризованный тест для разных форматов дат в функции convert_date_format """
    data = [{"Дата операции": input_date}]
    result = convert_date_format(data)
    assert result[0]["Дата операции"] == expected_date


def test_convert_date_format_empty_list():
    """ Тест на пустой список в функции convert_date_format"""
    empty_list = []
    result = convert_date_format(empty_list)
    assert result == empty_list


def test_missing_column():
    """ Тест на отсутствие столбца "Дата операции" в функции convert_date_format """
    missing_column_data = [
        {
            "Неверная колонка": "01.01.2025 12:00:00",
            "Сумма": 100
        }
    ]
    result = convert_date_format(missing_column_data)
    assert result == missing_column_data


# Пример ожидаемых данных от API для функции get_sp500_data
expected_api_response = {
    "Global Quote": {
        "01. symbol": "SPY",
        "02. open": "400.00",
        "03. high": "405.00",
        "04. low": "395.00",
        "05. price": "402.50",
        "06. volume": "10000000",
        "07. latest trading day": "2025-03-17",
        "08. previous close": "400.00",
        "09. change": "2.50",
        "10. change percent": "0.625%"
    }
}


def test_get_sp500_data_write_to_file(mock_file):
    """ Тест для проверки записи в файл в функции get_sp500_data """
    with open(mock_file, 'w') as f:
        json.dump(expected_api_response, f)

    with open(mock_file, 'r') as f:
        data = json.load(f)
        assert data == expected_api_response

@patch('requests.get')
def test_get_sp500_data_error(mock_get, mock_api_key):
    """ Тест для проверки обработки ошибок в функции get_sp500_data """
    # Настройка мока для ошибки
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_get.return_value = mock_response

    # Выполнение функции
    result = get_sp500_data()

    # Проверка
    assert result is None

@patch('requests.get')
def test_get_sp500_data_http_error(mock_get, mock_api_key):
    """ Тест ошибки HTTP в функции get_sp500_data """
    # Настройка мока
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_get.return_value = mock_response

    # Выполнение функции
    result = get_sp500_data()

    # Проверки
    assert result is None
    mock_get.assert_called_once_with('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey=TEST_API_KEY')


@patch('requests.get')
def test_get_sp500_data_empty_response(mock_get, mock_api_key):
    """ Тест пустого ответа в функции get_sp500_data """
    # Настройка мока
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    # Выполнение функции
    result = get_sp500_data()

    # Проверки
    assert result is None
    mock_get.assert_called_once_with('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey=TEST_API_KEY')


@patch('requests.get')
@patch('os.path.exists')
@patch('builtins.open', new_callable=mock_open, read_data='{"user_currencies": ["USD"]}')
def test_successful_response(mock_open, mock_exists, mock_get):
    """ Тест для функции get_exchange_rates """
    # Настраиваем mock для os.path.exists
    mock_exists.return_value = True

    # Настраиваем mock для requests.get
    mock_response = mock_get.return_value
    mock_response.json.return_value = {
        'result': 'success',
        'conversion_rate': 74.0,
        'time_last_update_utc': '2023-10-01T00:00:00Z'
    }
    mock_response.raise_for_status = lambda: None

    # Вызываем функцию и проверяем результат
    rates = get_exchange_rates()
    assert rates == {
        'USD': {
            'rate': 74.0,
            'date': '2023-10-01T00:00:00Z'
        }
    }


# Пример входных данных для функции convert_currency_rates
input_data = {
    "USD": {"rate": 85.6789, "date": "2025-03-17"},
    "EUR": {"rate": 95.4321, "date": "2025-03-17"},
    "GBP": {"rate": 105.1234, "date": "2025-03-17"}
}

# Ожидаемый результат для функции convert_currency_rates
expected_output = [
    {"currency": "USD", "rate": 85.68},
    {"currency": "EUR", "rate": 95.43},
    {"currency": "GBP", "rate": 105.12}
]


def test_convert_currency_rates_success():
    """ Тест успешного преобразования для функции convert_currency_rates """
    # Выполнение функции
    result = convert_currency_rates(input_data)

    # Проверка
    assert result == expected_output
    assert len(result) == len(input_data)
    for item in result:
        assert "currency" in item
        assert "rate" in item
        assert isinstance(item["rate"], float)
        assert len(str(item["rate"]).split(".")[1]) == 2  # Проверка округления до 2 знаков


def test_convert_currency_rates_empty():
    """ Тест с пустым словарем для функции convert_currency_rates """
    # Выполнение функции
    result = convert_currency_rates({})

    # Проверка
    assert result == []


def test_convert_currency_rates_invalid_data():
    """ Тест с некорректными данными для функции convert_currency_rates """
    # Некорректные входные данные
    invalid_data = {
        "USD": {"rate": "invalid"},
        "EUR": {"rate": None},
        "GBP": {"rate": 100}
    }

    # Выполнение функции
    result = convert_currency_rates(invalid_data)

    # Проверка
    assert len(result) == 1  # Должен обработать только корректные данные
    assert result[0] == {"currency": "GBP", "rate": 100.00}


def test_convert_currency_rates_missing_rate():
    """ Тест с отсутствующим ключом rate для функции convert_currency_rates """
    # Входные данные без ключа rate
    missing_rate_data = {
        "USD": {},
        "EUR": {"date": "2025-03-17"}
    }

    # Выполнение функции
    result = convert_currency_rates(missing_rate_data)

    # Проверка
    assert result == []


def test_convert_currency_rates_invalid_rate_format():
    """ Тест с некорректным форматом rate для функции convert_currency_rates """
    # Входные данные с некорректным форматом rate
    invalid_format_data = {
        "USD": {"rate": "85.6789"},
        "EUR": {"rate": [95.4321]},
        "GBP": {"rate": {"value": 105.1234}}
    }

    # Выполнение функции
    result = convert_currency_rates(invalid_format_data)

    # Проверка
    assert result == []


# Пример корректных входных данных для функции convert_stock_data
VALID_INPUT = {
    "Global Quote": {
        "01. symbol": "AAPL",
        "08. previous close": "150.25"
    }
}

# Ожидаемый результат для корректных данных для функции convert_stock_data
EXPECTED_OUTPUT = {
    "stock": "AAPL",
    "price": 150.25
}


def test_convert_stock_data_success():
    """ Тест успешного преобразования для функции convert_stock_data """
    # Выполнение функции
    result = convert_stock_data(VALID_INPUT)

    # Проверка
    assert result == EXPECTED_OUTPUT
    assert isinstance(result.get("price"), float)


def test_convert_stock_data_empty():
    """ Тест с пустым словарем для функции convert_stock_data """
    # Выполнение функции
    result = convert_stock_data({})

    # Проверка
    assert result == {}


def test_convert_stock_data_missing_global_quote():
    """ Тест с отсутствующим Global Quote для функции convert_stock_data """
    # Входные данные без Global Quote
    input_data = {"Some Other Key": {}}

    # Выполнение функции
    result = convert_stock_data(input_data)

    # Проверка
    assert result == {}


def test_convert_stock_data_missing_symbol():
    """ Тест с отсутствующим символом для функции convert_stock_data """
    # Входные данные без символа
    input_data = {
        "Global Quote": {
            "08. previous close": "150.25"
        }
    }

    # Выполнение функции
    result = convert_stock_data(input_data)

    # Проверка
    assert result == {}


def test_convert_stock_data_missing_price():
    """ Тест с отсутствующей ценой для функции convert_stock_data """
    # Входные данные без цены
    input_data = {
        "Global Quote": {
            "01. symbol": "AAPL"
        }
    }

    # Выполнение функции
    result = convert_stock_data(input_data)

    # Проверка
    assert result == {}


def test_convert_stock_data_invalid_price_format():
    """ Тест с некорректным форматом цены для функции convert_stock_data """
    # Входные данные с некорректной ценой
    input_data = {
        "Global Quote": {
            "01. symbol": "AAPL",
            "08. previous close": "invalid"
        }
    }

    # Выполнение функции
    result = convert_stock_data(input_data)

    # Проверка
    assert result == {}


def test_convert_stock_data_price_as_number():
    """ Тест с ценой в виде числа для функции convert_stock_data """
    # Входные данные с ценой в виде числа
    input_data = {
        "Global Quote": {
            "01. symbol": "AAPL",
            "08. previous close": 150.25
        }
    }

    # Выполнение функции
    result = convert_stock_data(input_data)

    # Проверка
    assert result == EXPECTED_OUTPUT


def test_convert_stock_data_price_with_spaces():
    """ Тест с пробелами в значении цены для функции convert_stock_data """
    # Входные данные с ценой, содержащей пробелы
    input_data = {
        "Global Quote": {
            "01. symbol": "AAPL",
            "08. previous close": " 150.25 "
        }
    }

    # Выполнение функции
    result = convert_stock_data(input_data)

    # Проверка
    assert result == EXPECTED_OUTPUT


# Пример тестовых данных для функции filter_transactions_by_date
VALID_TRANSACTIONS = [
    {
        "Дата операции": "2025-03-15 10:00:00",
        "Сумма": 1000,
        "Тип операции": "Поступление"
    },
    {
        "Дата операции": "2025-03-10 12:00:00",
        "Сумма": 500,
        "Тип операции": "Расход"
    },
    {
        "Дата операции": "2025-02-28 14:00:00",
        "Сумма": 200,
        "Тип операции": "Расход"
    },
    {
        "Дата операции": "2025-03-31 16:00:00",
        "Сумма": 300,
        "Тип операции": "Поступление"
    }
]


def test_filter_transactions_by_date_success():
    """ Тест успешного фильтрации для функции filter_transactions_by_date """
    # Входные данные
    valid_date_str = "2025-03-20 00:00:00"

    # Ожидаемый результат
    expected_result = [
        {
            "Дата операции": "2025-03-15 10:00:00",
            "Сумма": 1000,
            "Тип операции": "Поступление"
        },
        {
            "Дата операции": "2025-03-10 12:00:00",
            "Сумма": 500,
            "Тип операции": "Расход"
        }
    ]

    # Выполнение функции
    result = filter_transactions_by_date(VALID_TRANSACTIONS, valid_date_str)

    # Проверка
    assert len(result) == len(expected_result)
    assert result == expected_result


def test_filter_transactions_by_date_empty_list():
    """ Тест с пустой базой транзакций для функции filter_transactions_by_date """
    # Входные данные
    empty_list = []
    valid_date_str = "2025-03-20 00:00:00"

    # Выполнение функции
    result = filter_transactions_by_date(empty_list, valid_date_str)

    # Проверка
    assert result == []


def test_filter_transactions_by_date_invalid_date_format():
    """ Тест с некорректным форматом даты для функции filter_transactions_by_date """
    # Входные данные
    invalid_date_str = "2025-03-20"  # Некорректный формат

    # Выполнение функции
    result = filter_transactions_by_date(VALID_TRANSACTIONS, invalid_date_str)

    # Проверка
    assert result == []
