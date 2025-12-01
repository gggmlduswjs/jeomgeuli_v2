from django.db import models
from django.utils import timezone


class Textbook(models.Model):
    """수능특강 교재"""
    title = models.CharField(max_length=200, verbose_name="교재명")
    publisher = models.CharField(max_length=100, blank=True, verbose_name="출판사")
    year = models.IntegerField(null=True, blank=True, verbose_name="연도")
    subject = models.CharField(max_length=50, blank=True, verbose_name="과목")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', 'title']
        verbose_name = "교재"
        verbose_name_plural = "교재"
    
    def __str__(self):
        return f"{self.title} ({self.year or 'N/A'})"


class Unit(models.Model):
    """교재 단원"""
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='units', verbose_name="교재")
    title = models.CharField(max_length=200, verbose_name="단원명")
    order = models.IntegerField(default=0, verbose_name="순서")
    content = models.TextField(blank=True, verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['textbook', 'order']
        verbose_name = "단원"
        verbose_name_plural = "단원"
    
    def __str__(self):
        return f"{self.textbook.title} - {self.title}"


class Question(models.Model):
    """문제"""
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='questions', null=True, blank=True, verbose_name="단원")
    question_text = models.TextField(verbose_name="문제 내용")
    choice1 = models.CharField(max_length=500, blank=True, verbose_name="선택지 1")
    choice2 = models.CharField(max_length=500, blank=True, verbose_name="선택지 2")
    choice3 = models.CharField(max_length=500, blank=True, verbose_name="선택지 3")
    choice4 = models.CharField(max_length=500, blank=True, verbose_name="선택지 4")
    choice5 = models.CharField(max_length=500, blank=True, verbose_name="선택지 5")
    correct_answer = models.IntegerField(verbose_name="정답 (1-5)")
    explanation = models.TextField(blank=True, verbose_name="해설")
    difficulty = models.IntegerField(default=3, choices=[(1, '쉬움'), (2, '보통'), (3, '어려움')], verbose_name="난이도")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['unit', 'id']
        verbose_name = "문제"
        verbose_name_plural = "문제"
    
    def __str__(self):
        return f"Q{self.id}: {self.question_text[:50]}..."


