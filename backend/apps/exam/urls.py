from django.urls import path
from . import views

urlpatterns = [
    # Legacy endpoints
    path('convert-textbook/', views.convert_textbook, name='convert_textbook'),
    path('compress/', views.compress_text, name='compress_text'),
    path('sentence-summary/', views.get_sentence_summary, name='sentence_summary'),
    
    # New Jeomgeuli-Suneung endpoints
    path('textbook/', views.list_textbooks, name='list_textbooks'),
    path('textbook/upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('textbook/<int:textbook_id>/units/', views.list_units, name='list_units'),
    path('unit/<int:unit_id>/', views.get_unit, name='get_unit'),
    path('unit/<int:unit_id>/braille-status/', views.get_braille_status, name='get_braille_status'),
    path('question/<int:question_id>/', views.get_question, name='get_question'),
    path('submit/', views.submit_answer, name='submit_answer'),
    path('start/', views.start_exam, name='start_exam'),
    path('graph-analyze/', views.analyze_graph, name='analyze_graph'),
]

