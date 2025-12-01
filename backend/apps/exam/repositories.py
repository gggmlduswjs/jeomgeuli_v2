"""
Repository Pattern Implementation for Exam App
데이터 접근 계층 분리
"""
from typing import List, Optional
from .models import (
    Textbook, Unit, Question, QuestionAttempt, GraphTableItem, ExamSession,
    PDFDocument, Passage, Choice, EvidenceMapping, BrailleChunk, BrailleContent
)


class TextbookRepository:
    """Textbook 데이터 접근"""
    
    def get_all(self) -> List[Textbook]:
        """모든 교재 조회"""
        return list(Textbook.objects.all())
    
    def get_by_id(self, id: int) -> Optional[Textbook]:
        """ID로 교재 조회"""
        try:
            return Textbook.objects.get(id=id)
        except Textbook.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> Textbook:
        """새 교재 생성"""
        return Textbook.objects.create(**kwargs)
    
    def filter_by_subject(self, subject: str) -> List[Textbook]:
        """과목별 교재 조회"""
        return list(Textbook.objects.filter(subject=subject))


class UnitRepository:
    """Unit 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[Unit]:
        """ID로 단원 조회"""
        try:
            return Unit.objects.select_related('textbook').get(id=id)
        except Unit.DoesNotExist:
            return None
    
    def get_by_textbook(self, textbook_id: int) -> List[Unit]:
        """교재별 단원 조회"""
        return list(Unit.objects.filter(textbook_id=textbook_id).select_related('textbook').order_by('order'))
    
    def create(self, **kwargs) -> Unit:
        """새 단원 생성"""
        return Unit.objects.create(**kwargs)


class QuestionRepository:
    """Question 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[Question]:
        """ID로 문제 조회"""
        try:
            return Question.objects.select_related('unit', 'unit__textbook').get(id=id)
        except Question.DoesNotExist:
            return None
    
    def get_by_unit(self, unit_id: int) -> List[Question]:
        """단원별 문제 조회"""
        return list(Question.objects.filter(unit_id=unit_id).select_related('unit'))
    
    def create(self, **kwargs) -> Question:
        """새 문제 생성"""
        return Question.objects.create(**kwargs)
    
    def filter_by_difficulty(self, difficulty: int) -> List[Question]:
        """난이도별 문제 조회"""
        return list(Question.objects.filter(difficulty=difficulty))


class QuestionAttemptRepository:
    """QuestionAttempt 데이터 접근"""
    
    def create(self, **kwargs) -> QuestionAttempt:
        """새 시도 기록 생성"""
        return QuestionAttempt.objects.create(**kwargs)
    
    def get_wrong_answers(self, limit: int = 10) -> List[QuestionAttempt]:
        """오답 목록 조회"""
        return list(
            QuestionAttempt.objects
            .filter(is_correct=False)
            .order_by('-created_at')[:limit]
        )
    
    def get_by_question(self, question_id: int) -> List[QuestionAttempt]:
        """문제별 시도 기록 조회"""
        return list(
            QuestionAttempt.objects
            .filter(question_id=question_id)
            .order_by('-created_at')
        )


class GraphTableRepository:
    """GraphTableItem 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[GraphTableItem]:
        """ID로 그래프/도표 조회"""
        try:
            return GraphTableItem.objects.get(id=id)
        except GraphTableItem.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> GraphTableItem:
        """새 그래프/도표 항목 생성"""
        return GraphTableItem.objects.create(**kwargs)
    
    def get_all(self, limit: int = 20) -> List[GraphTableItem]:
        """모든 그래프/도표 조회"""
        return list(GraphTableItem.objects.all()[:limit])


class ExamSessionRepository:
    """ExamSession 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[ExamSession]:
        """ID로 시험 세션 조회"""
        try:
            return ExamSession.objects.get(id=id)
        except ExamSession.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> ExamSession:
        """새 시험 세션 생성"""
        return ExamSession.objects.create(**kwargs)
    
    def update(self, session: ExamSession, **kwargs) -> ExamSession:
        """시험 세션 업데이트"""
        for key, value in kwargs.items():
            setattr(session, key, value)
        session.save()
        return session
    
    def get_active_sessions(self) -> List[ExamSession]:
        """진행 중인 시험 세션 조회"""
        return list(ExamSession.objects.filter(status__in=['running', 'paused']))


class PDFDocumentRepository:
    """PDFDocument 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[PDFDocument]:
        """ID로 PDF 문서 조회"""
        try:
            return PDFDocument.objects.select_related('textbook').get(id=id)
        except PDFDocument.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> PDFDocument:
        """새 PDF 문서 생성"""
        return PDFDocument.objects.create(**kwargs)
    
    def get_by_textbook(self, textbook_id: int) -> List[PDFDocument]:
        """교재별 PDF 문서 조회"""
        return list(PDFDocument.objects.filter(textbook_id=textbook_id).order_by('-created_at'))
    
    def get_by_status(self, status: str) -> List[PDFDocument]:
        """상태별 PDF 문서 조회"""
        return list(PDFDocument.objects.filter(status=status).order_by('-created_at'))
    
    def update_status(self, document: PDFDocument, status: str, progress: int = None) -> PDFDocument:
        """PDF 문서 상태 업데이트"""
        document.status = status
        if progress is not None:
            document.progress = progress
        document.save()
        return document


class PassageRepository:
    """Passage 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[Passage]:
        """ID로 지문 조회"""
        try:
            return Passage.objects.select_related('unit', 'question').get(id=id)
        except Passage.DoesNotExist:
            return None
    
    def get_by_unit(self, unit_id: int) -> List[Passage]:
        """단원별 지문 조회"""
        return list(Passage.objects.filter(unit_id=unit_id).order_by('order', 'id'))
    
    def get_by_question(self, question_id: int) -> List[Passage]:
        """문제별 지문 조회"""
        return list(Passage.objects.filter(question_id=question_id).order_by('order'))
    
    def create(self, **kwargs) -> Passage:
        """새 지문 생성"""
        return Passage.objects.create(**kwargs)
    
    def update_analysis(self, passage: Passage, analysis_data: dict) -> Passage:
        """지문 분석 결과 업데이트"""
        if 'sentences' in analysis_data:
            passage.sentences = analysis_data['sentences']
        if 'paragraphs' in analysis_data:
            passage.paragraphs = analysis_data['paragraphs']
        if 'central_sentences' in analysis_data:
            passage.central_sentences = analysis_data['central_sentences']
        if 'keywords' in analysis_data:
            passage.keywords = analysis_data['keywords']
        if 'structure_analysis' in analysis_data:
            passage.structure_analysis = analysis_data['structure_analysis']
        passage.save()
        return passage


