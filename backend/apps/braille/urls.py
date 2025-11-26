from django.urls import path
from . import views

urlpatterns = [
    path("encode/", views.braille_convert, name="braille_encode"),
    path("convert/", views.braille_convert, name="braille_convert"),  # legacy compatibility
    path("", views.braille_convert, name="braille_convert_root"),  # /api/convert/ 호환
    path("pattern/", views.generate_pattern, name="generate_pattern"),  # New Jeomgeuli-Suneung
    path("formula/", views.convert_formula, name="convert_formula"),  # 수식 점자 변환
    path("extract-formula/", views.extract_formula, name="extract_formula"),  # 수식 추출
]