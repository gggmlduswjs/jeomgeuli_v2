"""
시험 관련 뷰
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .. import exam_services
from core.decorators import handle_api_errors
from core.exceptions import ValidationException

ExamSessionService = exam_services.ExamSessionService


@csrf_exempt
@handle_api_errors
def start_exam(request):
    """시험 시작"""
    if request.method != 'POST':
        raise ValidationException('POST만 지원', user_message='POST 요청만 지원됩니다.')
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        total_questions = data.get('total_questions', 0)
        
        # ExamSessionService를 사용하여 시험 세션 생성
        service = ExamSessionService()
        result = service.start_exam(total_questions=total_questions)
        
        return JsonResponse({
            'ok': True,
            'exam_id': result['exam_id'],
            'started_at': result['started_at'],
            'total_questions': result['total_questions'],
            'status': result['status'],
        })
    except json.JSONDecodeError:
        raise ValidationException(
            '잘못된 JSON 형식입니다',
            user_message='요청 데이터 형식이 올바르지 않습니다.'
        )

