from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    # 표준 경로 (복수형)
    path("chars/",     views.learn_char,     name="learn_chars"),
    path("words/",     views.learn_word,     name="learn_words"),
    path("sentences/", views.learn_sentence, name="learn_sentences"),
    path("keywords/",  views.learn_keyword,  name="learn_keywords"),
    
    # 과거 별칭 유지 (단수형)
    path("char/",      views.learn_char,     name="learn_char"),
    path("word/",      views.learn_word,     name="learn_word"),
    path("sentence/",  views.learn_sentence, name="learn_sentence"),
    path("keyword/",   views.learn_keyword,  name="learn_keyword"),
    
    # New Jeomgeuli-Suneung endpoints
    path("passage-analyze/", views.analyze_passage, name="analyze_passage"),
    path("extract-keywords/", views.extract_keywords, name="extract_keywords"),  # 핵심 키워드 추출
    path("extract-key/", views.extract_passage_key, name="extract_passage_key"),  # 핵심 문장 추출
]