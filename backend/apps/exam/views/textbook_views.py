"""
교재 관련 뷰
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .. import exam_services
from core.decorators import handle_api_errors
from core.exceptions import ValidationException, NotFoundException
from ..services.pdf_processing_service import PDFProcessingService

TextbookService = exam_services.TextbookService
UnitService = exam_services.UnitService


@csrf_exempt
@handle_api_errors
def list_textbooks(request):
    """교재 목록 조회"""
    if request.method != 'GET':
        raise ValidationException('GET만 지원', user_message='GET 요청만 지원됩니다.')
    
    service = TextbookService()
    subject = request.GET.get('subject')
    textbooks = service.list_textbooks(subject=subject)
    return JsonResponse({
        'ok': True,
        'textbooks': textbooks,
    })


@csrf_exempt
@handle_api_errors
def list_units(request, textbook_id):
    """교재별 단원 목록 조회"""
    if request.method != 'GET':
        raise ValidationException('GET만 지원', user_message='GET 요청만 지원됩니다.')
    
    service = UnitService()
    units = service.list_units(textbook_id)
    return JsonResponse({
        'ok': True,
        'units': units,
    })


@csrf_exempt
@handle_api_errors
def get_unit(request, unit_id):
    """단원 내용 조회"""
    if request.method != 'GET':
        raise ValidationException('GET만 지원', user_message='GET 요청만 지원됩니다.')
    
    service = UnitService()
    unit = service.get_unit(unit_id)
    if not unit:
        raise NotFoundException(f'단원 ID {unit_id}를 찾을 수 없습니다', user_message='단원을 찾을 수 없습니다.')
    
    return JsonResponse({
        'ok': True,
        'unit': unit,
    })


@csrf_exempt
@handle_api_errors
def upload_pdf(request):
    """
    PDF 업로드 → 텍스트 추출 → 단원 분리 → Textbook/Unit 생성 → 백그라운드 점자 변환
    POST /api/exam/textbook/upload-pdf/
    FormData: { pdf: File }
    """
    if request.method != 'POST':
        raise ValidationException('POST만 지원', user_message='POST 요청만 지원됩니다.')
    
    pdf_file = request.FILES.get('pdf')
    if not pdf_file:
        raise ValidationException('PDF 파일이 필요합니다', user_message='PDF 파일을 업로드해주세요.')
    
    # PDF 처리 서비스 사용
    service = PDFProcessingService()
    result = service.process_pdf(pdf_file, async_mode=True)
    
    return JsonResponse(result)

