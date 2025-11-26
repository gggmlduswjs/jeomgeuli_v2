from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.data_loader import load_json
from .services import PassageAnalysisService
import json

def learn_char(request):
    """자모 학습 데이터 반환"""
    data = load_json("lesson_chars.json", {"items": []})
    return JsonResponse(data if data else {"items": []})

def learn_word(request):
    """단어 학습 데이터 반환"""
    data = load_json("lesson_words.json", {"items": []})
    return JsonResponse(data if data else {"items": []})

def learn_sentence(request):
    """문장 학습 데이터 반환"""
    data = load_json("lesson_sentences.json", {"items": []})
    return JsonResponse(data if data else {"items": []})

def learn_keyword(request):
    """키워드 학습 데이터 반환"""
    data = load_json("lesson_keywords.json", [])
    return JsonResponse({"ok": True, "items": data if isinstance(data, list) else []})

# 필요 시 간단한 헬스체크(프런트 진단용)
def health(request):
    return JsonResponse({"ok": True})


@csrf_exempt
def analyze_passage(request):
    """지문 분석 및 구조화"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        passage = data.get('passage', '').strip()
        
        if not passage:
            return JsonResponse({'error': '지문이 필요합니다'}, status=400)
        
        service = PassageAnalysisService()
        structure = service.analyze_passage(passage)
        
        return JsonResponse({
            'ok': True,
            'structure': structure,
            'original_length': len(passage),
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'분석 중 오류: {str(e)}'}, status=500)


@csrf_exempt
def extract_keywords(request):
    """
    텍스트에서 핵심 키워드 추출
    POST /api/learn/extract-keywords/
    Body: { text: string, max_count?: number }
    """
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'POST만 지원'}, status=405)
        
        data = json.loads(request.body.decode('utf-8'))
        text = data.get('text', '').strip()
        max_count = data.get('max_count', 3)
        
        if not text:
            return JsonResponse({'error': '텍스트가 필요합니다'}, status=400)
        
        service = PassageAnalysisService()
        keywords = service.extract_keywords(text, max_count)
        
        return JsonResponse({
            'ok': True,
            'keywords': keywords,
            'count': len(keywords),
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def extract_passage_key(request):
    """
    지문 핵심 문장 추출
    POST /api/learn/extract-key/
    Body: { passage: string }
    """
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'POST만 지원'}, status=405)
        
        data = json.loads(request.body.decode('utf-8'))
        passage = data.get('passage', '').strip()
        
        if not passage:
            return JsonResponse({'error': '지문이 필요합니다'}, status=400)
        
        service = PassageAnalysisService()
        key_sentence = service.extract_passage_key(passage)
        
        return JsonResponse({
            'ok': True,
            'key_sentence': key_sentence,
            'original_length': len(passage),
            'key_length': len(key_sentence),
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)