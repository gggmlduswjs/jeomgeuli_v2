import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime
from .models import ReviewItem, ReviewAttempt
from .srs import calculate_next_review
from .repositories import ReviewItemRepository

@csrf_exempt
@require_http_methods(["POST"])
def enqueue_review(request):
    """복습 항목 추가"""
    try:
        data = json.loads(request.body)
        
        # 필수 필드 검증
        required_fields = ['type', 'content']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # 타입 검증
        valid_types = ['char', 'word', 'sentence', 'braille']
        if data['type'] not in valid_types:
            return JsonResponse({
                'error': f'Invalid type. Must be one of: {valid_types}'
            }, status=400)
        
        # ReviewItem 생성 (Repository 사용)
        repo = ReviewItemRepository()
        review_item = repo.create(
            type=data['type'],
            source=data.get('source', 'manual'),
            content=data['content'],
            next_due=timezone.now()  # 즉시 복습 가능
        )
        
        return JsonResponse({
            'success': True,
            'id': review_item.id,
            'message': f'Review item added: {review_item.get_content_display()}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def next_reviews(request):
    """다음 복습할 항목들 가져오기"""
    try:
        count = int(request.GET.get('n', 10))
        count = min(count, 50)  # 최대 50개로 제한
        
        # Repository 사용
        repo = ReviewItemRepository()
        due_items = repo.get_due_items(count)
        
        items = []
        for item in due_items:
            items.append({
                'id': item.id,
                'type': item.type,
                'content': item.content,
                'display': item.get_content_display(),
                'source': item.source,
                'ease_factor': item.ease_factor,
                'interval': item.interval,
                'repetitions': item.repetitions,
                'next_due': item.next_due.isoformat(),
                'created_at': item.created_at.isoformat(),
            })
        
        return JsonResponse({
            'items': items,
            'count': len(items),
            'total_due': repo.get_all_due_count()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def grade_review(request, item_id):
    """복습 결과 제출 (정오답 및 다음 복습 시간 계산)"""
    try:
        data = json.loads(request.body)
        grade = data.get('grade')
        response_time = data.get('response_time')
        
        if grade is None:
            return JsonResponse({'error': 'Grade is required'}, status=400)
        
        if not (0 <= grade <= 4):
            return JsonResponse({'error': 'Grade must be between 0 and 4'}, status=400)
        
        # Repository 사용
        repo = ReviewItemRepository()
        review_item = repo.get_by_id(item_id)
        if not review_item:
            return JsonResponse({'error': 'Review item not found'}, status=404)
        
        # SRS 계산으로 다음 복습 시간 업데이트
        updates = calculate_next_review(review_item, grade)
        
        # ReviewItem 업데이트 (Repository 사용)
        repo.update(review_item, **updates)
        
        # 시도 기록 생성
        ReviewAttempt.objects.create(
            review_item=review_item,
            grade=grade,
            response_time=response_time
        )
        
        return JsonResponse({
            'success': True,
            'next_due': review_item.next_due.isoformat(),
            'ease_factor': review_item.ease_factor,
            'interval': review_item.interval,
            'repetitions': review_item.repetitions,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_review(request):
    """간단한 복습 항목 추가 (오답 큐용)"""
    try:
        data = json.loads(request.body)
        
        # 간단한 응답
        return JsonResponse({
            "ok": True, 
            "saved": data,
            "message": "오답이 복습 큐에 추가되었습니다."
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 파일 기반 복습 시스템 함수들
@csrf_exempt
def review_save(request):
    """
    POST {"kind": "wrong|keyword", "payload": {...}} -> {"ok": true}
    데이터베이스를 사용하여 복습 항목 저장
    """
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
        kind = body.get("kind", "wrong")
        payload = body.get("payload", {})
        
        print(f"[review_save] Received request: kind={kind}, payload={payload}")
        
        # payload에서 타입과 내용 추출
        item_type = payload.get("type", "word")
        content_text = payload.get("content") or payload.get("text") or payload.get("word") or ""
        
        print(f"[review_save] Extracted: type={item_type}, content_text={content_text}")
        
        if not content_text:
            print("[review_save] Error: content is required")
            return JsonResponse({"error": "content is required"}, status=400)
        
        # ReviewItem 생성
        # content 필드 구조: get_content_display()에서 사용할 수 있도록 구성
        content_dict = {
            "text": content_text,
            "word": payload.get("word") or content_text,  # get_content_display()에서 사용
            "content": content_text,
            "original_payload": payload
        }
        
        # Repository 사용
        repo = ReviewItemRepository()
        review_item = repo.create(
            type=item_type if item_type in ['char', 'word', 'sentence', 'braille'] else 'word',
            source='quiz_wrong' if kind == 'wrong' else 'learning_queue',
            content=content_dict,
            next_due=timezone.now()  # 즉시 복습 가능
        )
        
        print(f"[review_save] Created ReviewItem: id={review_item.id}, type={review_item.type}, content={review_item.get_content_display()}")
        
        return JsonResponse({"ok": True, "id": review_item.id})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def review_enqueue(request):
    """POST {"kind": "wrong|keyword", "payload": {...}} -> {"ok": true}"""
    return review_save(request)

def review_list(request):
    """
    GET -> {"items": [...]}
    데이터베이스에서 복습 항목 목록 반환
    """
    try:
        # 복습 시간이 된 항목들 가져오기 (기본값: 최대 50개)
        count = int(request.GET.get('n', 50))
        count = min(count, 100)  # 최대 100개로 제한
        
        # Repository 사용
        repo = ReviewItemRepository()
        
        # 전체 항목 수 확인 (디버깅)
        # Note: Repository에 count 메서드가 없으므로 직접 조회 (필요시 추가 가능)
        from .models import ReviewItem
        total_count = ReviewItem.objects.count()
        print(f"[review_list] Total ReviewItems in DB: {total_count}")
        
        due_items = repo.get_due_items(count)
        print(f"[review_list] Due items count: {len(due_items)}")
        
        items = []
        for item in due_items:
            # payload 구성
            payload = {
                "type": item.type,
                "content": item.get_content_display(),
                "text": item.get_content_display(),
            }
            # item.content가 딕셔너리면 추가 필드 병합
            if isinstance(item.content, dict):
                payload.update(item.content)
            
            items.append({
                "id": item.id,
                "kind": "wrong" if item.source == "quiz_wrong" else "keyword",
                "payload": payload,
                "timestamp": item.created_at.isoformat(),
            })
        
        print(f"[review_list] Returning {len(items)} items")
        return JsonResponse({"items": items})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def review_add(request):
    """레거시: review_save와 동일"""
    return review_save(request)

def review_today(request):
    """레거시: review_list와 동일"""
    return review_list(request)
