from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import PyPDF2
import io
import os
import json
import re
from pathlib import Path
from utils.braille_converter import text_to_cells
import google.generativeai as genai
from .models import Textbook, Unit, Question, QuestionAttempt, GraphTableItem
from .services import (
    TextbookService, UnitService, QuestionService, GraphAnalysisService,
    ExamSessionService, BrailleConversionService
)


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


# New Jeomgeuli-Suneung endpoints

@csrf_exempt
def list_textbooks(request):
    """교재 목록 조회"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET만 지원'}, status=405)
    
    try:
        service = TextbookService()
        subject = request.GET.get('subject')
        textbooks = service.list_textbooks(subject=subject)
        return JsonResponse({
            'ok': True,
            'textbooks': textbooks,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def list_units(request, textbook_id):
    """교재별 단원 목록 조회"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET만 지원'}, status=405)
    
    try:
        service = UnitService()
        units = service.list_units(textbook_id)
        return JsonResponse({
            'ok': True,
            'units': units,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_unit(request, unit_id):
    """단원 내용 조회"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET만 지원'}, status=405)
    
    try:
        service = UnitService()
        unit = service.get_unit(unit_id)
        if not unit:
            return JsonResponse({'error': '단원을 찾을 수 없습니다'}, status=404)
        return JsonResponse({
            'ok': True,
            'unit': unit,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_question(request, question_id):
    """문제 조회"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET만 지원'}, status=405)
    
    try:
        service = QuestionService()
        question = service.get_question(question_id)
        if not question:
            return JsonResponse({'error': '문제를 찾을 수 없습니다'}, status=404)
        return JsonResponse({
            'ok': True,
            'question': question,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def submit_answer(request):
    """답안 제출"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        question_id = data.get('question_id')
        user_answer = data.get('answer')
        response_time = data.get('response_time')
        
        if not question_id or not user_answer:
            return JsonResponse({'error': 'question_id와 answer가 필요합니다'}, status=400)
        
        service = QuestionService()
        result = service.submit_answer(question_id, user_answer, response_time)
        
        return JsonResponse({
            'ok': True,
            **result,
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def start_exam(request):
    """시험 시작"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
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
        return JsonResponse({'error': '잘못된 JSON 형식입니다'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def analyze_graph(request):
    """그래프/도표 분석 및 패턴 추출"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
    try:
        # TODO: 실제 구현 - Vision API로 그래프 분석
        image_file = request.FILES.get('image')
        title = request.POST.get('title', '')
        
        if not image_file:
            return JsonResponse({'error': '이미지 파일이 필요합니다'}, status=400)
        
        # 이미지 데이터 읽기
        image_data = image_file.read()
        
        service = GraphAnalysisService()
        result = service.analyze_graph(image_data, title)
        
        return JsonResponse({
            'ok': True,
            **result,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def extract_textbook_info(filename: str) -> dict:
    """
    파일명에서 교재 정보 추출
    예: "수능특강_국어_2024.pdf" → {title: "수능특강 국어", subject: "국어", year: 2024}
    """
    # 확장자 제거
    name = filename.replace('.pdf', '').replace('.PDF', '')
    
    # 패턴 매칭
    patterns = [
        r'(.+?)_(\w+)_(\d{4})',  # 수능특강_국어_2024
        r'(.+?)\s+(\w+)\s+(\d{4})',  # 수능특강 국어 2024
        r'(.+?)_(\d{4})',  # 수능특강_2024
        r'(.+?)\s+(\d{4})',  # 수능특강 2024
    ]
    
    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            if len(match.groups()) == 3:
                title, subject, year = match.groups()
                return {
                    'title': f"{title} {subject}",
                    'subject': subject,
                    'year': int(year),
                    'publisher': 'EBS'  # 기본값
                }
            elif len(match.groups()) == 2:
                title, year = match.groups()
                # year가 숫자인지 확인
                if year.isdigit():
                    return {
                        'title': title,
                        'subject': '',
                        'year': int(year),
                        'publisher': 'EBS'
                    }
                else:
                    # year가 과목일 수도 있음
                    return {
                        'title': f"{title} {year}",
                        'subject': year,
                        'year': None,
                        'publisher': 'EBS'
                    }
    
    # 매칭 실패 시 파일명을 그대로 사용
    return {
        'title': name,
        'subject': '',
        'year': None,
        'publisher': 'EBS'
    }


def extract_units_from_text(text: str) -> list:
    """
    텍스트에서 단원 정보 추출 (간단한 패턴 매칭)
    """
    units = []
    
    # 간단한 패턴 매칭: "1단원", "제1장", "Chapter 1" 등
    unit_patterns = [
        r'(\d+)단원[:\s]+(.+?)(?=\d+단원|$|제\d+장|Chapter\s+\d+)',
        r'제(\d+)장[:\s]+(.+?)(?=제\d+장|$|\d+단원|Chapter\s+\d+)',
        r'Chapter\s+(\d+)[:\s]+(.+?)(?=Chapter\s+\d+|$|\d+단원|제\d+장)',
        r'제(\d+)과[:\s]+(.+?)(?=제\d+과|$|\d+단원)',
    ]
    
    for pattern in unit_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            order = int(match.group(1))
            content = match.group(2).strip()[:2000]  # 최대 2000자
            if content and len(content) > 50:  # 최소 50자 이상
                units.append({
                    'order': order,
                    'title': f"{order}단원",
                    'content': content
                })
    
    # 중복 제거 (order 기준)
    seen_orders = set()
    unique_units = []
    for unit in units:
        if unit['order'] not in seen_orders:
            seen_orders.add(unit['order'])
            unique_units.append(unit)
    units = sorted(unique_units, key=lambda x: x['order'])
    
    return units


@csrf_exempt
def upload_pdf(request):
    """
    PDF 업로드 → 텍스트 추출 → 단원 분리 → Textbook/Unit 생성 → 백그라운드 점자 변환
    POST /api/exam/textbook/upload-pdf/
    FormData: { pdf: File }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST만 지원'}, status=405)
    
    pdf_file = request.FILES.get('pdf')
    if not pdf_file:
        return JsonResponse({'error': 'PDF 파일이 필요합니다'}, status=400)
    
    try:
        # PDF 텍스트 추출
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                print(f"[upload_pdf] 페이지 추출 실패: {e}")
                continue
        
        if not text.strip():
            return JsonResponse({'error': 'PDF에서 텍스트를 추출할 수 없습니다'}, status=400)
        
        # 교재 정보 추출
        textbook_info = extract_textbook_info(pdf_file.name)
        
        # 단원 추출
        units_data = extract_units_from_text(text)
        
        if not units_data:
            # 단원을 찾지 못한 경우 전체를 하나의 단원으로
            units_data = [{
                'order': 1,
                'title': '전체',
                'content': text[:5000]  # 처음 5000자
            }]
        
        # Textbook 생성 또는 조회
        textbook, created = Textbook.objects.get_or_create(
            title=textbook_info['title'],
            year=textbook_info['year'],
            defaults={
                'publisher': textbook_info['publisher'],
                'subject': textbook_info['subject'],
            }
        )
        
        if not created:
            # 이미 존재하는 교재인 경우
            return JsonResponse({
                'ok': True,
                'textbook_id': textbook.id,
                'unit_count': 0,
                'message': '이미 존재하는 교재입니다.',
                'existing': True,
            })
        
        # Unit 생성
        unit_ids = []
        for unit_data in units_data:
            unit = Unit.objects.create(
                textbook=textbook,
                title=unit_data['title'],
                order=unit_data['order'],
                content=unit_data['content']
            )
            unit_ids.append(unit.id)
        
        # 백그라운드 점자 변환 시작 (동기적으로 실행 - 나중에 Celery로 변경 가능)
        conversion_service = BrailleConversionService()
        for unit_id in unit_ids:
            try:
                # 비동기로 실행하려면 여기서 Celery 태스크를 호출
                # 현재는 동기적으로 실행 (나중에 개선)
                conversion_service.convert_unit_to_braille(unit_id, textbook.subject)
            except Exception as e:
                print(f"[upload_pdf] 점자 변환 실패 (unit_id={unit_id}): {e}")
                # 변환 실패해도 계속 진행
        
        return JsonResponse({
            'ok': True,
            'textbook_id': textbook.id,
            'unit_count': len(unit_ids),
            'message': 'PDF 업로드 및 점자 변환 완료',
        })
        
    except PyPDF2.errors.PdfReadError:
        return JsonResponse({'error': 'PDF 파일이 손상되었거나 읽을 수 없습니다'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'처리 중 오류: {str(e)}'}, status=500)


@csrf_exempt
def get_braille_status(request, unit_id):
    """
    단원의 점자 변환 상태 조회
    GET /api/exam/unit/<unit_id>/braille-status/
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'GET만 지원'}, status=405)
    
    try:
        service = BrailleConversionService()
        status = service.get_braille_status(unit_id)
        
        if not status:
            return JsonResponse({'error': '단원을 찾을 수 없습니다'}, status=404)
        
        return JsonResponse({
            'ok': True,
            **status,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

