#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
9 ТЕСТОВ БЭКЕНДА - WINDOWS ВЕРСИЯ С АВТООЧИСТКОЙ
Работает в PowerShell PyCharm на Windows
"""

import requests
import json
import sys
from datetime import datetime
from typing import Tuple, Optional

BASE_URL = "http://192.168.0.21:5000/api"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def log(msg: str, status: str = "OK") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    symbols = {
        "OK": "✓",
        "ERR": "✗",
        "TEST": "►",
        "INFO": "ℹ",
        "WARN": "⚠"
    }
    colors = {
        "OK": Colors.GREEN,
        "ERR": Colors.RED,
        "TEST": Colors.BLUE,
        "INFO": Colors.CYAN,
        "WARN": Colors.YELLOW
    }

    color = colors.get(status, Colors.RESET)
    symbol = symbols.get(status, "•")
    print(f"{color}{Colors.BOLD}[{ts}] {symbol} {msg}{Colors.RESET}")


def detail(msg: str) -> None:
    print(f"  → {msg}")


def error_detail(msg: str) -> None:
    print(f"{Colors.RED}  ✗ {msg}{Colors.RESET}")


def separator(title: str = "") -> None:
    if title:
        print(f"\n{'=' * 70}")
        print(f"║ {title:^66} ║")
        print(f"{'=' * 70}\n")
    else:
        print(f"\n{'=' * 70}\n")


def show_error_response(response: requests.Response) -> None:
    """Показывает детали ошибки из ответа"""
    error_detail(f"HTTP Status: {response.status_code}")
    error_detail(f"URL: {response.url}")

    try:
        data = response.json()
        error_detail(f"JSON ответ:")
        print(f"{Colors.YELLOW}{json.dumps(data, indent=2, ensure_ascii=False)}{Colors.RESET}")
    except:
        error_detail(f"Текст ответа: {response.text[:500]}")


def cleanup_test_user():
    """Удаляет тестового пользователя login11 перед запуском тестов"""
    try:
        print(f"{Colors.CYAN}🔍 Проверка наличия тестового пользователя login11...{Colors.RESET}")

        # Авторизуемся как login1
        r = requests.post(f"{BASE_URL}/auth/login",
                          json={"login": "login1", "password": "pass1"},
                          timeout=5)

        if r.status_code != 200:
            print(f"{Colors.RED}⚠️  Не удалось авторизоваться для очистки{Colors.RESET}")
            return

        token = r.json().get("access_token")

        # Получаем список пользователей
        r = requests.get(f"{BASE_URL}/users/",
                         headers={"Authorization": f"Bearer {token}"},
                         timeout=5)

        if r.status_code == 200:
            users = r.json().get("data", [])
            login11_user = next((u for u in users if u.get('login') == 'login11'), None)

            if login11_user:
                user_id = login11_user.get('user_id')

                # Удаляем login11
                r = requests.delete(f"{BASE_URL}/users/{user_id}",
                                    headers={"Authorization": f"Bearer {token}"},
                                    timeout=5)

                if r.status_code == 200:
                    print(f"{Colors.GREEN}🗑️  Удален старый пользователь login11 (ID: {user_id}){Colors.RESET}")
                else:
                    print(f"{Colors.RED}⚠️  Не удалось удалить login11 (статус: {r.status_code}){Colors.RESET}")
                    show_error_response(r)
            else:
                print(f"{Colors.GREEN}✓ login11 не найден, можно создавать нового{Colors.RESET}")
        else:
            print(f"{Colors.RED}⚠️  Не удалось получить список пользователей{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Ошибка при очистке: {str(e)}{Colors.RESET}")


def test_1_auth_login1() -> Tuple[bool, Optional[str]]:
    """ТЕСТ 1: Получить токен login1"""
    separator("ТЕСТ 1: АУТЕНТИФИКАЦИЯ login1 (Менеджер)")

    log("POST /api/auth/login", "TEST")
    detail("Логин: login1")
    detail("Пароль: pass1")

    try:
        r = requests.post(f"{BASE_URL}/auth/login",
                          json={"login": "login1", "password": "pass1"},
                          timeout=5)

        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")

            log(f"✓ Авторизация успешна! (200)", "OK")
            detail(f"User ID: {data.get('user_id')}")
            detail(f"Логин: {data.get('login')}")
            detail(f"ФИО: {data.get('full_name')}")
            detail(f"Роль: {data.get('user_type')}")
            detail(f"Токен: {token[:30]}...")

            return True, token
        else:
            log(f"✗ Ошибка авторизации", "ERR")
            show_error_response(r)
            return False, None

    except requests.exceptions.ConnectionError:
        log(f"✗ Не удалось подключиться к серверу {BASE_URL}", "ERR")
        error_detail("Проверьте, что Flask-сервер запущен!")
        return False, None
    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False, None


def test_2_create_login11(token: str) -> Tuple[bool, Optional[int]]:
    """ТЕСТ 2: Создать пользователя login11"""
    separator("ТЕСТ 2: СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ (login11/pass11)")

    log("POST /api/users/ - Создание нового пользователя", "TEST")

    user_data = {
        "full_name": "Иван Качество",
        "phone": "8-912-345-67-89",
        "login": "login11",
        "password": "pass11",
        "user_type": "Менеджер по качеству"
    }

    detail(f"ФИО: {user_data['full_name']}")
    detail(f"Телефон: {user_data['phone']}")
    detail(f"Логин: {user_data['login']}")
    detail(f"Роль: {user_data['user_type']}")

    try:
        r = requests.post(f"{BASE_URL}/users/",
                          json=user_data,
                          headers={"Authorization": f"Bearer {token}"},
                          timeout=5)

        if r.status_code == 201:
            data = r.json()
            user_id = data.get("user_id")

            log(f"✓ Пользователь создан! (201)", "OK")
            detail(f"User ID: {user_id}")
            detail(f"Логин: {data.get('login')}")
            detail(f"Роль: {data.get('user_type')}")

            return True, user_id
        else:
            log(f"✗ Ошибка создания пользователя", "ERR")
            show_error_response(r)
            return False, None

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False, None


def test_3_auth_login11() -> Tuple[bool, Optional[str]]:
    """ТЕСТ 3: Аутентификация login11"""
    separator("ТЕСТ 3: АУТЕНТИФИКАЦИЯ login11")

    log("POST /api/auth/login - Вход как login11", "TEST")
    detail("Логин: login11")
    detail("Пароль: pass11")

    try:
        r = requests.post(f"{BASE_URL}/auth/login",
                          json={"login": "login11", "password": "pass11"},
                          timeout=5)

        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")

            log(f"✓ Авторизация успешна! (200)", "OK")
            detail(f"User ID: {data.get('user_id')}")
            detail(f"ФИО: {data.get('full_name')}")
            detail(f"Роль: {data.get('user_type')}")
            detail(f"Токен: {token[:30]}...")

            return True, token
        else:
            log(f"✗ Ошибка авторизации login11", "ERR")
            show_error_response(r)
            return False, None

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False, None


def test_4_get_users(token: str) -> bool:
    """ТЕСТ 4: GET /users/"""
    separator("ТЕСТ 4: ПОЛУЧЕНИЕ СПИСКА ПОЛЬЗОВАТЕЛЕЙ")

    log("GET /api/users/", "TEST")
    detail("Получить всех пользователей")

    try:
        r = requests.get(f"{BASE_URL}/users/",
                         headers={"Authorization": f"Bearer {token}"},
                         timeout=5)

        if r.status_code == 200:
            data = r.json().get("data", [])

            log(f"✓ Список получен! (200)", "OK")
            detail(f"Всего пользователей: {len(data)}")

            if data:
                log("Первые 3 пользователя:", "INFO")
                for i, user in enumerate(data[:3], 1):
                    detail(f"{i}. {user.get('full_name')} ({user.get('login')}) - {user.get('user_type')}")

            return True
        else:
            log(f"✗ Ошибка получения списка пользователей", "ERR")
            show_error_response(r)
            return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_5_get_requests(token: str) -> bool:
    """ТЕСТ 5: GET /requests/"""
    separator("ТЕСТ 5: ПОЛУЧЕНИЕ СПИСКА ЗАЯВОК")

    log("GET /api/requests/", "TEST")
    detail("Получить все заявки (page=1, limit=20)")

    try:
        r = requests.get(f"{BASE_URL}/requests/?page=1&limit=20",
                         headers={"Authorization": f"Bearer {token}"},
                         timeout=5)

        if r.status_code == 200:
            data = r.json().get("data", [])

            log(f"✓ Список получен! (200)", "OK")
            detail(f"Всего заявок: {len(data)}")

            if data:
                log("Первые 2 заявки:", "INFO")
                for i, req in enumerate(data[:2], 1):
                    detail(
                        f"{i}. ID={req.get('request_id')} | {req.get('climate_tech_type')} | {req.get('request_status')}")

            return True
        else:
            log(f"✗ Ошибка получения списка заявок", "ERR")
            show_error_response(r)
            return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_6_get_specialists(token: str) -> bool:
    """ТЕСТ 6: GET /specialists"""
    separator("ТЕСТ 6: ПОЛУЧЕНИЕ СПИСКА СПЕЦИАЛИСТОВ")

    log("GET /api/users/specialists", "TEST")
    detail("Получить всех специалистов")

    try:
        r = requests.get(f"{BASE_URL}/users/specialists",
                         headers={"Authorization": f"Bearer {token}"},
                         timeout=5)

        if r.status_code == 200:
            data = r.json().get("data", [])

            log(f"✓ Список получен! (200)", "OK")
            detail(f"Всего специалистов: {len(data)}")

            if data:
                log("Специалисты в системе:", "INFO")
                for i, spec in enumerate(data, 1):
                    detail(f"{i}. {spec.get('full_name')} ({spec.get('login')})")

            return True
        else:
            log(f"✗ Ошибка получения списка специалистов", "ERR")
            show_error_response(r)
            return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_7_create_request(token: str) -> bool:
    """ТЕСТ 7: POST /requests/"""
    separator("ТЕСТ 7: СОЗДАНИЕ НОВОЙ ЗАЯВКИ")

    log("POST /api/requests/", "TEST")
    detail("Создать новую заявку")

    request_data = {
        "climate_tech_type": "Холодильник",
        "climate_tech_model": "Atlant Test",
        "problem_description": "Не охлаждает, издаёт странные звуки",
        "client_id": 6
    }

    detail(f"Тип: {request_data['climate_tech_type']}")
    detail(f"Модель: {request_data['climate_tech_model']}")
    detail(f"Проблема: {request_data['problem_description']}")
    detail(f"Client ID: {request_data['client_id']}")

    try:
        r = requests.post(f"{BASE_URL}/requests/",
                          json=request_data,
                          headers={"Authorization": f"Bearer {token}"},
                          timeout=5)

        if r.status_code == 201:
            data = r.json()

            log(f"✓ Заявка создана! (201)", "OK")
            detail(f"Request ID: {data.get('request_id')}")
            detail(f"Статус: {data.get('request_status')}")

            return True
        else:
            log(f"✗ Ошибка создания заявки", "ERR")
            show_error_response(r)
            return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_8_get_statistics(token: str) -> bool:
    """ТЕСТ 8: GET /statistics/"""
    separator("ТЕСТ 8: ПОЛУЧЕНИЕ СТАТИСТИКИ")

    log("GET /api/statistics/", "TEST")
    detail("Получить статистику работы")

    try:
        r = requests.get(f"{BASE_URL}/statistics/",
                         headers={"Authorization": f"Bearer {token}"},
                         timeout=5)

        if r.status_code == 200:
            data = r.json()

            log(f"✓ Статистика получена! (200)", "OK")

            log("Полученные данные:", "INFO")
            print(f"{Colors.CYAN}{json.dumps(data, indent=2, ensure_ascii=False)[:500]}...{Colors.RESET}")

            return True
        else:
            log(f"✗ Ошибка получения статистики", "ERR")
            show_error_response(r)
            return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def test_9_permissions(token: str) -> bool:
    """ТЕСТ 9: Проверка прав доступа (403)"""
    separator("ТЕСТ 9: ПРОВЕРКА ПРАВ ДОСТУПА")

    log("POST /api/users/ как Менеджер по качеству (должна быть ошибка 403)", "TEST")
    detail("Попытка добавить пользователя без прав")
    detail("Ожидаемый результат: 403 Permission Denied")

    try:
        r = requests.post(f"{BASE_URL}/users/",
                          json={
                              "full_name": "Тест Юзер",
                              "phone": "8-999-999-99-99",
                              "login": "test_user",
                              "password": "pass123",
                              "user_type": "Оператор"
                          },
                          headers={"Authorization": f"Bearer {token}"},
                          timeout=5)

        if r.status_code == 403:
            data = r.json()
            error_msg = data.get("error", "")

            log(f"✓ Ошибка 403 получена правильно!", "OK")
            detail(f"Сообщение: {error_msg}")

            return True
        else:
            log(f"✗ Ожидалась 403, получена {r.status_code}", "WARN")
            show_error_response(r)
            return False

    except Exception as e:
        log(f"✗ Исключение: {str(e)}", "ERR")
        return False


def main():
    separator("ПОЛНАЯ ДИАГНОСТИКА БЭКЕНДА - 9 ТЕСТОВ")

    # АВТООЧИСТКА перед тестами
    cleanup_test_user()
    print()

    tests_passed = []
    tests_failed = []

    # ТЕСТ 1
    success, token1 = test_1_auth_login1()
    if success and token1:
        tests_passed.append("Auth login1")
    else:
        tests_failed.append("Auth login1")
        print("\n" + Colors.RED + "❌ Невозможно продолжать без токена!" + Colors.RESET)
        return 1

    # ТЕСТ 2
    success, user_id = test_2_create_login11(token1)
    if success:
        tests_passed.append("Create login11")
    else:
        tests_failed.append("Create login11")

    # ТЕСТ 3
    success, token11 = test_3_auth_login11()
    if success and token11:
        tests_passed.append("Auth login11")
    else:
        tests_failed.append("Auth login11")
        token11 = None

    # ТЕСТ 4
    if test_4_get_users(token1):
        tests_passed.append("GET users")
    else:
        tests_failed.append("GET users")

    # ТЕСТ 5
    if test_5_get_requests(token1):
        tests_passed.append("GET requests")
    else:
        tests_failed.append("GET requests")

    # ТЕСТ 6
    if test_6_get_specialists(token1):
        tests_passed.append("GET specialists")
    else:
        tests_failed.append("GET specialists")

    # ТЕСТ 7
    test_token = token11 if token11 else token1
    if test_7_create_request(test_token):
        tests_passed.append("POST request")
    else:
        tests_failed.append("POST request")

    # ТЕСТ 8
    if test_8_get_statistics(token1):
        tests_passed.append("GET statistics")
    else:
        tests_failed.append("GET statistics")

    # ТЕСТ 9
    if token11:
        if test_9_permissions(token11):
            tests_passed.append("Permissions check")
        else:
            tests_failed.append("Permissions check")
    else:
        tests_failed.append("Permissions check (токен login11 недоступен)")

    # ИТОГОВЫЙ ОТЧЁТ
    separator("ИТОГОВЫЙ ОТЧЁТ")

    print("Результаты тестов:\n")
    for test_name in tests_passed:
        print(f"  {Colors.GREEN}✓ PASS{Colors.RESET}  {test_name}")

    for test_name in tests_failed:
        print(f"  {Colors.RED}✗ FAIL{Colors.RESET}  {test_name}")

    total = len(tests_passed) + len(tests_failed)
    print(f"\n{'=' * 70}")
    print(
        f"Всего: {total} тестов | Пройдено: {Colors.GREEN}{len(tests_passed)}{Colors.RESET} | Ошибок: {Colors.RED}{len(tests_failed)}{Colors.RESET}")
    print(f"{'=' * 70}")

    if len(tests_failed) == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!{Colors.RESET}\n")
        print("🎉 Статус системы: ГОТОВА К ИСПОЛЬЗОВАНИЮ")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ {len(tests_failed)} ТЕСТОВ НЕ ПРОШЛИ{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log("\n\n⚠ Тестирование прервано пользователем", "WARN")
        sys.exit(2)
    except Exception as e:
        log(f"💥 Критическая ошибка: {str(e)}", "ERR")
        import traceback

        traceback.print_exc()
        sys.exit(2)
