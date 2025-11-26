"""
Repository Pattern Implementation for Exam App
데이터 접근 계층 분리
"""
from typing import List, Optional
from .models import Textbook, Unit, Question, QuestionAttempt, GraphTableItem, ExamSession


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

