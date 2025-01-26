import json
import random

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# This is mock API endpoints needed for front-end until real ones are implemented


@csrf_exempt
def mock_settings_email(request):
    body = json.loads(request.body.decode("utf-8"))
    if body["email"] == "":
        data = {"status": "error"}
        status = 400
    else:
        data = {"status": "success"}
        status = 200

    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        status=status,
        content_type="application/json; charset=utf-8",
    )


@csrf_exempt
def mock_settings_delete_account(request):
    if random.randint(0, 10) < 5:
        data = {"status": "success"}
        status = 200
    else:
        data = {"status": "error"}
        status = 400

    return HttpResponse(
        json.dumps(data, ensure_ascii=False),
        status=status,
        content_type="application/json; charset=utf-8",
    )
