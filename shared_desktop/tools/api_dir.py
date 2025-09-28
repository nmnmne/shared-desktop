import os
import requests
import time
import json
import logging
from datetime import datetime, timezone

from django.http import JsonResponse
from django.shortcuts import render

from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Конфигурация
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

# Настройка логирования
logger = logging.getLogger('tools')

# Глобальные переменные для хранения токена и времени его получения
TOKEN_CACHE = {
    "token": None,
    "timestamp": None
}

def get_token(api_key):
    global TOKEN_CACHE
    current_time = time.time()  # Это уже UTC timestamp

    token = TOKEN_CACHE.get("token")
    expiration = TOKEN_CACHE.get("expiration")

    if token and expiration:
        # Добавляем запас безопасности (5 минут)
        if current_time < (expiration - 300):
            return token
        else:
            print("Токен истек или скоро истекает, обновляем...")

    # Получаем новый токен
    url = f"{API_URL}/auth/refresh?APIKey={api_key}"
    headers = {"accept": "application/json"}
    try:
        response = requests.post(url, headers=headers, timeout=5)
        data = response.json()
        if response.status_code == 200 and data.get("Success"):
            token = data["Auth"]["Token"]
            exp_str = data["Auth"]["ExpirationDate"]
            
            # Преобразуем строку в datetime с явным указанием UTC
            if exp_str.endswith('Z'):
                exp_dt = datetime.fromisoformat(exp_str[:-1] + '+00:00')
            else:
                exp_dt = datetime.fromisoformat(exp_str)
            
            # Убеждаемся, что время в UTC
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            else:
                exp_dt = exp_dt.astimezone(timezone.utc)
            
            # Получаем корректный UTC timestamp
            expiration_timestamp = exp_dt.timestamp()

            # Добавляем запас безопасности (раньше считаем токен истекшим)
            safety_margin = 300  # 5 минут
            cache_expiration = expiration_timestamp - safety_margin

            # Сохраняем в кеш с запасом безопасности
            TOKEN_CACHE["token"] = token
            TOKEN_CACHE["expiration"] = cache_expiration
            
            # Логируем оба времени
            logger.info(f"{datetime.now().isoformat()} | Token obtained | First 10 chars: {token[:10]} | Server expires: {exp_str} | Client cache expires: {datetime.fromtimestamp(cache_expiration, tz=timezone.utc).isoformat()}")
            
            return token
        else:
            logger.error(f"{datetime.now().isoformat()} | Token error | Status: {response.status_code} | Full response: {response.text}")
            TOKEN_CACHE["token"] = None
            TOKEN_CACHE["expiration"] = None
            return None
    except Exception as e:
        logger.error(f"{datetime.now().isoformat()} | Token exception | Error: {e}")
        TOKEN_CACHE["token"] = None
        TOKEN_CACHE["expiration"] = None
        return None

# Функция для получения информации о контроллере
def get_controller_info(controller_id):
    token = get_token(API_KEY)
    if not token:
        return {
            "Success": False,
            "Message": "Не удалось получить токен авторизации",
            "StatusCode": 401
        }
    
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
def get_controller_status(controller_id):
    token = get_token(API_KEY)
    if not token:
        return {
            "Success": False,
            "Message": "Не удалось получить токен авторизации",
            "StatusCode": 401
        }
    
    url = f"{API_URL}/controllers/ext:{controller_id}/status"
    headers = {"accept": "application/json", "x-rmsapi-token": token}
    response = requests.get(url, headers=headers)
    
    # Логирование только если статус не 200
    if response.status_code != 200:
        logger.info(f"{datetime.now().isoformat()} | {url} | Status: {response.status_code} | Response: {response.text}")
    
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
        
        controller_info = get_controller_info(controller_id)
        controller_status = get_controller_status(controller_id)

        # Если получили ошибку связанную с токеном, пробуем обновить токен и повторить запрос
        if controller_status.get("StatusCode") == 401:
            print("Повторяем запрос статуса с обновленным токеном...")
            controller_status = get_controller_status(controller_id)

        # Также проверяем информацию контроллера на ошибки токена
        if controller_info.get("StatusCode") == 401:
            print("Повторяем запрос информации с обновленным токеном...")
            controller_info = get_controller_info(controller_id)

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
    return render(request, "tools/api_dir.html")

# Функция проверки связи маршрута 10
def controllers_status_check(request):
    # Список тестовых контроллеров
    controllers = ["827", "818", "828", "854", "3632", "2191", "3139", "3355", "2274"]

    results = []
    for controller_id in controllers:
        status_data = get_controller_status(controller_id)

        # Проверим, что пришёл ответ от API
        if not status_data.get("Success"):
            # Логируем ошибку для каждого контроллера
            logger.error(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "controller_id": controller_id,
                "error_type": "API_REQUEST_ERROR",
                "full_response_data": status_data,
                "function": "controllers_status_check"
            }, ensure_ascii=False, default=str))
            
            results.append({
                "ControllerId": controller_id,
                "Status": "Ошибка запроса"
            })
            continue

        # Получаем список ошибок
        faults = status_data.get("ControllerStatus", {}).get("Faults", [])

        # Нормализуем коды к числу и проверяем наличие 10002
        has_fault = False
        try:
            has_fault = any(int(f.get("Code")) == 10002 for f in faults if f.get("Code") is not None)
        except (ValueError, TypeError):
            has_fault = False

        results.append({
            "ControllerId": controller_id,
            "Status": "Нет связи" if has_fault else "На связи"
        })

    return JsonResponse({
        "Success": True,
        "Controllers": results
    })
