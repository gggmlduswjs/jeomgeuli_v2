from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .repositories import (
    BrailleSpeedLogRepository, WrongAnswerPatternRepository, TimingLogRepository
)


@csrf_exempt
def log_analytics(request):
    """분석 데이터 로깅"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        log_type = data.get('type')  # 'speed', 'wrong_answer', 'timing'
        
        if log_type == 'speed':
            repo = BrailleSpeedLogRepository()
            repo.create(
                pattern_count=data.get('pattern_count', 0),
                time_seconds=data.get('time_seconds', 0),
                speed_per_minute=data.get('speed_per_minute', 0),
                accuracy=data.get('accuracy'),
            )
        
        elif log_type == 'wrong_answer':
            repo = WrongAnswerPatternRepository()
            repo.create(
                question_id=data.get('question_id'),
                wrong_answer=data.get('wrong_answer'),
                correct_answer=data.get('correct_answer'),
                pattern_type=data.get('pattern_type', 'user_mistake'),
            )
        
        elif log_type == 'timing':
            repo = TimingLogRepository()
            repo.create(
                exam_type=data.get('exam_type', ''),
                subject=data.get('subject', ''),
                allocated_time=data.get('allocated_time', 0),
                used_time=data.get('used_time', 0),
                remaining_time=data.get('remaining_time', 0),
            )
        
        else:
            return JsonResponse({'error': f'알 수 없는 로그 타입: {log_type}'}, status=400)
        
        return JsonResponse({
            'ok': True,
            'logged': True,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

