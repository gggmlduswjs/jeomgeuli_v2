from django.db import models
from django.utils import timezone


class Vocabulary(models.Model):
    """어휘 데이터베이스"""
    word = models.CharField(max_length=100, unique=True, verbose_name="단어")
    meaning = models.TextField(verbose_name="의미")
    example = models.TextField(blank=True, verbose_name="예문")
    difficulty = models.IntegerField(default=3, choices=[(1, '쉬움'), (2, '보통'), (3, '어려움')], verbose_name="난이도")
    category = models.CharField(max_length=50, blank=True, verbose_name="카테고리")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['word']
        verbose_name = "어휘"
        verbose_name_plural = "어휘"
    
    def __str__(self):
        return self.word


class VocabQueue(models.Model):
    """일일 어휘 학습 큐"""
    vocab = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, related_name='queue_items', verbose_name="어휘")
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    order = models.IntegerField(default=0, verbose_name="순서")
    is_learned = models.BooleanField(default=False, verbose_name="학습 완료")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'order']
        unique_together = ['vocab', 'date']
        verbose_name = "어휘 큐"
        verbose_name_plural = "어휘 큐"
    
    def __str__(self):
        return f"{self.date}: {self.vocab.word}"


class VocabProgress(models.Model):
    """어휘 학습 진행 상황"""
    vocab = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, related_name='progress', verbose_name="어휘")
    # SRS fields
    ease_factor = models.FloatField(default=2.5, verbose_name="쉬움 인수")
    interval = models.IntegerField(default=1, verbose_name="간격 (일)")
    repetitions = models.IntegerField(default=0, verbose_name="반복 횟수")
    next_due = models.DateTimeField(default=timezone.now, verbose_name="다음 복습일")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['next_due']
        verbose_name = "어휘 진행"
        verbose_name_plural = "어휘 진행"
    
    def __str__(self):
        return f"{self.vocab.word}: {self.repetitions}회"


class SisaWord(models.Model):
    """시사 용어"""
    word = models.CharField(max_length=100, unique=True, verbose_name="용어")
    meaning = models.TextField(verbose_name="의미")
    context = models.TextField(blank=True, verbose_name="맥락")
    source = models.CharField(max_length=200, blank=True, verbose_name="출처")
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', 'word']
        verbose_name = "시사 용어"
        verbose_name_plural = "시사 용어"
    
    def __str__(self):
        return f"{self.word} ({self.date})"

