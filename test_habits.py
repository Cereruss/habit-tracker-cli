"""
test_habits.py
Автоматизований тест для функцій трекера звичок.
Перевіряє логіку підрахунку статистики та відсотка виконання.
Кожен тест працює з тимчасовим файлом test_data.json,
що не впливає на основний файл habits.json.
"""

import json
import os
from datetime import date
import main  # iмпортуемо головний модуль

TEST_FILE = "test_data.json"

SEP = "-" * 50


def setup(data: dict):
    """
    Записує тестові дані у тимчасовий файл.
    """
    main.DATA_FILE = TEST_FILE
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def teardown():
    """
    Видаляє тимчасовий файл після тесту.
    """
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


# ======
# Тест 1: Відсоток виконання при нормальних даних
# ======

print(SEP)
print("TECT 1: Відсоток виконання при нормальних даних")
print(SEP)

test_data = {
    "habits": [
        {"id": 1, "name": "Ранкова пробіжка", "goal": 1,
         "created_at": "2026-06-01"},
        {"id": 2, "name": "Читання книг", "goal": 2,
         "created_at": "2026-06-01"},
    ],
    "checkins": [
        {"habit_id": 1, "date": "2026-06-15"},
        {"habit_id": 1, "date": "2026-06-16"},
        {"habit_id": 1, "date": "2026-06-17"},
        {"habit_id": 1, "date": "2026-06-18"},
        {"habit_id": 1, "date": "2026-06-19"},
        {"habit_id": 2, "date": "2026-06-17"},
        {"habit_id": 2, "date": "2026-06-19"},
    ],
}
setup(test_data)
data = main.load_data()

assert len(data["habits"]) == 2
assert len(data["checkins"]) == 7

# Статистика за червень 2026: 01.06 - 19.06
today = date(2026, 6, 19)
month_start = date(2026, 6, 1)
elapsed_days = 19

# Звичка 1: цель = 1, виконань = 5
count_1 = sum(
    1 for c in data["checkins"]
    if c["habit_id"] == 1
    and month_start.isoformat() <= c["date"] <= today.isoformat()
)
total_goal_1 = 1 * elapsed_days
percent_1 = round(count_1 / total_goal_1 * 100, 1)
assert count_1 == 5, f"Звичка 1: очікувалось 5, отримано {count_1}"
assert percent_1 == 26.3, f"Звичка 1: очікувалось 26.3%, отримано {percent_1}%"
print(f"  [OK] Звичка 1: {count_1} виконань, {percent_1}% від цілі")

# Звичка 2: цель = 2, виконань = 2
count_2 = sum(
    1 for c in data["checkins"]
    if c["habit_id"] == 2
    and month_start.isoformat() <= c["date"] <= today.isoformat()
)
total_goal_2 = 2 * elapsed_days
percent_2 = round(count_2 / total_goal_2 * 100, 1)
assert count_2 == 2, f"Звичка 2: очікувалось 2, отримано {count_2}"
assert percent_2 == 5.3, f"Звичка 2: очікувалось 5.3%, отримано {percent_2}%"
print(f"  [OK] Звичка 2: {count_2} виконань, {percent_2}% від цілі")

teardown()
print(" [PASS] Тест 1 пройдено\n")


# ======
# Тест 2: Статистика при порожньому файлі
# ======

print(SEP)
print("TECT 2: Статистика при порожньому файлі")
print(SEP)

setup({"habits": [], "checkins": []})
data = main.load_data()

assert len(data["habits"]) == 0
assert len(data["checkins"]) == 0

# Цикл не виконається жодного разу (список порожній)
for h in data["habits"]:
    raise AssertionError("Не має бути звичок у порожньому файлі")

print("  [OK] Порожні списки обробляються коректно")
teardown()
print(" [PASS] Тест 2 пройдено\n")


# ======
# Тест 3: 100% виконання при заповнених днях
# ======

print(SEP)
print("TECT 3: 100% виконання при заповнених днях")
print(SEP)

checkins_19_days = [
    {"habit_id": 1, "date": f"2026-06-{d:02d}"}
    for d in range(1, 20)
]

test_data = {
    "habits": [
        {"id": 1, "name": "Щоденна медитація", "goal": 1,
         "created_at": "2026-06-01"},
    ],
    "checkins": checkins_19_days,
}
setup(test_data)
data = main.load_data()

today = date(2026, 6, 19)
month_start = date(2026, 6, 1)
elapsed_days = 19

count = sum(
    1 for c in data["checkins"]
    if c["habit_id"] == 1
    and month_start.isoformat() <= c["date"] <= today.isoformat()
)
percent = round(count / (1 * elapsed_days) * 100, 1)

assert count == 19, f"Очікувалось 19 виконань, отримано {count}"
assert percent == 100.0, f"Очікувалось 100.0%, отримано {percent}%"
print(f"  [OK] Виконань: {count} з {elapsed_days} днів = {percent}%")

teardown()
print(" [PASS] Тест 3 пройдено\n")


# ======
# Тест 4: Перевірка parse_date
# ======

print(SEP)
print("TECT 4: Парсинг дат")
print(SEP)

from main import parse_date

d1 = parse_date("2026-06-19")
assert d1 is not None
assert d1.isoformat() == "2026-06-19"
print("  [OK] YYYY-MM-DD: 2026-06-19")

d2 = parse_date("19.06.2026")
assert d2 is not None
assert d2.isoformat() == "2026-06-19"
print("  [OK] DD.MM.YYYY: 19.06.2026")

d3 = parse_date("")
assert d3 == date.today()
print("  [OK] Порожній рядок -> сьогодні")

d4 = parse_date("abc")
assert d4 is None
print("  [OK] Некоректний рядок -> None")

print(" [PASS] Тест 4 пройдено\n")


# ======
# Тест 5: Перевірка find_habit_by_id
# ======

print(SEP)
print("TECT 5: Пошук звички за ID")
print(SEP)

from main import find_habit_by_id

habits = [
    {"id": 1, "name": "Звичка A", "goal": 1},
    {"id": 5, "name": "Звичка B", "goal": 2},
    {"id": 10, "name": "Звичка C", "goal": 3},
]

h = find_habit_by_id(habits, 5)
assert h is not None
assert h["name"] == "Звичка B"
print("  [OK] ID=5 -> Звичка B")

h2 = find_habit_by_id(habits, 999)
assert h2 is None
print("  [OK] ID=999 -> None")

h3 = find_habit_by_id([], 1)
assert h3 is None
print("  [OK] Порожній список -> None")

print(" [PASS] Тест 5 пройдено\n")


# ======
# Завершення
# ======

print("=" * 50)
print(" УСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
print("=" * 50)