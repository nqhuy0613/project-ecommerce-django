# assistant/urls.py
from django.urls import path
from .views import chat  # hoặc chat_api nếu bạn đặt tên vậy

urlpatterns = [
    path("chat/", chat, name="chat-api"),  # => /api/chat/
]
