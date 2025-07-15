import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from tools.toolkit.sdp_lib.potok_controller.condition.gen_condition import ConditionMaker


@csrf_exempt
def dt_potok2_api(request):
    if not request.method == "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)
    try:
        # Предполагаем, что данные передаются в формате JSON
        data = json.loads(request.body)
        raw_conditions = data["user_condition_string"]
        func_name = data["func_name"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Неверный формат данных."}, status=400)

    maker = ConditionMaker(raw_conditions, func_name)
    return JsonResponse(maker.process_data_and_build_result_as_dict())



