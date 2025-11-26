"""
Service Layer Pattern Implementation for Exam App
비즈니스 로직 캡슐화
"""
from typing import Dict, Optional, List
from django.utils import timezone
from .repositories import (
    TextbookRepository, UnitRepository, QuestionRepository,
    QuestionAttemptRepository, GraphTableRepository, ExamSessionRepository
)
from .models import QuestionAttempt, BrailleContent, Unit
from utils.braille_converter import text_to_cells


class TextbookService:
    """교재 관련 비즈니스 로직"""
    
    def __init__(self, textbook_repo: TextbookRepository = None):
        self.repo = textbook_repo or TextbookRepository()
    
    def list_textbooks(self, subject: str = None) -> list:
        """교재 목록 조회"""
        if subject:
            textbooks = self.repo.filter_by_subject(subject)
        else:
            textbooks = self.repo.get_all()
        
        # 모델 객체를 딕셔너리로 변환
        return [
            {
                'id': textbook.id,
                'title': textbook.title,
                'publisher': textbook.publisher or '',
                'year': textbook.year,
                'subject': textbook.subject or '',
            }
            for textbook in textbooks
        ]
    
    def get_textbook(self, textbook_id: int) -> Optional[dict]:
        """교재 상세 조회"""
        textbook = self.repo.get_by_id(textbook_id)
        if not textbook:
            return None
        
        return {
            'id': textbook.id,
            'title': textbook.title,
            'publisher': textbook.publisher,
            'year': textbook.year,
            'subject': textbook.subject,
        }


class UnitService:
    """단원 관련 비즈니스 로직"""
    
    def __init__(self, unit_repo: UnitRepository = None):
        self.repo = unit_repo or UnitRepository()
    
    def get_unit(self, unit_id: int) -> Optional[dict]:
        """단원 상세 조회"""
        unit = self.repo.get_by_id(unit_id)
        if not unit:
            return None
        
        return {
            'id': unit.id,
            'title': unit.title,
            'order': unit.order,
            'content': unit.content,
            'textbook_id': unit.textbook.id,
            'textbook_title': unit.textbook.title,
        }
    
    def list_units(self, textbook_id: int) -> list:
        """교재별 단원 목록"""
        units = self.repo.get_by_textbook(textbook_id)
        return [
            {
                'id': unit.id,
                'title': unit.title,
                'order': unit.order,
            }
            for unit in units
        ]


class QuestionService:
    """문제 관련 비즈니스 로직"""
    
    def __init__(
        self,
        question_repo: QuestionRepository = None,
        attempt_repo: QuestionAttemptRepository = None
    ):
        self.question_repo = question_repo or QuestionRepository()
        self.attempt_repo = attempt_repo or QuestionAttemptRepository()
    
    def get_question(self, question_id: int) -> Optional[dict]:
        """문제 상세 조회"""
        question = self.question_repo.get_by_id(question_id)
        if not question:
            return None
        
        return {
            'id': question.id,
            'question_text': question.question_text,
            'choice1': question.choice1,
            'choice2': question.choice2,
            'choice3': question.choice3,
            'choice4': question.choice4,
            'choice5': question.choice5,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
            'difficulty': question.difficulty,
        }
    
    def submit_answer(
        self,
        question_id: int,
        user_answer: int,
        response_time: float = None
    ) -> Dict:
        """답안 제출 및 검증"""
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise ValueError("Question not found")
        
        # 답안 검증
        is_correct = question.correct_answer == user_answer
        
        # 시도 기록 저장
        attempt = self.attempt_repo.create(
            question=question,
            user_answer=user_answer,
            is_correct=is_correct,
            response_time=response_time,
        )
        
        # 오답 패턴 로깅 (나중에 analytics 서비스로 이동 가능)
        if not is_correct:
            self._log_wrong_pattern(question, user_answer)
        
        return {
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
            'attempt_id': attempt.id,
        }
    
    def _log_wrong_pattern(self, question, user_answer):
        """오답 패턴 로깅 (내부 메서드)"""
        from apps.analytics.services import AnalyticsService
        analytics_service = AnalyticsService()
        analytics_service.log_wrong_answer(
            question_id=question.id,
            wrong_answer=user_answer,
            correct_answer=question.correct_answer,
            pattern_type='user_mistake',
        )


