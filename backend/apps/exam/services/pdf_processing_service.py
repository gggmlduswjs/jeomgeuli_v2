"""
PDF 처리 통합 서비스
동기/비동기 처리 통합
"""
from typing import Dict, Optional
from django.core.files.uploadedfile import UploadedFile
from django.core.files.storage import default_storage
from ..models import Textbook, Unit, PDFDocument
from ..utils.text_extractor import extract_textbook_info, extract_units_from_text
from ..parsers import PDFParser
from core.exceptions import PDFProcessingException, ValidationException


class PDFProcessingService:
    """PDF 처리 통합 서비스"""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
    
    def process_pdf(
        self,
        pdf_file: UploadedFile,
        async_mode: bool = True
    ) -> Dict:
        """
        PDF 처리 (동기/비동기 선택)
        
        Args:
            pdf_file: 업로드된 PDF 파일
            async_mode: True면 Celery 태스크로 비동기 처리
        
        Returns:
            {
                'textbook_id': int,
                'unit_count': int,
                'pdf_document_id': int,
                'task_id': str (async_mode일 때만),
                'message': str
            }
        """
        if async_mode:
            return self._process_async(pdf_file)
        else:
            return self._process_sync(pdf_file)
    
    def _process_sync(self, pdf_file: UploadedFile) -> Dict:
        """동기 처리 (즉시 완료)"""
        # PDF 텍스트 추출
        pdf_file.seek(0)
        text = self.pdf_parser.extract_text(pdf_file)
        
        if not text.strip():
            raise PDFProcessingException(
                'PDF에서 텍스트를 추출할 수 없습니다',
                user_message='PDF 파일에서 텍스트를 추출할 수 없습니다. 이미지로만 구성된 PDF일 수 있습니다.'
            )
        
        # 교재 정보 추출
        textbook_info = extract_textbook_info(pdf_file.name)
        
        # 단원 추출
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
        
        if not created:
            return {
                'ok': True,
                'textbook_id': textbook.id,
                'unit_count': 0,
                'message': '이미 존재하는 교재입니다.',
                'existing': True,
            }
        
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
        
        return {
            'ok': True,
            'textbook_id': textbook.id,
            'unit_count': len(unit_ids),
            'message': 'PDF 처리 완료',
        }
    
    def _process_async(self, pdf_file: UploadedFile) -> Dict:
        """비동기 처리 (Celery 태스크)"""
        # PDF 파일 저장
        pdf_path = default_storage.save(f'pdfs/{pdf_file.name}', pdf_file)
        full_path = default_storage.path(pdf_path)
        
        # 초기 텍스트 추출 (빠른 응답을 위해)
        pdf_file.seek(0)
        try:
            text = self.pdf_parser.extract_text(pdf_file)
        except Exception as e:
            raise PDFProcessingException(
                f'PDF 텍스트 추출 실패: {str(e)}',
                user_message='PDF 파일 처리 중 오류가 발생했습니다.'
            )
        
        if not text.strip():
            raise PDFProcessingException(
                'PDF에서 텍스트를 추출할 수 없습니다',
                user_message='PDF 파일에서 텍스트를 추출할 수 없습니다. 이미지로만 구성된 PDF일 수 있습니다.'
            )
        
        # 교재 정보 추출
        textbook_info = extract_textbook_info(pdf_file.name)
        
        # 단원 추출 (간단한 버전)
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
        
        if not created:
            return {
                'ok': True,
                'textbook_id': textbook.id,
                'unit_count': 0,
                'message': '이미 존재하는 교재입니다.',
                'existing': True,
            }
        
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
        
        # PDFDocument 생성
        pdf_doc = PDFDocument.objects.create(
            textbook=textbook,
            original_filename=pdf_file.name,
            file_path=full_path,
            file_size=pdf_file.size,
            status='pending',
            extracted_text=text,
            progress=0
        )
        
        # Celery 태스크로 비동기 처리 시작 (순환 import 방지를 위해 지연 import)
        from ..tasks import process_pdf_async, convert_braille_async
        task = process_pdf_async.delay(pdf_doc.id)
        
        # 점자 변환도 비동기로 시작
        for unit_id in unit_ids:
            convert_braille_async.delay(unit_id, textbook.subject)
        
        return {
            'ok': True,
            'textbook_id': textbook.id,
            'unit_count': len(unit_ids),
            'pdf_document_id': pdf_doc.id,
            'task_id': task.id,
            'message': 'PDF 업로드 완료. 분석 및 점자 변환은 백그라운드에서 진행됩니다.',
        }

