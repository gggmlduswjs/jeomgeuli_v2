from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.get_news, name='get_news'),
]

