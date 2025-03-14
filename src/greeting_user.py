from datetime import datetime
from typing import Optional, Dict


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
        message = ('Неверный формат даты. Ожидается формат YYYY-MM-DD HH:MM:SS. '
                   f'Вы ввели {date_string}')
        return message


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