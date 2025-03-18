import pytest
import json
from src.services import search_transactions


def test_search_success(monkeypatch, mock_transactions):
    """
    Тестируем успешный поиск
    """
    monkeypatch.setattr('src.services.read_excel_transactions', lambda x: mock_transactions)
    result = search_transactions("юность")
    expected = json.dumps([mock_transactions[0], mock_transactions[1]], ensure_ascii=False, indent=2)
    assert result == expected


def test_search_not_found(monkeypatch, mock_transactions):
    """
    Тестируем поиск без результатов
    """
    monkeypatch.setattr('src.services.read_excel_transactions', lambda x: mock_transactions)
    result = search_transactions("несуществующее")
    assert result is None


def test_invalid_data(monkeypatch):
    """
    Тестируем неверный формат данных
    """
    monkeypatch.setattr('src.services.read_excel_transactions', lambda x: [1, 2, 3])
    with pytest.raises(ValueError):
        search_transactions("тест")


def test_empty_search_word(monkeypatch, mock_transactions):
    """
    Тестируем пустой поисковый запрос
    """
    monkeypatch.setattr('src.services.read_excel_transactions', lambda x: mock_transactions)
    result = search_transactions("")
    assert result == json.dumps(mock_transactions, ensure_ascii=False, indent=2)


def test_case_insensitive_search(monkeypatch, mock_transactions):
    """
    Тестируем нечувствительность к регистру
    """
    monkeypatch.setattr('src.services.read_excel_transactions', lambda x: mock_transactions)
    result = search_transactions("ЮНОСТЬ")
    expected = json.dumps([mock_transactions[0], mock_transactions[1]], ensure_ascii=False, indent=2)
    assert result == expected
