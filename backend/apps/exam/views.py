from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import PyPDF2
import io
import os
import json
from utils.braille_converter import text_to_cells
import google.generativeai as genai


def convert_cells_to_brl(cells):
    """
    점자 셀 배열을 .brl 형식 텍스트로 변환 (간단한 버전)
    실제로는 점자 유니코드 매핑이 필요하지만, 여기서는 기본 구현만 제공
    """
    # 점자 유니코드 기본 매핑 (일부만 구현, 실제로는 전체 매핑 필요)
    braille_unicode_map = {
        (1, 0, 0, 0, 0, 0): '⠁', (1, 1, 0, 0, 0, 0): '⠃', (1, 0, 0, 1, 0, 0): '⠉',
        (1, 0, 0, 1, 1, 0): '⠙', (1, 0, 0, 0, 1, 0): '⠑', (1, 1, 0, 1, 0, 0): '⠋',
        (1, 1, 0, 1, 1, 0): '⠛', (1, 1, 0, 0, 1, 0): '⠓', (0, 1, 0, 1, 0, 0): '⠊',
        (0, 1, 0, 1, 1, 0): '⠚', (1, 0, 1, 0, 0, 0): '⠅', (1, 0, 1, 1, 0, 0): '⠇',
        (1, 0, 0, 0, 0, 1): '⠍', (1, 0, 1, 0, 1, 0): '⠝', (1, 0, 1, 1, 1, 0): '⠕',
        (1, 0, 0, 0, 1, 1): '⠏', (1, 1, 1, 0, 0, 0): '⠟', (1, 1, 1, 0, 1, 0): '⠗',
        (1, 1, 0, 0, 0, 1): '⠎', (0, 1, 1, 1, 0, 0): '⠞', (1, 1, 1, 1, 0, 0): '⠥',
        (1, 1, 1, 1, 1, 0): '⠧', (1, 0, 1, 1, 0, 1): '⠺', (0, 1, 0, 1, 1, 1): '⠭',
        (1, 1, 1, 1, 0, 1): '⠽', (1, 0, 0, 1, 0, 1): '⠵', (0, 0, 0, 0, 0, 0): ' ',
    }
    
    result = []
    for cell in cells:
        key = tuple(cell)
        result.append(braille_unicode_map.get(key, ' '))
    return ''.join(result)


@csrf_exempt
def convert_textbook(request):
    """
    PDF 교재 → 점자 변환
    POST /api/exam/convert-textbook/
    FormData: { pdf: File }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
    pdf_file = request.FILES.get('pdf')
    if not pdf_file:
        return JsonResponse({'error': 'PDF 파일이 필요합니다'}, status=400)
    
    try:
        # PDF → 텍스트 추출
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            return JsonResponse({'error': 'PDF에서 텍스트를 추출할 수 없습니다'}, status=400)
        
        # 텍스트 → 점자 변환
        braille_cells = text_to_cells(text)
        
        # 점자 텍스트 생성 (선택적, .brl 형식)
        braille_text = convert_cells_to_brl(braille_cells)
        
        return JsonResponse({
            'braille_cells': braille_cells,
            'braille_text': braille_text,
            'original_text': text[:1000],  # 처음 1000자만 반환 (전체는 너무 큼)
            'text_length': len(text),
            'cells_count': len(braille_cells),
            'pages_count': len(pdf_reader.pages),
        })
    except PyPDF2.errors.PdfReadError:
        return JsonResponse({'error': 'PDF 파일이 손상되었거나 읽을 수 없습니다'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'변환 중 오류: {str(e)}'}, status=500)


@csrf_exempt
def compress_text(request):
    """
    텍스트 압축 (언어영역 지문용)
    POST /api/exam/compress/
    Body: { text: string, mode: 'compressed' | 'outline', targetRatio: number }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    
    text = data.get('text', '').strip()
    mode = data.get('mode', 'compressed')  # compressed, outline
    target_ratio = data.get('targetRatio', 0.3)  # 30%
    
    if not text:
        return JsonResponse({'error': '텍스트가 필요합니다'}, status=400)
    
    if mode not in ['compressed', 'outline']:
        mode = 'compressed'
    
    try:
        # Gemini API 사용
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'AI API 키가 설정되지 않았습니다'}, status=500)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
다음 수능 언어영역 지문을 {mode} 모드로 압축해주세요.
원문 길이의 {target_ratio * 100}% 수준으로 줄여주세요.

모드별 요구사항:
- compressed: 핵심 문장만 재구성하여 원문의 의미를 유지하되 길이를 줄입니다.
- outline: 줄거리 기반 순서 요약으로 등장인물/사건 중심으로 요약합니다.

원문:
{text}

압축된 텍스트만 반환해주세요. 설명이나 추가 문구 없이 압축된 텍스트만 출력해주세요.
"""
        
        response = model.generate_content(prompt)
        compressed = response.text.strip()
        
        return JsonResponse({
            'compressed_text': compressed,
            'original_length': len(text),
            'compressed_length': len(compressed),
            'compression_ratio': len(compressed) / len(text) if text else 0,
            'mode': mode,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'압축 중 오류: {str(e)}'}, status=500)


@csrf_exempt
def get_sentence_summary(request):
    """
    문장 요약 (문장 반복 모드용)
    POST /api/exam/sentence-summary/
    Body: { sentence: string }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    
    sentence = data.get('sentence', '').strip()
    
    if not sentence:
        return JsonResponse({'error': '문장이 필요합니다'}, status=400)
    
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'AI API 키가 설정되지 않았습니다'}, status=500)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
다음 문장을 한 문장으로 요약해주세요. 핵심 의미만 간단히 설명해주세요.

문장: {sentence}

요약:
"""
        
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        return JsonResponse({
            'summary': summary,
            'original': sentence,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'요약 중 오류: {str(e)}'}, status=500)

