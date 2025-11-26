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

