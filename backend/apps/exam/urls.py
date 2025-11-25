from django.urls import path
from . import views

urlpatterns = [
    path('convert-textbook/', views.convert_textbook, name='convert_textbook'),
    path('compress/', views.compress_text, name='compress_text'),
    path('sentence-summary/', views.get_sentence_summary, name='sentence_summary'),
]

