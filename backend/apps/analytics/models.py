from django.db import models
from django.utils import timezone


class BrailleSpeedLog(models.Model):
    """점자 읽기 속도 로그"""
    pattern_count = models.IntegerField(verbose_name="패턴 수")
    time_seconds = models.FloatField(verbose_name="시간 (초)")
    speed_per_minute = models.FloatField(verbose_name="분당 속도")
    accuracy = models.FloatField(null=True, blank=True, verbose_name="정확도")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "점자 속도 로그"
        verbose_name_plural = "점자 속도 로그"
    
    def __str__(self):
        return f"{self.speed_per_minute:.1f} 패턴/분 ({self.created_at.strftime('%Y-%m-%d')})"


class WrongAnswerPattern(models.Model):
    """오답 패턴 분석"""
    question_id = models.IntegerField(null=True, blank=True, verbose_name="문제 ID")
    wrong_answer = models.IntegerField(verbose_name="오답")
    correct_answer = models.IntegerField(verbose_name="정답")
    pattern_type = models.CharField(max_length=50, blank=True, verbose_name="패턴 유형")
    # 예: "similar_choice", "calculation_error", "concept_misunderstanding"
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "오답 패턴"
        verbose_name_plural = "오답 패턴"
    
    def __str__(self):
        return f"Q{self.question_id}: {self.wrong_answer}→{self.correct_answer} ({self.pattern_type})"


class TimingLog(models.Model):
    """시험 시간 관리 로그"""
    exam_type = models.CharField(max_length=50, verbose_name="시험 유형")
    subject = models.CharField(max_length=50, blank=True, verbose_name="과목")
    allocated_time = models.IntegerField(verbose_name="할당 시간 (분)")
    used_time = models.IntegerField(verbose_name="사용 시간 (분)")
    remaining_time = models.IntegerField(verbose_name="남은 시간 (분)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "시간 로그"
        verbose_name_plural = "시간 로그"
    
    def __str__(self):
        return f"{self.exam_type} - {self.subject}: {self.used_time}/{self.allocated_time}분"

