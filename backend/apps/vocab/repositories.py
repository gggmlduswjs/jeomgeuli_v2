"""
Repository Pattern Implementation for Vocab App
"""
from typing import List, Optional
from datetime import date
from .models import Vocabulary, VocabQueue, VocabProgress, SisaWord


class VocabularyRepository:
    """Vocabulary 데이터 접근"""
    
    def get_by_id(self, id: int) -> Optional[Vocabulary]:
        """ID로 어휘 조회"""
        try:
            return Vocabulary.objects.get(id=id)
        except Vocabulary.DoesNotExist:
            return None
    
    def get_all(self, limit: int = 100) -> List[Vocabulary]:
        """모든 어휘 조회"""
        return list(Vocabulary.objects.all()[:limit])
    
    def search_by_word(self, word: str) -> List[Vocabulary]:
        """단어로 검색"""
        return list(Vocabulary.objects.filter(word__icontains=word))
    
    def create(self, **kwargs) -> Vocabulary:
        """새 어휘 생성"""
        return Vocabulary.objects.create(**kwargs)


class VocabQueueRepository:
    """VocabQueue 데이터 접근"""
    
    def get_today_queue(self, target_date: date = None) -> List[VocabQueue]:
        """오늘의 어휘 큐 조회"""
        if target_date is None:
            target_date = date.today()
        return list(
            VocabQueue.objects
            .select_related('vocab')
            .filter(date=target_date, is_learned=False)
            .order_by('order')
        )
    
    def mark_learned(self, queue_id: int) -> bool:
        """학습 완료 표시"""
        try:
            queue_item = VocabQueue.objects.get(id=queue_id)
            queue_item.is_learned = True
            queue_item.save()
            return True
        except VocabQueue.DoesNotExist:
            return False
    
    def create(self, **kwargs) -> VocabQueue:
        """새 큐 항목 생성"""
        return VocabQueue.objects.create(**kwargs)


class VocabProgressRepository:
    """VocabProgress 데이터 접근"""
    
    def get_by_vocab(self, vocab_id: int) -> Optional[VocabProgress]:
        """어휘별 진행 상황 조회"""
        try:
            return VocabProgress.objects.select_related('vocab').get(vocab_id=vocab_id)
        except VocabProgress.DoesNotExist:
            return None
    
    def get_due_items(self) -> List[VocabProgress]:
        """복습 시간이 된 항목 조회"""
        from django.utils import timezone
        return list(
            VocabProgress.objects
            .filter(next_due__lte=timezone.now())
            .order_by('next_due')
        )
    
    def create_or_update(self, vocab_id: int, **kwargs) -> VocabProgress:
        """진행 상황 생성 또는 업데이트"""
        progress, created = VocabProgress.objects.get_or_create(
            vocab_id=vocab_id,
            defaults=kwargs
        )
        if not created:
            for key, value in kwargs.items():
                setattr(progress, key, value)
            progress.save()
        return progress


class SisaWordRepository:
    """SisaWord 데이터 접근"""
    
    def get_today_words(self, target_date: date = None) -> List[SisaWord]:
        """오늘의 시사 용어 조회"""
        if target_date is None:
            target_date = date.today()
        return list(
            SisaWord.objects
            .filter(date=target_date)
            .order_by('-created_at')
        )
    
    def get_recent(self, limit: int = 10) -> List[SisaWord]:
        """최근 시사 용어 조회"""
        return list(
            SisaWord.objects
            .order_by('-date', '-created_at')[:limit]
        )
    
    def create(self, **kwargs) -> SisaWord:
        """새 시사 용어 생성"""
        return SisaWord.objects.create(**kwargs)