class ChoiceRepository:
    """Choice 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[Choice]:
        """ID로 선택지 조회"""
        try:
            return Choice.objects.select_related('question').get(id=id)
        except Choice.DoesNotExist:
            return None
    
    def get_by_question(self, question_id: int) -> List[Choice]:
        """문제별 선택지 조회"""
        return list(Choice.objects.filter(question_id=question_id).order_by('order'))
    
    def create(self, **kwargs) -> Choice:
        """새 선택지 생성"""
        return Choice.objects.create(**kwargs)
    
    def get_correct_choice(self, question_id: int) -> Optional[Choice]:
        """문제의 정답 선택지 조회"""
        try:
            return Choice.objects.filter(question_id=question_id, is_correct=True).first()
        except Choice.DoesNotExist:
            return None
    
    def update_analysis(self, choice: Choice, analysis_data: dict) -> Choice:
        """선택지 분석 결과 업데이트"""
        if 'evidence_sentences' in analysis_data:
            choice.evidence_sentences = analysis_data['evidence_sentences']
        if 'logic_structure' in analysis_data:
            choice.logic_structure = analysis_data['logic_structure']
        if 'wrong_answer_analysis' in analysis_data:
            choice.wrong_answer_analysis = analysis_data['wrong_answer_analysis']
        choice.save()
        return choice


class EvidenceMappingRepository:
    """EvidenceMapping 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[EvidenceMapping]:
        """ID로 근거 매핑 조회"""
        try:
            return EvidenceMapping.objects.select_related('question', 'passage').get(id=id)
        except EvidenceMapping.DoesNotExist:
            return None
    
    def get_by_question(self, question_id: int, min_score: float = 0.0) -> List[EvidenceMapping]:
        """문제별 근거 매핑 조회 (유사도 점수 기준)"""
        return list(
            EvidenceMapping.objects
            .filter(question_id=question_id, similarity_score__gte=min_score)
            .order_by('-similarity_score')
        )
    
    def get_by_passage(self, passage_id: int) -> List[EvidenceMapping]:
        """지문별 근거 매핑 조회"""
        return list(EvidenceMapping.objects.filter(passage_id=passage_id).order_by('-similarity_score'))
    
    def create(self, **kwargs) -> EvidenceMapping:
        """새 근거 매핑 생성"""
        return EvidenceMapping.objects.create(**kwargs)
    
    def create_bulk(self, mappings: List[dict]) -> List[EvidenceMapping]:
        """대량 근거 매핑 생성"""
        return EvidenceMapping.objects.bulk_create([
            EvidenceMapping(**mapping) for mapping in mappings
        ])


class BrailleChunkRepository:
    """BrailleChunk 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[BrailleChunk]:
        """ID로 점자 청크 조회"""
        try:
            return BrailleChunk.objects.select_related('content', 'passage', 'question', 'choice').get(id=id)
        except BrailleChunk.DoesNotExist:
            return None
    
    def get_by_content(self, content_id: int) -> List[BrailleChunk]:
        """점자 콘텐츠별 청크 조회"""
        return list(BrailleChunk.objects.filter(content_id=content_id).order_by('chunk_index'))
    
    def get_by_semantic_type(self, content_id: int, semantic_type: str) -> List[BrailleChunk]:
        """의미 타입별 청크 조회"""
        return list(
            BrailleChunk.objects
            .filter(content_id=content_id, semantic_type=semantic_type)
            .order_by('chunk_index')
        )
    
    def create(self, **kwargs) -> BrailleChunk:
        """새 점자 청크 생성"""
        return BrailleChunk.objects.create(**kwargs)
    
    def create_bulk(self, chunks: List[dict]) -> List[BrailleChunk]:
        """대량 점자 청크 생성"""
        return BrailleChunk.objects.bulk_create([
            BrailleChunk(**chunk) for chunk in chunks
        ])
    
    def get_next_chunk(self, content_id: int, current_index: int) -> Optional[BrailleChunk]:
        """다음 청크 조회"""
        try:
            return BrailleChunk.objects.filter(
                content_id=content_id,
                chunk_index__gt=current_index
            ).order_by('chunk_index').first()
        except BrailleChunk.DoesNotExist:
            return None
    
    def get_prev_chunk(self, content_id: int, current_index: int) -> Optional[BrailleChunk]:
        """이전 청크 조회"""
        try:
            return BrailleChunk.objects.filter(
                content_id=content_id,
                chunk_index__lt=current_index
            ).order_by('-chunk_index').first()
        except BrailleChunk.DoesNotExist:
            return None