class QuestionAttempt(models.Model):
    """문제 풀이 시도"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempts', verbose_name="문제")
    user_answer = models.IntegerField(verbose_name="사용자 답안")
    is_correct = models.BooleanField(verbose_name="정답 여부")
    response_time = models.FloatField(null=True, blank=True, verbose_name="응답 시간 (초)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "문제 시도"
        verbose_name_plural = "문제 시도"
    
    def __str__(self):
        return f"{self.question.id}: {self.user_answer} ({'정답' if self.is_correct else '오답'})"


class GraphTableItem(models.Model):
    """그래프/도표 항목"""
    title = models.CharField(max_length=200, verbose_name="제목")
    description = models.TextField(blank=True, verbose_name="설명")
    image_url = models.URLField(blank=True, verbose_name="이미지 URL")
    image_file = models.FileField(upload_to='graph_table/', null=True, blank=True, verbose_name="이미지 파일")
    
    # Extracted patterns (JSON)
    patterns = models.JSONField(default=dict, verbose_name="추출된 패턴")
    # 예: {"trend": "increase", "extremum": "maximum", "comparison": "greater"}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "그래프/도표"
        verbose_name_plural = "그래프/도표"
    
    def __str__(self):
        return self.title


class ExamSession(models.Model):
    """실전 모의고사 세션"""
    STATUS_CHOICES = [
        ('running', '진행 중'),
        ('paused', '일시정지'),
        ('finished', '종료'),
    ]
    
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="시작 시간")
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name="종료 시간")
    total_questions = models.IntegerField(default=0, verbose_name="총 문제 수")
    current_question_index = models.IntegerField(default=0, verbose_name="현재 문제 인덱스")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running', verbose_name="상태")
    answers = models.JSONField(default=dict, verbose_name="답안")
    # 예: {"1": 3, "2": 1, "3": 5} - 문제 ID: 답안 번호
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "시험 세션"
        verbose_name_plural = "시험 세션"
    
    def __str__(self):
        return f"시험 세션 {self.id} ({self.status})"


class BrailleContent(models.Model):
    """단원 점자 변환 데이터"""
    STATUS_CHOICES = [
        ('pending', '대기 중'),
        ('converting', '변환 중'),
        ('completed', '완료'),
        ('failed', '실패'),
    ]
    
    STRATEGY_CHOICES = [
        ('math', '수학'),
        ('korean', '국어'),
        ('english', '영어'),
        ('science', '과학'),
        ('social', '사회'),
    ]
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='braille_contents', verbose_name="단원")
    cells = models.JSONField(default=list, verbose_name="점자 셀 배열")
    # 예: [[1, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], ...]
    
    strategy = models.CharField(max_length=20, choices=STRATEGY_CHOICES, default='korean', verbose_name="과목별 전략")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="변환 상태")
    converted_at = models.DateTimeField(null=True, blank=True, verbose_name="변환 완료 시간")
    error_message = models.TextField(blank=True, verbose_name="오류 메시지")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['unit', '-created_at']
        verbose_name = "점자 변환 데이터"
        verbose_name_plural = "점자 변환 데이터"
        indexes = [
            models.Index(fields=['unit', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.unit.title} - {self.get_strategy_display()} ({self.get_status_display()})"


class PDFDocument(models.Model):
    """PDF 문서 메타데이터"""
    STATUS_CHOICES = [
        ('pending', '대기 중'),
        ('uploading', '업로드 중'),
        ('parsing', '파싱 중'),
        ('analyzing', '분석 중'),
        ('completed', '완료'),
        ('failed', '실패'),
    ]
    
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name='pdf_documents', null=True, blank=True, verbose_name="교재")
    original_filename = models.CharField(max_length=255, verbose_name="원본 파일명")
    file_path = models.CharField(max_length=500, verbose_name="파일 경로")
    file_size = models.BigIntegerField(default=0, verbose_name="파일 크기 (bytes)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="처리 상태")
    progress = models.IntegerField(default=0, verbose_name="진행률 (%)")
    
    # OCR 및 분석 결과
    ocr_results = models.JSONField(default=dict, blank=True, verbose_name="OCR 결과")
    layout_analysis = models.JSONField(default=dict, blank=True, verbose_name="레이아웃 분석 결과")
    extracted_text = models.TextField(blank=True, verbose_name="추출된 텍스트")
    image_areas = models.JSONField(default=list, blank=True, verbose_name="이미지 영역 정보")
    
    error_message = models.TextField(blank=True, verbose_name="오류 메시지")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "PDF 문서"
        verbose_name_plural = "PDF 문서"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['textbook', 'status']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.get_status_display()})"


class Passage(models.Model):
    """지문 모델"""
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='passages', verbose_name="단원")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='passages', null=True, blank=True, verbose_name="문제")
    
    content = models.TextField(verbose_name="지문 내용")
    order = models.IntegerField(default=0, verbose_name="순서")
    
    # 문장 분리 및 구조 분석 결과
    sentences = models.JSONField(default=list, blank=True, verbose_name="문장 분리 결과")
    # 예: [{"id": 1, "text": "문장1", "index": 0}, ...]
    
    paragraphs = models.JSONField(default=list, blank=True, verbose_name="단락 분리 결과")
    # 예: [{"id": 1, "start_sentence": 0, "end_sentence": 5, "type": "introduction"}, ...]
    
    central_sentences = models.JSONField(default=list, blank=True, verbose_name="중심 문장")
    # 예: [1, 3, 5] - sentence id 리스트
    
    keywords = models.JSONField(default=list, blank=True, verbose_name="키워드")
    # 예: ["키워드1", "키워드2", ...]
    
    # 구조 분석 결과
    structure_analysis = models.JSONField(default=dict, blank=True, verbose_name="구조 분석 결과")
    # 예: {"summary": "...", "characters": [...], "structure": "..."}
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['unit', 'order', 'id']
        verbose_name = "지문"
        verbose_name_plural = "지문"
        indexes = [
            models.Index(fields=['unit', 'order']),
            models.Index(fields=['question']),
        ]
    
    def __str__(self):
        return f"Passage {self.id}: {self.content[:50]}..."


class Choice(models.Model):
    """선택지 모델"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name="문제")
    order = models.IntegerField(verbose_name="선택지 번호 (1-5)")
    text = models.TextField(verbose_name="선택지 내용")
    
    # 근거 문장 매핑
    evidence_sentences = models.JSONField(default=list, blank=True, verbose_name="근거 문장 ID")
    # 예: [1, 3, 5] - Passage의 sentence id 리스트
    
    # 논리 구조 분석 결과
    logic_structure = models.JSONField(default=dict, blank=True, verbose_name="논리 구조")
    # 예: {"core_claim": "...", "error_type": "condition_mismatch", "paraphrase_analysis": {...}}
    
    # 오답 분석 결과
    wrong_answer_analysis = models.JSONField(default=dict, blank=True, verbose_name="오답 분석")
    # 예: {"reason": "...", "corrected_claim": "..."}
    
    is_correct = models.BooleanField(default=False, verbose_name="정답 여부")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['question', 'order']
        verbose_name = "선택지"
        verbose_name_plural = "선택지"
        unique_together = [['question', 'order']]
        indexes = [
            models.Index(fields=['question', 'order']),
        ]
    
    def __str__(self):
        return f"Q{self.question.id} - {self.order}번: {self.text[:50]}..."


