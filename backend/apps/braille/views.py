from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from utils.braille_converter import text_to_cells
from .services import BraillePatternService

@csrf_exempt
def braille_convert(request):
    """
    POST {"text": "..."} -> {"cells": [[0|1 x 6], ...]}
    프론트엔드 호환을 위한 점자 변환 API
    """
    try:
        print(f"[braille_convert] Request method: {request.method}")
        print(f"[braille_convert] Request body: {request.body}")
        
        if request.method == "GET":
            text = request.GET.get("text","")
        else:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            text = payload.get("text","")
        
        print(f"[braille_convert] Text to convert: '{text}'")
        cells = text_to_cells(text)
        print(f"[braille_convert] Generated {len(cells)} cells")
        
        return JsonResponse({"cells": cells})
    except Exception as e:
        print(f"[braille_convert] Error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def convert(request):
    """레거시 호환"""
    return braille_convert(request)


@csrf_exempt
def generate_pattern(request):
    """
    상징적 점자 패턴 생성 (3-cell display용)
    POST /api/braille/pattern/
    Body: { type: string, data: any }
    """
    try:
        if request.method == "GET":
            return JsonResponse({'error': 'POST만 지원'}, status=405)
        
        payload = json.loads(request.body.decode("utf-8") or "{}")
        pattern_type = payload.get('type')
        pattern_data = payload.get('data', {})
        
        if not pattern_type:
            return JsonResponse({'error': 'type이 필요합니다'}, status=400)
        
        service = BraillePatternService()
        pattern = service.generate_pattern(pattern_type, pattern_data)
        
        if not service.validate_pattern(pattern):
            return JsonResponse({'error': '패턴 생성 실패'}, status=500)
        
        return JsonResponse({
            'ok': True,
            'pattern': pattern,
            'type': pattern_type,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def convert_formula(request):
    """
    수식 점자 변환
    POST /api/braille/formula/
    Body: { formula: string }
    """
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'POST만 지원'}, status=405)
        
        payload = json.loads(request.body.decode("utf-8") or "{}")
        formula = payload.get('formula', '').strip()
        
        if not formula:
            return JsonResponse({'error': '수식이 필요합니다'}, status=400)
        
        service = BraillePatternService()
        cells = service.convert_formula_to_braille(formula)
        
        return JsonResponse({
            'ok': True,
            'cells': cells,
            'formula': formula,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def extract_formula(request):
    """
    텍스트에서 수식 추출
    POST /api/braille/extract-formula/
    Body: { text: string }
    """
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'POST만 지원'}, status=405)
        
        payload = json.loads(request.body.decode("utf-8") or "{}")
        text = payload.get('text', '').strip()
        
        if not text:
            return JsonResponse({'error': '텍스트가 필요합니다'}, status=400)
        
        service = BraillePatternService()
        formula = service.extract_formula_from_text(text)
        
        return JsonResponse({
            'ok': True,
            'formula': formula,
            'has_formula': formula is not None,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)