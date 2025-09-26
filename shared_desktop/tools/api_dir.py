import os
import requests
import time

from django.http import JsonResponse
from django.shortcuts import render

from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Конфигурация
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

# Глобальные переменные для хранения токена и времени его получения
TOKEN_CACHE = {
    "token": None,
    "timestamp": None
}

def get_token(api_key):
    """
    Возвращает рабочий токен. Кеширует токен и дату окончания его действия.
    При каждом вызове проверяет локально срок действия и обновляет токен только при необходимости.
    """
    global TOKEN_CACHE
    current_time = time.time()

    # Проверяем, есть ли токен и не истек ли срок действия
    token = TOKEN_CACHE.get("token")
    expiration = TOKEN_CACHE.get("expiration")  # timestamp в секундах

    if token and expiration:
        if current_time < expiration:
            # Токен еще действителен
            return token
        else:
            print("Токен истек, обновляем...")

    # Получаем новый токен
    url = f"{API_URL}/auth/refresh?APIKey={api_key}"
    headers = {"accept": "application/json"}
    try:
        response = requests.post(url, headers=headers, timeout=5)
        data = response.json()
        if response.status_code == 200 and data.get("Success"):
            token = data["Auth"]["Token"]
            exp_str = data["Auth"]["ExpirationDate"]  # строка ISO
            # Преобразуем ExpirationDate в timestamp
            from datetime import datetime, timezone
            exp_dt = datetime.fromisoformat(exp_str.replace("Z", "+00:00"))
            expiration_timestamp = exp_dt.timestamp()

            # Сохраняем в кеш
            TOKEN_CACHE["token"] = token
            TOKEN_CACHE["expiration"] = expiration_timestamp
            print("Получен новый токен")
            return token
        else:
            print(f"Ошибка получения токена: {response.status_code} - {response.text}")
            TOKEN_CACHE["token"] = None
            TOKEN_CACHE["expiration"] = None
            return None
    except Exception as e:
        print(f"Ошибка запроса токена: {e}")
        TOKEN_CACHE["token"] = None
        TOKEN_CACHE["expiration"] = None
        return None

# Функция для получения информации о контроллере
def get_controller_info(controller_id, token):
    url = f"{API_URL}/controllers/ext:{controller_id}"
    headers = {"accept": "application/json", "x-rmsapi-token": token}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:  # Unauthorized - токен истек
        print(f"Токен недействителен (статус 401), обновляем...")
        # Сбрасываем кеш токена
        TOKEN_CACHE["token"] = None
        TOKEN_CACHE["expiration"] = None
        return {
            "Success": False,
            "Message": "Токен истек, требуется обновление",
            "StatusCode": response.status_code
        }
    else:
        return {
            "Success": False,
            "Message": f"Не удалось получить информацию о контроллере. Статус код: {response.status_code}",
            "StatusCode": response.status_code
        }

# Функция для получения статуса контроллера
def get_controller_status(controller_id, token):
    url = f"{API_URL}/controllers/ext:{controller_id}/status"
    headers = {"accept": "application/json", "x-rmsapi-token": token}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:  # Unauthorized - токен истек
        print(f"Токен недействителен (статус 401), обновляем...")
        # Сбрасываем кеш токена, чтобы при следующем вызове get_token получили новый
        TOKEN_CACHE["token"] = None
        TOKEN_CACHE["expiration"] = None
        return {
            "Success": False,
            "Message": "Токен истек, требуется обновление",
            "StatusCode": response.status_code
        }
    else:
        return {
            "Success": False,
            "Message": f"Не удалось получить статус контроллера. Статус код: {response.status_code}",
            "StatusCode": response.status_code
        }

# Основная функция для обработки запросов
def api_dir(request):
    if request.method == "POST":
        controller_id = request.POST.get("controllerId")
        token = get_token(API_KEY)
        if token:
            controller_info = get_controller_info(controller_id, token)
            controller_status = get_controller_status(controller_id, token)

            # Если получили ошибку связанную с токеном, пробуем обновить токен и повторить запрос
            if controller_status.get("StatusCode") == 401:
                print("Повторяем запрос статуса с обновленным токеном...")
                token = get_token(API_KEY)  # Получаем новый токен
                if token:
                    controller_status = get_controller_status(controller_id, token)

            # Также проверяем информацию контроллера на ошибки токена
            if controller_info.get("StatusCode") == 401:
                print("Повторяем запрос информации с обновленным токеном...")
                token = get_token(API_KEY)  # Получаем новый токен
                if token:
                    controller_info = get_controller_info(controller_id, token)

            response = {"Success": True}

            if controller_info.get("Success"):
                response["Controller"] = controller_info.get("Controller")
            else:
                response["ControllerError"] = controller_info.get("Message")

            if controller_status.get("Success"):
                response["ControllerStatus"] = controller_status.get(
                    "ControllerStatus"
                )
            else:
                response["ControllerStatusError"] = controller_status.get(
                    "Message"
                )

            if (
                "Controller" not in response
                and "ControllerStatus" not in response
            ):
                response["Success"] = False
                response["Message"] = (
                    "Не удалось получить информацию о контроллере или его статус."
                )

            return JsonResponse(response)
        else:
            return JsonResponse(
                {
                    "Success": False,
                    "Message": "Не удалось получить токен авторизации.",
                }
            )
    return render(request, "tools/api_dir.html")

# Функция проверки связи маршрута 10
def controllers_status_check(request):
    # Список тестовых контроллеров
    controllers = ["827", "818", "828", "854", "3632", "2191", "3139", "3355", "2274"]

    token = get_token(API_KEY)
    if not token:
        return JsonResponse({
            "Success": False,
            "Message": "Не удалось получить токен авторизации."
        })

    results = []
    for controller_id in controllers:
        status_data = get_controller_status(controller_id, token)

        # Если получили ошибку 401, обновляем токен и повторяем запрос для этого контроллера
        if status_data.get("StatusCode") == 401:
            print(f"Обновляем токен и повторяем запрос для контроллера {controller_id}...")
            token = get_token(API_KEY)
            if token:
                status_data = get_controller_status(controller_id, token)

        # Проверим, что пришёл ответ от API
        if not status_data.get("Success"):
            results.append({
                "ControllerId": controller_id,
                "Status": "Ошибка запроса"
            })
            continue

        # Получаем список ошибок
        faults = status_data.get("ControllerStatus", {}).get("Faults", [])

        # Нормализуем коды к числу и проверяем наличие 10002
        has_fault = any(int(f.get("Code")) == 10002 for f in faults if f.get("Code") is not None)

        results.append({
            "ControllerId": controller_id,
            "Status": "Нет связи" if has_fault else "На связи"
        })

    return JsonResponse({
        "Success": True,
        "Controllers": results
    })
