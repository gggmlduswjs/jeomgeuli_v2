from django.urls import path
from . import views

urlpatterns = [
    path('today/', views.today_vocab, name='today_vocab'),
    path('learned/', views.mark_vocab_learned, name='mark_vocab_learned'),
]

