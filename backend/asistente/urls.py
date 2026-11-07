from django.urls import path

from .views import ChatAsistenteView, ChatStreamAsistenteView, EstadoAsistenteView

urlpatterns = [
    path('estado/', EstadoAsistenteView.as_view(), name='asistente-estado'),
    path('chat/', ChatAsistenteView.as_view(), name='asistente-chat'),
    path('chat/stream/', ChatStreamAsistenteView.as_view(), name='asistente-chat-stream'),
]
