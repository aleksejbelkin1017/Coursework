from typing import Optional

import os
import pandas as pd
import requests
import json


def read_excel_transactions(file_path: str) -> Optional[list[dict]]:
    """ Функция считывает финансовые операции из excel-файла """
    try:
        df = pd.read_excel(file_path)
        return df.to_dict('records')
    except FileNotFoundError:
        print(f'Файл по пути "{file_path}" не найден')
        return None


def get_sp500_data():
    """ Функция получает данные об S&P 500 через API сервис Alpha Vantage """
    try:
        api_key = os.getenv('API_KEY_alphavantage')
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=SPY&apikey={api_key}'

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

        print("Данные успешно сохранены в файл sp500_data.json")

    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
    except ValueError as e:
        print(f"Ошибка при парсинге JSON: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


# if __name__ == "__main__":
#    get_sp500_data()
#    file = 'data/operations.xlsx'
#    print(read_excel_transactions(file))
