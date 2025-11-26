"""
Service Layer Pattern Implementation for Vocab App
어휘 학습 비즈니스 로직
"""
from typing import List, Dict
from datetime import date
from .repositories import (
    VocabularyRepository, VocabQueueRepository,
    VocabProgressRepository, SisaWordRepository
)
from apps.learning.srs import calculate_next_review


class VocabLearningService:
    """어휘 학습 비즈니스 로직"""
    
    def __init__(
        self,
        vocab_repo: VocabularyRepository = None,
        queue_repo: VocabQueueRepository = None,
        progress_repo: VocabProgressRepository = None
    ):
        self.vocab_repo = vocab_repo or VocabularyRepository()
        self.queue_repo = queue_repo or VocabQueueRepository()
        self.progress_repo = progress_repo or VocabProgressRepository()
    
    def get_today_vocab(self, target_date: date = None) -> List[Dict]:
        """오늘의 어휘 큐 조회"""
        queue_items = self.queue_repo.get_today_queue(target_date)
        
        result = []
        for item in queue_items:
            vocab = item.vocab
            result.append({
                'id': vocab.id,
                'word': vocab.word,
                'meaning': vocab.meaning,
                'example': vocab.example,
                'queue_id': item.id,
            })
        
        return result
    
    def mark_learned(self, queue_id: int, grade: int = 3) -> bool:
        """
        학습 완료 표시 및 SRS 업데이트
        grade: 0=틀림, 1=어려움, 2=보통, 3=쉬움, 4=완벽
        """
        queue_item = self.queue_repo.mark_learned(queue_id)
        if not queue_item:
            return False
        
        # SRS 진행 상황 업데이트
        progress = self.progress_repo.get_by_vocab(queue_item.vocab_id)
        if not progress:
            progress = self.progress_repo.create_or_update(
                vocab_id=queue_item.vocab_id
            )
        
        # SRS 알고리즘 적용
        new_interval, new_ease_factor, new_repetitions = calculate_next_review(
            progress.interval,
            progress.ease_factor,
            progress.repetitions,
            grade
        )
        
        from django.utils import timezone
        from datetime import timedelta
        
        self.progress_repo.create_or_update(
            vocab_id=queue_item.vocab_id,
            interval=new_interval,
            ease_factor=new_ease_factor,
            repetitions=new_repetitions,
            next_due=timezone.now() + timedelta(days=new_interval),
        )
        
        return True


class SisaWordService:
    """시사 용어 비즈니스 로직"""
    
    def __init__(self, sisa_repo: SisaWordRepository = None):
        self.repo = sisa_repo or SisaWordRepository()
    
    def get_today_sisa(self, target_date: date = None) -> List[Dict]:
        """오늘의 시사 용어 조회"""
        words = self.repo.get_today_words(target_date)
        
        return [
            {
                'id': word.id,
                'word': word.word,
                'meaning': word.meaning,
                'context': word.context,
                'source': word.source,
                'date': word.date.isoformat(),
            }
            for word in words
        ]
    
    def get_recent_sisa(self, limit: int = 10) -> List[Dict]:
        """최근 시사 용어 조회"""
        words = self.repo.get_recent(limit)
        
        return [
            {
                'id': word.id,
                'word': word.word,
                'meaning': word.meaning,
                'context': word.context,
                'date': word.date.isoformat(),
            }
            for word in words
        ]


