#!/usr/bin/env python3
"""
Трекер звичок (Варіант 7)
Консольна утиліта для відстеження виконання щоденних звичок.
Зберігає дані у JSON-файлі habits.json.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, date, timedelta
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# Конфігурація
# ═══════════════════════════════════════════════════════════════

DATA_FILE = "habits.json"

# Дні тижня (Пн = 0, Нд = 6)
WEEKDAY_NAMES_UA = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]

# Символи для виведення (ASCII-safe, працюють у будь-якому кодуванні)
CHECK_MARK = "[X]"
EMPTY_MARK = "[ ]"
LINE_SEP = "-" * 50
LINE_EQ  = "=" * 50
TICK_OK  = "[OK]"
TICK_WARN = "[WARN]"
TICK_ERR = "[ERR]"


# ═══════════════════════════════════════════════════════════════
# Робота з файлами даних
# ═══════════════════════════════════════════════════════════════

def load_data() -> dict:
    """
    Завантажує дані з JSON-файлу.
    Якщо файл не існує, створює його зі структурою за замовчуванням.
    Якщо файл порожній або пошкоджений, повертає структуру за замовчуванням.

    Повертає:
        dict з ключами 'habits' (list) та 'checkins' (list).
    """
    default_data = {"habits": [], "checkins": []}

    if not os.path.exists(DATA_FILE):
        save_data(default_data)
        return dict(default_data)

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                save_data(default_data)
                return dict(default_data)
            data = json.loads(content)
            # Переконаємось, що ключі існують
            if "habits" not in data:
                data["habits"] = []
            if "checkins" not in data:
                data["checkins"] = []
            return data
    except (json.JSONDecodeError, IOError):
        save_data(default_data)
        return dict(default_data)


def save_data(data: dict) -> None:
    """
    Зберігає дані у JSON-файл.
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════
# Допоміжні функції
# ═══════════════════════════════════════════════════════════════

def get_next_id(habits: list) -> int:
    """
    Повертає наступний унікальний ID для нової звички.
    """
    if not habits:
        return 1
    return max(h["id"] for h in habits) + 1


def parse_date(user_input: str) -> Optional[date]:
    """
    Парсить рядок у дату. Формати: YYYY-MM-DD, DD.MM.YYYY.
    Якщо рядок порожній, повертає поточну дату.
    Якщо формат неправильний, повертає None.
    """
    user_input = user_input.strip()
    if not user_input:
        return date.today()

    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(user_input, fmt).date()
        except ValueError:
            continue
    return None


def find_habit_by_id(habits: list, habit_id: int) -> Optional[dict]:
    """
    Знаходить звичку за ID у списку звичок.
    """
    for h in habits:
        if h["id"] == habit_id:
            return h
    return None


def get_week_start(target_date: date = None) -> date:
    """
    Повертає дату понеділка поточного тижня для заданої дати.
    """
    if target_date is None:
        target_date = date.today()
    # isoweekday(): Пн=1, Вт=2 ... Нд=7
    # Віднімаємо (isoweekday - 1) днів, щоб отримати Пн
    delta = target_date.isoweekday() - 1
    return target_date - timedelta(days=delta)


def get_week_days(week_start: date) -> list:
    """
    Повертає список дат (date) від понеділка до неділі заданого тижня.
    """
    return [week_start + timedelta(days=i) for i in range(7)]


def get_days_in_month(target_date: date = None) -> int:
    """
    Повертає кількість днів у місяці для заданої дати.
    """
    if target_date is None:
        target_date = date.today()
    year = target_date.year
    month = target_date.month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day = next_month - timedelta(days=1)
    return last_day.day


# ═══════════════════════════════════════════════════════════════
# Основні функції меню
# ═══════════════════════════════════════════════════════════════

def add_habit(data: dict) -> dict:
    """
    Додає нову звичку.
    Користувач вводить назву та періодичність/ціль.
    """
    print(f"\n--- Додавання нової звички ---")

    name = input("Назва звички: ").strip()
    if not name:
        print(f" {TICK_ERR} Назва не може бути порожньою.")
        return data

    # Перевірка на дублікат
    if any(h["name"].lower() == name.lower() for h in data["habits"]):
        print(f" {TICK_ERR} Звичка '{name}' вже існує.")
        return data

    goal_input = input("Ціль на день (Enter = 1): ").strip()
    try:
        goal = int(goal_input) if goal_input else 1
        if goal < 1:
            print(f" {TICK_ERR} Ціль має бути додатним числом. Встановлено 1.")
            goal = 1
    except ValueError:
        print(f" {TICK_WARN} Некоректне число. Встановлено ціль = 1.")
        goal = 1

    habit = {
        "id": get_next_id(data["habits"]),
        "name": name,
        "goal": goal,
        "created_at": date.today().isoformat(),
    }

    data["habits"].append(habit)
    save_data(data)
    print(f" {TICK_OK} Звичка '{name}' додана з ID = {habit['id']}.")
    return data


