"""
API 에러 처리 데코레이터
통일된 에러 응답 형식 제공
"""
from functools import wraps
from django.http import JsonResponse
from typing import Callable, Any
import traceback
import logging

from .exceptions import AppException

logger = logging.getLogger(__name__)


def handle_api_errors(func: Callable) -> Callable:
    """
    API 에러 처리 데코레이터
    
    사용법:
        @handle_api_errors
        def my_view(request):
            # view 로직
            pass
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except AppException as e:
            # 애플리케이션 예외는 사용자 친화적 메시지 반환
            logger.warning(f"[{e.error_code}] {e.message}", exc_info=True)
            return JsonResponse(
                e.to_dict(),
                status=e.status_code
            )
        except Exception as e:
            # 예상치 못한 예외는 로그에 기록하고 일반적인 에러 메시지 반환
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            return JsonResponse(
                {
                    'error': '서버 오류가 발생했습니다.',
                    'code': 'INTERNAL_ERROR',
                    'message': str(e) if logger.level <= logging.DEBUG else 'Internal server error',
                },
                status=500
            )
    return wrapper


def handle_api_errors_async(func: Callable) -> Callable:
    """
    비동기 API 에러 처리 데코레이터 (Celery 태스크용)
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppException as e:
            logger.warning(f"[{e.error_code}] {e.message}", exc_info=True)
            raise  # Celery 태스크는 예외를 다시 발생시켜야 함
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=500,
                error_code='INTERNAL_ERROR'
            )
    return wrapper

