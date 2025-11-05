# assistant/views.py
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest


from .chat_engine import process_message

@csrf_exempt
@require_POST
def chat(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    msg = (data.get("message") or "").strip()
    if not msg:
        return HttpResponseBadRequest("Empty message")

    reply = process_message(msg, user=request.user)

    return JsonResponse({"reply": reply})