class GraphAnalysisService:
    """그래프/도표 분석 비즈니스 로직"""
    
    def __init__(self, graph_repo: GraphTableRepository = None):
        self.repo = graph_repo or GraphTableRepository()
    
    def analyze_graph(self, image_data: bytes, title: str = "", prompt: str = "") -> Dict:
        """
        그래프/도표 분석 및 패턴 추출
        Vision API 사용
        """
        patterns = {
            'trend': 'stable',  # 기본값
            'extremum': 'none',
            'comparison': 'equal',
        }
        
        # AI 클라이언트로 이미지 분석
        try:
            from core.ai.factory import AIClientFactory
            
            # AIClientFactory를 사용하여 AI 클라이언트 생성
            ai_client = AIClientFactory.create(provider='gemini')
            
            if ai_client and hasattr(ai_client, 'analyze_image'):
                analysis_prompt = prompt or "이 그래프나 도표를 분석하여 추세(증가/감소/유지), 극대/극소점, 주요 비교값을 추출해주세요. JSON 형식: {\"trend\": \"increase|decrease|stable\", \"extremum\": \"maximum|minimum|none\", \"comparison\": \"greater|less|equal\"}"
                patterns = ai_client.analyze_image(image_data, analysis_prompt)
            else:
                # Vision API를 지원하지 않는 클라이언트인 경우
                print("[GraphAnalysisService] Vision API를 지원하지 않는 AI 클라이언트입니다.")
        except Exception as e:
            # AI 분석 실패 시 기본값 사용
            print(f"[GraphAnalysisService] AI 분석 실패: {e}")
        
        # DB에 저장 (선택적)
        graph_item = self.repo.create(
            title=title or "Graph Analysis",
            patterns=patterns,
        )
        
        return {
            'patterns': patterns,
            'item_id': graph_item.id,
        }


class ExamSessionService:
    """시험 세션 관련 비즈니스 로직"""
    
    def __init__(self, session_repo: ExamSessionRepository = None):
        self.repo = session_repo or ExamSessionRepository()
    
    def start_exam(self, total_questions: int = 0) -> Dict:
        """시험 세션 시작"""
        session = self.repo.create(
            total_questions=total_questions,
            status='running',
            current_question_index=0,
            answers={},
        )
        
        return {
            'exam_id': session.id,
            'started_at': session.started_at.isoformat(),
            'total_questions': session.total_questions,
            'status': session.status,
        }
    
    def get_exam_session(self, exam_id: int) -> Optional[Dict]:
        """시험 세션 조회"""
        session = self.repo.get_by_id(exam_id)
        if not session:
            return None
        
        return {
            'exam_id': session.id,
            'started_at': session.started_at.isoformat(),
            'ended_at': session.ended_at.isoformat() if session.ended_at else None,
            'total_questions': session.total_questions,
            'current_question_index': session.current_question_index,
            'status': session.status,
            'answers': session.answers,
        }
    
    def update_answer(self, exam_id: int, question_id: int, answer: int) -> Dict:
        """답안 업데이트"""
        session = self.repo.get_by_id(exam_id)
        if not session:
            raise ValueError("Exam session not found")
        
        if session.status != 'running':
            raise ValueError("Exam session is not running")
        
        # 답안 업데이트
        answers = session.answers.copy()
        answers[str(question_id)] = answer
        self.repo.update(session, answers=answers)
        
        return {
            'exam_id': session.id,
            'answers': session.answers,
        }
    
    def update_question_index(self, exam_id: int, question_index: int) -> Dict:
        """현재 문제 인덱스 업데이트"""
        session = self.repo.get_by_id(exam_id)
        if not session:
            raise ValueError("Exam session not found")
        
        if question_index < 0 or question_index >= session.total_questions:
            raise ValueError("Invalid question index")
        
        self.repo.update(session, current_question_index=question_index)
        
        return {
            'exam_id': session.id,
            'current_question_index': session.current_question_index,
        }
    
    def pause_exam(self, exam_id: int) -> Dict:
        """시험 일시정지"""
        session = self.repo.get_by_id(exam_id)
        if not session:
            raise ValueError("Exam session not found")
        
        if session.status != 'running':
            raise ValueError("Exam session is not running")
        
        self.repo.update(session, status='paused')
        
        return {
            'exam_id': session.id,
            'status': session.status,
        }
    
    def resume_exam(self, exam_id: int) -> Dict:
        """시험 재개"""
        session = self.repo.get_by_id(exam_id)
        if not session:
            raise ValueError("Exam session not found")
        
        if session.status != 'paused':
            raise ValueError("Exam session is not paused")
        
        self.repo.update(session, status='running')
        
        return {
            'exam_id': session.id,
            'status': session.status,
        }
    
    def finish_exam(self, exam_id: int) -> Dict:
        """시험 종료"""
        session = self.repo.get_by_id(exam_id)
        if not session:
            raise ValueError("Exam session not found")
        
        self.repo.update(
            session,
            status='finished',
            ended_at=timezone.now(),
        )
        
        return {
            'exam_id': session.id,
            'status': session.status,
            'ended_at': session.ended_at.isoformat(),
            'total_answers': len(session.answers),
        }


