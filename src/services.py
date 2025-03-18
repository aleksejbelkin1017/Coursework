import logging
import os
import json
from src.utils import read_excel_transactions
from typing import Optional

logger = logging.getLogger('services.py')
file_name = os.path.join(os.getcwd(), 'logs', 'services.log')
file_handler = logging.FileHandler(file_name, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s:\n%(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def search_transactions(search_word: str, path_to_file: str = 'data/operations.xlsx') -> Optional[list[dict]]:
    """
    Функция поиска транзакций по заданному слову

    :param search_word: искомое слово
    :param path_to_file: путь к файлу с транзакциями
    :return: JSON с результатами поиска или сообщение об отсутствии результатов
    """
    logger.info(f'Запущена функция "search_transactions".')
    logger.debug(f'Приводим слово "{search_word}" к нижнему регистру для нечувствительного поиска.')
    search_word = search_word.lower()

    logger.debug(f'Получаем список транзакций "transactions" из файла "{path_to_file}".')
    transactions = read_excel_transactions(path_to_file)

    logger.debug('Создаем список для хранения результатов поиска.')
    result = []

    if not isinstance(transactions, list) or not all(isinstance(t, dict) for t in transactions):
        logger.error('Ошибка: Ожидался список словарей. "transactions" не является списком словарей.')
        raise ValueError("Ожидался список словарей")

    logger.info('Запускаем цикл. Проходим по всем транзакциям в "transactions".')
    try:
        for transaction in transactions:
            # print(f"Обрабатываемый элемент: {transaction}")  # Добавь эту строку для отладки
            if not isinstance(transaction, dict):
                logger.error('Ошибка: "transaction" не является словарем. '
                             'Ожидался словарь, но получено что-то другое.')
                raise ValueError('Ожидался словарь, но получено что-то другое')

            logger.debug('Получаем значения для ключей "Категория" и "Описание". \n'
                         'Приводим значения '
                         f'"{transaction.get("Категория", "")}" и '
                         f'"{transaction.get("Описание", "")}" для ключей "Категория" и "Описание" к нижнему регистру.')

            category_value = transaction.get("Категория", "")

            if isinstance(category_value, str):
                category = category_value.lower()
            else:
                category = ""

            description = transaction.get("Описание", "").lower()

            logger.debug(f'Проверяем наличие искомого слова "{search_word}" '
                         f'в списке словарей под ключами "Категория" и "Описание".')

            if search_word in category or search_word in description:
                logger.debug(f'Добавляем значение "{transaction}" в переменную "result"')
                result.append(transaction)

        logger.info('Если результаты найдены, возвращаем их в формате JSON.')

        if result:
            logger.info('Выполнение функции "search_transactions" успешно завершено.')
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            logger.error(f'Ошибка: Транзакций по слову "{search_word}" не найдено!')
            print(f'Транзакций по слову "{search_word}" не найдено!')

    except FileNotFoundError:
        logger.warning(f'Ошибка: Файл по пути "{path_to_file}" не найден!')
        print(f'Файл по пути "{path_to_file}" не найден!')
        return None

# Для вывода результатов на печать раскомментировать код ниже
# search_word = input("Введите слово для поиска: ")
# print(search_transactions(search_word))
