"""
Celery 비동기 태스크
PDF 처리, 점자 변환, 그래프 분석 등
"""
from celery import shared_task
from typing import Dict, Optional
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

from .models import PDFDocument, Textbook, Unit, BrailleContent, BrailleChunk
from .parsers import PDFParser, OCRAnalyzer
from . import exam_services
from .services.graph_cv_analyzer import GraphCVAnalyzer
BrailleConversionService = exam_services.BrailleConversionService
GraphAnalysisService = exam_services.GraphAnalysisService
from core.exceptions import PDFProcessingException, BrailleConversionException


@shared_task(bind=True, max_retries=3)
def process_pdf_async(self, pdf_document_id: int) -> Dict:
    """
    PDF 업로드 및 분석 비동기 처리
    
    Args:
        pdf_document_id: PDFDocument ID
    
    Returns:
        {
            'document_id': pdf_document_id,
            'status': 'completed' | 'failed',
            'textbook_id': textbook_id,
            'unit_count': unit_count
        }
    """
    try:
        pdf_doc = PDFDocument.objects.get(id=pdf_document_id)
        pdf_doc.status = 'parsing'
        pdf_doc.progress = 10
        pdf_doc.save()
        
        # PDF 파일 읽기
        if not pdf_doc.file_path or not os.path.exists(pdf_doc.file_path):
            raise PDFProcessingException(f'PDF 파일을 찾을 수 없습니다: {pdf_doc.file_path}')
        
        with open(pdf_doc.file_path, 'rb') as f:
            # PDF 파서로 텍스트 추출
            parser = PDFParser()
            text = parser.extract_text(f)
            
            pdf_doc.extracted_text = text
            pdf_doc.progress = 30
            pdf_doc.save()
            
            # 레이아웃 분석
            f.seek(0)
            layout = parser.analyze_layout(f)
            pdf_doc.layout_analysis = layout
            
            # 이미지 영역 감지
            f.seek(0)
            image_areas = parser.detect_image_areas(f)
            pdf_doc.image_areas = image_areas
            
            pdf_doc.progress = 50
            pdf_doc.save()
            
            # OCR 처리 (이미지 영역이 있는 경우)
            if image_areas:
                ocr_analyzer = OCRAnalyzer()
                ocr_results = {}
                for img_area in image_areas[:5]:  # 최대 5개만 처리
                    try:
                        # 이미지 데이터 추출 (실제 구현 필요)
                        # 여기서는 기본 구조만 제공
                        pass
                    except Exception as e:
                        print(f"[process_pdf_async] OCR 실패: {e}")
                
                pdf_doc.ocr_results = ocr_results
                pdf_doc.progress = 60
                pdf_doc.save()
        
        # 단원 추출 및 Textbook/Unit 생성
        from .utils.text_extractor import extract_textbook_info, extract_units_from_text
        
        textbook_info = extract_textbook_info(pdf_doc.original_filename)
        units_data = extract_units_from_text(text)
        
        if not units_data:
            units_data = [{
                'order': 1,
                'title': '전체',
                'content': text[:5000]
            }]
        
        # Textbook 생성
        textbook, created = Textbook.objects.get_or_create(
            title=textbook_info['title'],
            year=textbook_info['year'],
            defaults={
                'publisher': textbook_info['publisher'],
                'subject': textbook_info['subject'],
            }
        )
        
        pdf_doc.textbook = textbook
        pdf_doc.progress = 70
        pdf_doc.save()
        
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
        
        pdf_doc.progress = 80
        pdf_doc.status = 'analyzing'
        pdf_doc.save()
        
        # 점자 변환 태스크 큐에 추가 (비동기)
        for unit_id in unit_ids:
            convert_braille_async.delay(unit_id, textbook.subject)
        
        pdf_doc.progress = 100
        pdf_doc.status = 'completed'
        pdf_doc.save()
        
        return {
            'document_id': pdf_document_id,
            'status': 'completed',
            'textbook_id': textbook.id,
            'unit_count': len(unit_ids)
        }
        
    except Exception as e:
        pdf_doc = PDFDocument.objects.get(id=pdf_document_id)
        pdf_doc.status = 'failed'
        pdf_doc.error_message = str(e)
        pdf_doc.save()
        
        # 재시도
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        
        return {
            'document_id': pdf_document_id,
            'status': 'failed',
            'error': str(e)
        }


