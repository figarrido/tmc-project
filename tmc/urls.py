from django.urls import path
from .view import TMCView


urlpatterns = [
  path('', TMCView.as_view())
]
