from datetime import datetime
from src.utils import get_date


def greeting(time_str: str) -> str:
    """Функция приветствует пользователя, выбирая «Доброе утро» /
    «Добрый день» / «Добрый вечер» / «Доброй ночи» в зависимости
    от текущего времени"""
    try:
        parsed_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        hour = parsed_time.hour
        if 5 <= hour <= 12:
            return "Доброе утро"
        elif 13 <= hour <= 18:
            return "Добрый день"
        elif 19 <= hour <= 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except ValueError:
        return "Ошибка: неверный формат даты и времени"


current_time = get_date()
print(greeting(current_time))
