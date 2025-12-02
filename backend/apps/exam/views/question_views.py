"""
문제 관련 뷰
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .. import exam_services
from core.decorators import handle_api_errors
from core.exceptions import ValidationException, NotFoundException

QuestionService = exam_services.QuestionService


@csrf_exempt
@handle_api_errors
def get_question(request, question_id):
    """문제 조회"""
    if request.method != 'GET':
        raise ValidationException('GET만 지원', user_message='GET 요청만 지원됩니다.')
    
    service = QuestionService()
    question = service.get_question(question_id)
    if not question:
        raise NotFoundException(f'문제 ID {question_id}를 찾을 수 없습니다', user_message='문제를 찾을 수 없습니다.')
    
    return JsonResponse({
        'ok': True,
        'question': question,
    })


@csrf_exempt
@handle_api_errors
def submit_answer(request):
    """답안 제출"""
    if request.method != 'POST':
        raise ValidationException('POST만 지원', user_message='POST 요청만 지원됩니다.')
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        question_id = data.get('question_id')
        user_answer = data.get('answer')
        response_time = data.get('response_time')
        
        if not question_id or not user_answer:
            raise ValidationException(
                'question_id와 answer가 필요합니다',
                user_message='문제 ID와 답안을 입력해주세요.'
            )
        
        service = QuestionService()
        result = service.submit_answer(question_id, user_answer, response_time)
        
        return JsonResponse({
            'ok': True,
            **result,
        })
    except json.JSONDecodeError:
        raise ValidationException(
            '잘못된 JSON 형식입니다',
            user_message='요청 데이터 형식이 올바르지 않습니다.'
        )
    except ValueError as e:
        raise NotFoundException(str(e), user_message='문제를 찾을 수 없습니다.')

