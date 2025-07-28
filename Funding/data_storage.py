import time
from typing import Dict, Any, Optional


class DataStorage:
    def __init__(self):
        """
        Универсальное хранилище данных по финансовым инструментам с возможностью
        хранения дополнительных параметров.
        """
        self._storage: Dict[str, Dict[str, Any]] = {}

    def set(self, data: Dict[str, Any]):
        """
        Сохраняет данные с текущей временной меткой. Обновляет существующие ключи или добавляет новые.

        :param data: Словарь, должен содержать как минимум 'symbol'.
                     Остальные ключи будут добавлены в хранилище.
        :raises ValueError: Если данные не соответствуют формату
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        if 'symbol' not in data:
            raise ValueError("Data must contain 'symbol' key")

        symbol = data['symbol']

        # Если символ уже есть, обновляем словарь
        if symbol not in self._storage:
            self._storage[symbol] = {}

        # Обновляем данные
        for key, value in data.items():
            if key != 'symbol':
                self._storage[symbol][key] = value

        # Обновляем timestamp при каждом обновлении
        self._storage[symbol]["timestamp"] = int(time.time())

    def get(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Получает все данные по символу.

        :return: Словарь с произвольными ключами и значениями, включая timestamp, или None
        """
        if symbol not in self._storage:
            return None

        # Возвращаем копию словаря, включая 'symbol'
        return {
            "symbol": symbol,
            **self._storage[symbol]
        }


data_storage = DataStorage()

if __name__ == "__main__":

    # Добавляем базовые данные
    data_storage.set({'symbol': "USDRUBF", 'avg_price': 81.04})
    data_storage.set({'symbol': "EURRUBF", 'avg_price': 89.12, 'fund': 123})

    # Добавляем дополнительные данные
    data_storage.set({'symbol': "USDRUBF", 'cbr_price': 80.99})

    # Получаем данные
    print(data_storage.get("EURRUBF"))
    print(data_storage.get("USDRUBF"))
    print(data_storage.get("xc"))