class BrailleConversionService:
    """점자 변환 서비스"""
    
    def __init__(self):
        pass
    
    def convert_unit_to_braille(self, unit_id: int, subject: str = None) -> Dict:
        """
        단원을 점자로 변환
        과목별 전략 적용
        """
        try:
            unit = Unit.objects.get(id=unit_id)
        except Unit.DoesNotExist:
            raise ValueError(f"Unit {unit_id} not found")
        
        # 과목 자동 감지 (textbook.subject 사용)
        if not subject:
            subject = unit.textbook.subject or 'korean'
        
        # 과목명 정규화
        subject_lower = subject.lower()
        if '수학' in subject_lower or subject_lower == 'math':
            strategy = 'math'
        elif '국어' in subject_lower or subject_lower == 'korean':
            strategy = 'korean'
        elif '영어' in subject_lower or subject_lower == 'english':
            strategy = 'english'
        elif '과학' in subject_lower or subject_lower == 'science':
            strategy = 'science'
        elif '사회' in subject_lower or subject_lower == 'social':
            strategy = 'social'
        else:
            strategy = 'korean'  # 기본값
        
        # 기존 점자 데이터 확인
        existing = BrailleContent.objects.filter(
            unit=unit,
            strategy=strategy,
            status='completed'
        ).first()
        
        if existing:
            return {
                'unit_id': unit_id,
                'status': 'completed',
                'cells': existing.cells,
                'strategy': existing.strategy,
                'converted_at': existing.converted_at.isoformat() if existing.converted_at else None,
            }
        
        # 새 변환 시작
        braille_content, created = BrailleContent.objects.get_or_create(
            unit=unit,
            strategy=strategy,
            defaults={
                'status': 'converting',
                'cells': [],
            }
        )
        
        if not created and braille_content.status == 'converting':
            # 이미 변환 중이면 대기
            return {
                'unit_id': unit_id,
                'status': 'converting',
                'cells': [],
                'strategy': strategy,
            }
        
        # 점자 변환 (과목별 전략 적용)
        try:
            cells = self._convert_with_strategy(unit.content, strategy)
            
            # 변환 완료
            braille_content.cells = cells
            braille_content.status = 'completed'
            braille_content.converted_at = timezone.now()
            braille_content.error_message = ''
            braille_content.save()
            
            return {
                'unit_id': unit_id,
                'status': 'completed',
                'cells': cells,
                'strategy': strategy,
                'converted_at': braille_content.converted_at.isoformat(),
            }
        except Exception as e:
            # 변환 실패
            braille_content.status = 'failed'
            braille_content.error_message = str(e)
            braille_content.save()
            
            return {
                'unit_id': unit_id,
                'status': 'failed',
                'cells': [],
                'strategy': strategy,
                'error': str(e),
            }
    
    def _convert_with_strategy(self, text: str, strategy: str) -> List[List[int]]:
        """
        과목별 전략에 따라 텍스트를 점자로 변환
        """
        from utils.content_extractor import extract_formula, split_sentences, extract_keywords
        
        if strategy == 'math':
            # 수학: 수식 중심
            formula = extract_formula(text)
            if formula:
                # 수식만 점자로 변환
                return text_to_cells(formula)
            else:
                # 수식이 없으면 전체 텍스트 변환
                return text_to_cells(text)
        
        elif strategy == 'korean':
            # 국어: 문장 단위
            sentences = split_sentences(text)
            if sentences:
                # 각 문장을 점자로 변환하여 합침
                all_cells = []
                for sentence in sentences:
                    cells = text_to_cells(sentence)
                    all_cells.extend(cells)
                return all_cells
            else:
                return text_to_cells(text)
        
        elif strategy == 'english':
            # 영어: 단어/구절 단위 (일단 전체 변환)
            return text_to_cells(text)
        
        elif strategy in ['science', 'social']:
            # 과학/사회: 용어 중심 (일단 전체 변환)
            return text_to_cells(text)
        
        else:
            # 기본: 전체 텍스트 변환
            return text_to_cells(text)
    
    def convert_textbook_to_braille(self, textbook_id: int) -> Dict:
        """
        교재 전체를 점자로 변환
        """
        from .models import Textbook
        
        try:
            textbook = Textbook.objects.get(id=textbook_id)
        except Textbook.DoesNotExist:
            raise ValueError(f"Textbook {textbook_id} not found")
        
        units = textbook.units.all()
        results = []
        
        for unit in units:
            result = self.convert_unit_to_braille(unit.id, textbook.subject)
            results.append(result)
        
        return {
            'textbook_id': textbook_id,
            'total_units': len(units),
            'results': results,
        }
    
    def get_braille_status(self, unit_id: int) -> Optional[Dict]:
        """
        단원의 점자 변환 상태 조회
        """
        try:
            braille_content = BrailleContent.objects.filter(
                unit_id=unit_id
            ).order_by('-created_at').first()
            
            if not braille_content:
                return {
                    'unit_id': unit_id,
                    'status': 'pending',
                    'cells': [],
                    'strategy': None,
                }
            
            return {
                'unit_id': unit_id,
                'status': braille_content.status,
                'cells': braille_content.cells if braille_content.status == 'completed' else [],
                'strategy': braille_content.strategy,
                'converted_at': braille_content.converted_at.isoformat() if braille_content.converted_at else None,
                'error_message': braille_content.error_message if braille_content.status == 'failed' else None,
            }
        except Exception as e:
            return {
                'unit_id': unit_id,
                'status': 'error',
                'error': str(e),
            }

