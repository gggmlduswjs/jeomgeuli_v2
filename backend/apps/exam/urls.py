from django.urls import path
from .views import (
    convert_textbook,
    compress_text,
    get_sentence_summary,
    list_textbooks,
    upload_pdf,
    list_units,
    get_unit,
    get_question,
    submit_answer,
    start_exam,
    analyze_graph,
    get_braille_status,
)

urlpatterns = [
    # Legacy endpoints
    path('convert-textbook/', convert_textbook, name='convert_textbook'),
    path('compress/', compress_text, name='compress_text'),
    path('sentence-summary/', get_sentence_summary, name='sentence_summary'),
    
    # New Jeomgeuli-Suneung endpoints
    path('textbook/', list_textbooks, name='list_textbooks'),
    path('textbook/upload-pdf/', upload_pdf, name='upload_pdf'),
    path('textbook/<int:textbook_id>/units/', list_units, name='list_units'),
    path('unit/<int:unit_id>/', get_unit, name='get_unit'),
    path('unit/<int:unit_id>/braille-status/', get_braille_status, name='get_braille_status'),
    path('question/<int:question_id>/', get_question, name='get_question'),
    path('submit/', submit_answer, name='submit_answer'),
    path('start/', start_exam, name='start_exam'),
    path('graph-analyze/', analyze_graph, name='analyze_graph'),
]