@shared_task(bind=True, max_retries=2)
def convert_braille_async(self, unit_id: int, subject: str = None) -> Dict:
    """
    점자 변환 비동기 처리
    
    Args:
        unit_id: Unit ID
        subject: 과목
    
    Returns:
        {
            'unit_id': unit_id,
            'status': 'completed' | 'failed',
            'chunk_count': chunk_count
        }
    """
    try:
        from . import exam_services
        BrailleConversionService = exam_services.BrailleConversionService
        
        # 서비스 사용 (중복 로직 제거)
        service = BrailleConversionService()
        result = service.convert_with_semantic_chunking(
            unit_id=unit_id,
            subject=subject,
            create_chunks=True
        )
        
        if result['status'] == 'completed':
            braille_content = BrailleContent.objects.filter(unit_id=unit_id).first()
            chunk_count = 0
            if braille_content:
                chunk_count = BrailleChunk.objects.filter(content=braille_content).count()
            
            return {
                'unit_id': unit_id,
                'status': 'completed',
                'chunk_count': chunk_count or len(result.get('chunks', []))
            }
        else:
            return {
                'unit_id': unit_id,
                'status': 'failed',
                'error': result.get('error', 'Unknown error')
            }
        
    except Exception as e:
        braille_content = BrailleContent.objects.filter(unit_id=unit_id).first()
        if braille_content:
            braille_content.status = 'failed'
            braille_content.error_message = str(e)
            braille_content.save()
        
        # 재시도
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=30 * (self.request.retries + 1))
        
        return {
            'unit_id': unit_id,
            'status': 'failed',
            'error': str(e)
        }


@shared_task(bind=True, max_retries=2)
def analyze_graph_async(self, graph_item_id: int, image_data: bytes, title: str = "") -> Dict:
    """
    그래프 분석 비동기 처리
    
    Args:
        graph_item_id: GraphTableItem ID
        image_data: 이미지 바이트 데이터
        title: 그래프 제목
    
    Returns:
        {
            'item_id': graph_item_id,
            'status': 'completed' | 'failed',
            'patterns': {...}
        }
    """
    try:
        from .repositories import GraphTableRepository
        from . import exam_services
        GraphAnalysisService = exam_services.GraphAnalysisService
        
        graph_repo = GraphTableRepository()
        graph_item = graph_repo.get_by_id(graph_item_id)
        
        if not graph_item:
            raise ValueError(f"GraphTableItem {graph_item_id} not found")
        
        # 그래프 분석
        service = GraphAnalysisService(graph_repo=graph_repo)
        result = service.analyze_graph(image_data, title)
        
        # 결과 업데이트
        graph_repo.create(
            title=title or graph_item.title,
            patterns=result['patterns']
        )
        
        return {
            'item_id': graph_item_id,
            'status': 'completed',
            'patterns': result['patterns']
        }
        
    except Exception as e:
        # 재시도
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=30 * (self.request.retries + 1))
        
        return {
            'item_id': graph_item_id,
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def extract_units_async(textbook_id: int, text: str) -> Dict:
    """
    단원 추출 비동기 처리
    
    Args:
        textbook_id: Textbook ID
        text: 추출할 텍스트
    
    Returns:
        {
            'textbook_id': textbook_id,
            'unit_count': unit_count,
            'unit_ids': [1, 2, 3, ...]
        }
    """
    try:
        from .utils.text_extractor import extract_units_from_text
        from .models import Textbook, Unit
        
        textbook = Textbook.objects.get(id=textbook_id)
        units_data = extract_units_from_text(text)
        
        if not units_data:
            units_data = [{
                'order': 1,
                'title': '전체',
                'content': text[:5000]
            }]
        
        unit_ids = []
        for unit_data in units_data:
            unit = Unit.objects.create(
                textbook=textbook,
                title=unit_data['title'],
                order=unit_data['order'],
                content=unit_data['content']
            )
            unit_ids.append(unit.id)
        
        return {
            'textbook_id': textbook_id,
            'unit_count': len(unit_ids),
            'unit_ids': unit_ids
        }
        
    except Exception as e:
        return {
            'textbook_id': textbook_id,
            'status': 'failed',
            'error': str(e)
        }

