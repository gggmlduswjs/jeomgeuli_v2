"""
Django 프로젝트 초기화
Celery 앱 등록 (선택적)
"""
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery가 설치되지 않은 경우
    celery_app = None
    __all__ = ()

