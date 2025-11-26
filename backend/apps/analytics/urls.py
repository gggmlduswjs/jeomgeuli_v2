from django.urls import path
from . import views

urlpatterns = [
    path('log/', views.log_analytics, name='log_analytics'),
]