class EvidenceMapping(models.Model):
    """문항-근거 매핑"""
    MAPPING_TYPE_CHOICES = [
        ('direct', '직접 근거'),
        ('inference', '추론 근거'),
        ('contradiction', '모순 근거'),
        ('support', '지지 근거'),
    ]
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='evidence_mappings', verbose_name="문제")
    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name='evidence_mappings', null=True, blank=True, verbose_name="지문")
    passage_sentence_id = models.IntegerField(verbose_name="지문 문장 인덱스")
    # Passage의 sentences JSON 배열에서의 인덱스
    
    similarity_score = models.FloatField(verbose_name="의미 유사도 점수")
    # 0.0 ~ 1.0
    
    mapping_type = models.CharField(max_length=20, choices=MAPPING_TYPE_CHOICES, default='direct', verbose_name="매핑 타입")
    
    # 추가 정보
    context_sentences = models.JSONField(default=list, blank=True, verbose_name="주변 문장 ID")
    # 예: [0, 1, 2] - 앞뒤 문장 포함
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['question', '-similarity_score']
        verbose_name = "근거 매핑"
        verbose_name_plural = "근거 매핑"
        indexes = [
            models.Index(fields=['question', 'similarity_score']),
            models.Index(fields=['passage', 'passage_sentence_id']),
        ]
    
    def __str__(self):
        return f"Q{self.question.id} → Passage {self.passage.id if self.passage else 'N/A'}: Sentence {self.passage_sentence_id} ({self.similarity_score:.2f})"


class BrailleChunk(models.Model):
    """점자 청크 모델 (3-cell 패킷)"""
    SEMANTIC_TYPE_CHOICES = [
        ('sentence', '문장'),
        ('word', '단어'),
        ('formula', '수식'),
        ('keyword', '키워드'),
        ('graph_pattern', '그래프 패턴'),
        ('choice', '선택지'),
        ('evidence', '근거'),
    ]
    
    content = models.ForeignKey(BrailleContent, on_delete=models.CASCADE, related_name='chunks', verbose_name="점자 콘텐츠")
    passage = models.ForeignKey(Passage, on_delete=models.CASCADE, related_name='braille_chunks', null=True, blank=True, verbose_name="지문")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='braille_chunks', null=True, blank=True, verbose_name="문제")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='braille_chunks', null=True, blank=True, verbose_name="선택지")
    
    chunk_index = models.IntegerField(verbose_name="청크 인덱스")
    # 같은 content 내에서의 순서
    
    # 3-cell 패킷 데이터
    cells = models.JSONField(default=list, verbose_name="3-cell 패킷")
    # 예: [[1,0,0,0,0,0], [1,1,0,0,0,0], [1,0,0,1,0,0]] - 3개 셀
    
    semantic_type = models.CharField(max_length=50, choices=SEMANTIC_TYPE_CHOICES, default='sentence', verbose_name="의미 타입")
    
    # 원본 텍스트 정보
    original_text = models.TextField(blank=True, verbose_name="원본 텍스트")
    start_position = models.IntegerField(null=True, blank=True, verbose_name="원본 텍스트 시작 위치")
    end_position = models.IntegerField(null=True, blank=True, verbose_name="원본 텍스트 끝 위치")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['content', 'chunk_index']
        verbose_name = "점자 청크"
        verbose_name_plural = "점자 청크"
        unique_together = [['content', 'chunk_index']]
        indexes = [
            models.Index(fields=['content', 'chunk_index']),
            models.Index(fields=['semantic_type']),
        ]
    
    def __str__(self):
        return f"Chunk {self.chunk_index} ({self.get_semantic_type_display()}) - {self.content.unit.title}"
