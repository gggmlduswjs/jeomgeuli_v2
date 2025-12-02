"""
점자 변환 관련 뷰
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import PyPDF2
from utils.braille_converter import text_to_cells
from ..utils.braille_utils import convert_cells_to_brl
from .. import exam_services
from core.decorators import handle_api_errors
from core.exceptions import (
    ValidationException,
    PDFProcessingException,
    BrailleConversionException,
)

BrailleConversionService = exam_services.BrailleConversionService


@csrf_exempt
@handle_api_errors
def convert_textbook(request):
    """
    PDF 교재 → 점자 변환
    POST /api/exam/convert-textbook/
    FormData: { pdf: File }
    """
    if request.method != 'POST':
        raise ValidationException('POST만 지원', user_message='POST 요청만 지원됩니다.')
    
    pdf_file = request.FILES.get('pdf')
    if not pdf_file:
        raise ValidationException('PDF 파일이 필요합니다', user_message='PDF 파일을 업로드해주세요.')
    
    try:
        # PDF → 텍스트 추출
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            raise PDFProcessingException(
                'PDF에서 텍스트를 추출할 수 없습니다',
                user_message='PDF 파일에서 텍스트를 추출할 수 없습니다. 이미지로만 구성된 PDF일 수 있습니다.'
            )
        
        # 텍스트 → 점자 변환
        try:
            braille_cells = text_to_cells(text)
        except Exception as e:
            raise BrailleConversionException(
                f'점자 변환 실패: {str(e)}',
                user_message='점자 변환 중 오류가 발생했습니다.'
            )
        
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
    except PyPDF2.errors.PdfReadError as e:
        raise PDFProcessingException(
            f'PDF 파일 읽기 실패: {str(e)}',
            user_message='PDF 파일이 손상되었거나 읽을 수 없습니다.'
        )


@csrf_exempt
@handle_api_errors
def get_braille_status(request, unit_id):
    """
    단원의 점자 변환 상태 조회
    GET /api/exam/unit/<unit_id>/braille-status/
    """
    if request.method != 'GET':
        raise ValidationException('GET만 지원', user_message='GET 요청만 지원됩니다.')
    
    service = BrailleConversionService()
    status = service.get_braille_status(unit_id)
    
    if not status:
        from core.exceptions import NotFoundException
        raise NotFoundException(
            f'단원 ID {unit_id}를 찾을 수 없습니다',
            user_message='단원을 찾을 수 없습니다.'
        )
    
    return JsonResponse({
        'ok': True,
        **status,
    })

