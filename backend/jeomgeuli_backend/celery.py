"""
Celery 설정
비동기 작업 처리
"""
import os
from celery import Celery
from django.conf import settings

# Django 설정 모듈 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeomgeuli_backend.settings')

# Celery 앱 생성
app = Celery('jeomgeuli_backend')

# Django 설정에서 Celery 설정 로드
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱에서 태스크 자동 발견
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """디버그 태스크"""
    print(f'Request: {self.request!r}')

