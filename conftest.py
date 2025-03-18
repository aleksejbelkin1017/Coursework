import pytest


@pytest.fixture
def valid_date_string():
    """ Фикстура корректного формата даты """
    return "2023-10-12 12:00:00"


@pytest.fixture
def convert_data():
    """ Фикстура для создания тестовых данных """
    return [
        {
            "Дата операции": "01.01.2025 12:00:00",
            "Сумма": 100
        },
        {
            "Дата операции": "02.01.2025 13:00:00",
            "Сумма": 200
        }
    ]


@pytest.fixture
def mock_api_key(monkeypatch):
    """ Фикстура для мокинга API ключа """
    monkeypatch.setenv('API_KEY_alphavantage', 'TEST_API_KEY')


@pytest.fixture
def mock_file(tmp_path):
    """ Фикстура для создания временного файла """
    # Создаем директорию data
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Создаем файл sp500_data.json
    file_path = data_dir / "sp500_data.json"
    file_path.write_text("{}")  # Пишем пустой JSON в файл

    # Возвращаем путь к файлу
    yield str(file_path)


# Тестовые данные для фикстуры mock_transactions
test_transactions = [
    {
        "Дата операции": "01.01.2018 12:49:53",
        "Категория": "Переводы",
        "Описание": "Линзомат ТЦ Юность"
    },
    {
        "Дата операции": "02.01.2018 12:49:53",
        "Категория": "Магазины",
        "Описание": "ТЦ Юность"
    },
    {
        "Дата операции": "03.01.2018 12:49:53",
        "Категория": "Еда",
        "Описание": "Продуктовый магазин"
    }
]
@pytest.fixture
def mock_transactions():
    return test_transactions