def add_checkin(data: dict) -> dict:
    """
    Додає відмітку про виконання звички за вказану дату.
    """
    print(f"\n--- Щоденна відмітка ---")

    if not data["habits"]:
        print(f" {TICK_ERR} Немає жодної звички. Спочатку додайте звичку.")
        return data

    # Показуємо наявні звички
    print("Наявні звички:")
    for h in data["habits"]:
        print(f"  ID {h['id']}: {h['name']} (ціль: {h['goal']} на день)")

    id_input = input("ID звички: ").strip()
    try:
        habit_id = int(id_input)
    except ValueError:
        print(f" {TICK_ERR} ID має бути числом.")
        return data

    habit = find_habit_by_id(data["habits"], habit_id)
    if habit is None:
        print(f" {TICK_ERR} Звички з ID {habit_id} не знайдено.")
        return data

    date_input = input("Дата (YYYY-MM-DD або DD.MM.YYYY, Enter = сьогодні): ").strip()
    check_date = parse_date(date_input)
    if check_date is None:
        print(f" {TICK_ERR} Неправильний формат дати. Використовуйте YYYY-MM-DD або DD.MM.YYYY.")
        return data

    # Перевіряємо, чи вже є відмітка за цю дату
    for c in data["checkins"]:
        if c["habit_id"] == habit_id and c["date"] == check_date.isoformat():
            print(f" {TICK_WARN} Відмітка за {check_date} вже існує для цієї звички.")
            return data

    checkin = {
        "habit_id": habit_id,
        "date": check_date.isoformat(),
    }
    data["checkins"].append(checkin)
    save_data(data)
    print(f" {TICK_OK} Відмітка додана: {habit['name']} -- {check_date}.")
    return data


def show_weekly_status(data: dict) -> None:
    """
    Виводить таблицю виконання звичок за поточний тиждень (Пн-Нд).
    """
    print(f"\n--- Статус за поточний тиждень ---")

    if not data["habits"]:
        print(f" {TICK_ERR} Немає жодної звички.")
        return

    today = date.today()
    week_start = get_week_start(today)
    week_days = get_week_days(week_start)

    # Формуємо набір відміток для швидкого пошуку
    checkin_set = set()
    for c in data["checkins"]:
        checkin_set.add((c["habit_id"], c["date"]))

    # Шапка таблиці
    header_days = " | ".join(
        f"{WEEKDAY_NAMES_UA[i]} {d.day:02d}" for i, d in enumerate(week_days)
    )
    print(f"{'Звичка':<20} | {header_days}")
    print("-" * (22 + len(header_days)))

    for h in data["habits"]:
        name = h["name"] if len(h["name"]) <= 18 else h["name"][:17] + "~"
        row = f"{name:<20} | "
        for d in week_days:
            iso = d.isoformat()
            if (h["id"], iso) in checkin_set:
                row += f"{CHECK_MARK}".center(6)
            else:
                row += f"{EMPTY_MARK}".center(6)
        print(row)

    print(f"\nТиждень: {week_start} -- {week_days[-1]}")


