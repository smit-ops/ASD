from django.urls import path
from . import views

urlpatterns = [
    path('', views.fruit_recognition_view, name='fruit_ai'),
]