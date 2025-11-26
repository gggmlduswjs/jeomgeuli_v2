from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import date
import json
from .services import VocabLearningService, SisaWordService


@csrf_exempt
def today_vocab(request):
    """오늘의 어휘 큐 조회"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET만 지원'}, status=405)
    
    try:
        vocab_service = VocabLearningService()
        sisa_service = SisaWordService()
        
        today = date.today()
        vocab_list = vocab_service.get_today_vocab(today)
        sisa_list = sisa_service.get_today_sisa(today)
        
        return JsonResponse({
            'ok': True,
            'date': today.isoformat(),
            'vocab': vocab_list,
            'sisa': sisa_list,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def mark_vocab_learned(request):
    """어휘 학습 완료 표시 및 SRS 업데이트"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        queue_id = data.get('queue_id')
        grade = data.get('grade', 3)  # 기본값: 3 (쉬움)
        
        if not queue_id:
            return JsonResponse({'error': 'queue_id가 필요합니다'}, status=400)
        
        vocab_service = VocabLearningService()
        success = vocab_service.mark_learned(queue_id, grade)
        
        if success:
            return JsonResponse({
                'ok': True,
                'message': '학습 완료 처리되었습니다',
            })
        else:
            return JsonResponse({'error': '학습 완료 처리 실패'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