def show_statistics(data: dict) -> None:
    """
    Виводить статистику виконання звичок за поточний місяць.
    """
    print(f"\n--- Відсоток виконання за поточний місяць ---")

    if not data["habits"]:
        print(f" {TICK_ERR} Немає жодної звички.")
        return

    today = date.today()
    month_start = date(today.year, today.month, 1)
    days_in_month = get_days_in_month(today)
    month_end = date(today.year, today.month, days_in_month)

    # Визначаємо, скільки днів минуло в місяці
    if today > month_end:
        elapsed_days = days_in_month
    else:
        elapsed_days = today.day

    if elapsed_days == 0:
        elapsed_days = 1  # захист від ділення на нуль

    print(f"Період: {month_start} -- {today}")
    print(f"Всього днів у місяці: {days_in_month}, минуло: {elapsed_days}")
    print()

    for h in data["habits"]:
        habit_id = h["id"]
        name = h["name"]
        goal = h["goal"]

        # Підраховуємо кількість відміток за цей місяць
        count = sum(
            1
            for c in data["checkins"]
            if c["habit_id"] == habit_id
            and month_start.isoformat() <= c["date"] <= today.isoformat()
        )

        # Відносно цілі (goal на день * кількість днів)
        total_goal = goal * elapsed_days
        percent_goal = (count / total_goal * 100) if total_goal > 0 else 0.0

        # Відносно кількості днів (1 виконання на день = 100%)
        percent_days = (count / elapsed_days * 100) if elapsed_days > 0 else 0.0

        print(f"  {name} (ID {habit_id}):")
        print(f"    Виконань за місяць: {count}")
        print(f"    Відносно цілі ({goal} на день): {percent_goal:.1f}%")
        print(f"    Відносно днів періоду:   {percent_days:.1f}%")
        print()


def show_all_habits(data: dict) -> None:
    """
    Виводить список усіх звичок.
    """
    print(f"\n--- Список звичок ---")
    if not data["habits"]:
        print(f" {TICK_ERR} Звичок поки що немає.")
        return
    for h in data["habits"]:
        print(f"  ID {h['id']}: {h['name']} (ціль: {h['goal']} на день)")


# ═══════════════════════════════════════════════════════════════
# Запуск автотесту
# ═══════════════════════════════════════════════════════════════

def run_tests(data: dict = None) -> None:
    """
    Запускає автоматизований тест (test_habits.py) через підпроцес.
    Параметр data приймається для сумісності з механізмом меню, але не використовується.
    """
    print(f"\n--- Запуск автотесту ---")
    print("Виконується test_habits.py...\n")

    try:
        result = subprocess.run(
            [sys.executable, "test_habits.py"],
            capture_output=True,
            text=True,
        )
        # Виводимо stdout тесту
        print(result.stdout)

        if result.returncode != 0:
            print(f" {TICK_ERR} Тест завершився з помилкою (код {result.returncode})")
            if result.stderr:
                print(result.stderr)
        else:
            print(f" {TICK_OK} Автотест виконано успішно!")

    except FileNotFoundError:
        print(f" {TICK_ERR} Файл test_habits.py не знайдено.")
        print("   Спочатку створіть файл test_habits.py або переконайтесь,")
        print("   що він знаходиться в тій самій папці, що й main.py.")
    except Exception as e:
        print(f" {TICK_ERR} Помилка запуску тесту: {e}")


# ═══════════════════════════════════════════════════════════════
# Меню
# ═══════════════════════════════════════════════════════════════

def menu() -> None:
    """
    Головний цикл меню. Використовує словник для виклику функцій.
    """
    data = load_data()

    menu_items = {
        "1": ("Додати звичку", add_habit),
        "2": ("Щоденна відмітка", add_checkin),
        "3": ("Статус за тиждень", show_weekly_status),
        "4": ("Відсоток виконання", show_statistics),
        "5": ("Список звичок", show_all_habits),
        "6": ("Запустити автотест", run_tests),
        "0": ("Вийти", None),
    }

    while True:
        print(f"\n{LINE_EQ}")
        print("         ТРЕКЕР ЗВИЧОК -- Головне меню")
        print(f"{LINE_EQ}")
        for key, (desc, _) in menu_items.items():
            print(f"  {key}. {desc}")
        print(f"{LINE_SEP}")

        choice = input("Ваш вибір: ").strip()

        # Варіант з виходом обробляємо окремо
        if choice == "0":
            print("До побачення!")
            break

        if choice in menu_items:
            _, func = menu_items[choice]
            try:
                # Для run_tests передаємо data (вона ігнорується, але сумісність)
                if func is run_tests:
                    func(data)
                # Якщо функція повертає data (тобто змінює дані)
                elif func in (add_habit, add_checkin):
                    data = func(data)
                else:
                    # Функції, які тільки виводять інформацію (не змінюють data)
                    func(data)
            except Exception as e:
                print(f" {TICK_ERR} Сталася помилка: {e}")
        else:
            print(f" {TICK_ERR} Невірний вибір: '{choice}'. Введіть число зі списку.")


# ═══════════════════════════════════════════════════════════════
# Точка входу
