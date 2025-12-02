"""
Views 모듈
분리된 뷰들을 통합
"""
from .textbook_views import (
    list_textbooks,
    list_units,
    get_unit,
    upload_pdf,
)
from .question_views import (
    get_question,
    submit_answer,
)
from .braille_views import (
    convert_textbook,
    get_braille_status,
)
from .graph_views import (
    analyze_graph,
)
from .exam_views import (
    start_exam,
)
from .text_processing_views import (
    compress_text,
    get_sentence_summary,
)

__all__ = [
    'list_textbooks',
    'list_units',
    'get_unit',
    'upload_pdf',
    'get_question',
    'submit_answer',
    'convert_textbook',
    'get_braille_status',
    'analyze_graph',
    'start_exam',
    'compress_text',
    'get_sentence_summary',
]

