"""
Repository Pattern - Learning App
복습 항목 데이터 접근 계층
"""
from typing import List, Optional
from django.utils import timezone
from .models import ReviewItem


class ReviewItemRepository:
    """ReviewItem 데이터 접근"""
    
    def create(self, **kwargs) -> ReviewItem:
        """새 복습 항목 생성"""
        return ReviewItem.objects.create(**kwargs)
    
    def get_by_id(self, id: int) -> Optional[ReviewItem]:
        """ID로 복습 항목 조회"""
        try:
            return ReviewItem.objects.get(id=id)
        except ReviewItem.DoesNotExist:
            return None
    
    def get_due_items(self, count: int = 10) -> List[ReviewItem]:
        """
        복습 시간이 된 항목들 조회
        next_due가 현재 시간 이하인 항목들을 반환
        """
        return list(
            ReviewItem.objects
            .filter(next_due__lte=timezone.now())
            .order_by('next_due', 'created_at')[:count]
        )
    
    def get_all_due_count(self) -> int:
        """복습 시간이 된 항목의 총 개수"""
        return ReviewItem.objects.filter(next_due__lte=timezone.now()).count()
    
    def update(self, item: ReviewItem, **kwargs) -> ReviewItem:
        """복습 항목 업데이트"""
        for key, value in kwargs.items():
            setattr(item, key, value)
        item.save()
        return item
    
    def delete(self, item: ReviewItem) -> None:
        """복습 항목 삭제"""
        item.delete()
    
    def get_by_type(self, type: str, limit: int = 100) -> List[ReviewItem]:
        """타입별 복습 항목 조회"""
        return list(
            ReviewItem.objects
            .filter(type=type)
            .order_by('-created_at')[:limit]
        )
    
    def get_by_source(self, source: str, limit: int = 100) -> List[ReviewItem]:
        """소스별 복습 항목 조회"""
        return list(
            ReviewItem.objects
            .filter(source=source)
            .order_by('-created_at')[:limit]
        )


