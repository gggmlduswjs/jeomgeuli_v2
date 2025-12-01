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
        try:
            from apps.analytics.services import AnalyticsService
        except ImportError:
            AnalyticsService = None
        analytics_service = AnalyticsService()
        analytics_service.log_wrong_answer(
            question_id=question.id,
            wrong_answer=user_answer,
            correct_answer=question.correct_answer,
            pattern_type='user_mistake',
        )


class GraphAnalysisService:
    """그래프/도표 분석 비즈니스 로직 (CV + LLM Hybrid)"""
    
    def __init__(self, graph_repo: GraphTableRepository = None):
        self.repo = graph_repo or GraphTableRepository()
        self.cv_analyzer = None
        try:
            from .graph_cv_analyzer import GraphCVAnalyzer
            self.cv_analyzer = GraphCVAnalyzer()
        except Exception:
            # OpenCV가 없으면 CV 분석 스킵
            pass
    
    def analyze_graph(self, image_data: bytes, title: str = "", prompt: str = "") -> Dict:
        """
        그래프/도표 분석 및 패턴 추출 (CV + LLM Hybrid)
        
        Process:
        1. CV 기반 분석 (좌표계, 곡선, 막대, 점 데이터)
        2. LLM 기반 의미 보정 (CV 결과를 LLM에 전달하여 의미 보정)
        """
        # Step 1: CV 기반 분석
        cv_results = self._analyze_with_cv(image_data)
        
        # Step 2: LLM 기반 의미 보정
        patterns = self._refine_with_llm(image_data, cv_results, prompt)
        
        # DB에 저장
        graph_item = self.repo.create(
            title=title or "Graph Analysis",
            patterns=patterns,
        )
        
        return {
            'patterns': patterns,
            'cv_results': cv_results,  # CV 결과도 포함
            'item_id': graph_item.id,
        }
    
    def _analyze_with_cv(self, image_data: bytes) -> Dict:
        """CV 기반 그래프 분석"""
        if not self.cv_analyzer:
            return {
                'coordinate_system': {},
                'curves': [],
                'bars': [],
                'points': [],
                'intervals': [],
                'intersections': []
            }
        
        try:
            # 좌표계 감지
            coord_system = self.cv_analyzer.analyze_coordinate_system(image_data)
            
            # 곡선 데이터 추출
            curves = self.cv_analyzer.extract_curve_data(image_data)
            
            # 막대 데이터 추출
            bars = self.cv_analyzer.extract_bar_data(image_data)
            
            # 점 데이터 추출
            points = self.cv_analyzer.extract_point_data(image_data)
            
            # 증감 구간 분석
            intervals = self.cv_analyzer.analyze_intervals(curves)
            
            # 교점 찾기
            intersections = self.cv_analyzer.find_intersections(curves)
            
            return {
                'coordinate_system': coord_system,
                'curves': curves,
                'bars': bars,
                'points': points,
                'intervals': intervals,
                'intersections': intersections
            }
        except Exception as e:
            print(f"[GraphAnalysisService] CV 분석 실패: {e}")
            return {
                'coordinate_system': {},
                'curves': [],
                'bars': [],
                'points': [],
                'intervals': [],
                'intersections': []
            }
    
    def _refine_with_llm(self, image_data: bytes, cv_results: Dict, prompt: str = "") -> Dict:
        """LLM 기반 의미 보정"""
        from core.ai.factory import AIClientFactory
        from core.exceptions import AIAnalysisException
        
        ai_client = AIClientFactory.create(provider='gemini')
        
        if not ai_client or not hasattr(ai_client, 'analyze_image'):
            # LLM이 없으면 CV 결과를 기본 패턴으로 변환
            return self._cv_to_patterns(cv_results)
        
        # CV 결과를 텍스트로 요약
        cv_summary = self._summarize_cv_results(cv_results)
        
        analysis_prompt = prompt or f"""
이 그래프나 도표를 분석해주세요.

CV 분석 결과:
{cv_summary}

다음 정보를 추출해주세요:
1. 추세 (trend): increase | decrease | stable
2. 극값 (extremum): maximum | minimum | none
3. 주요 비교값 (comparison): greater | less | equal
4. 증감 구간 (intervals): 증가/감소 구간
5. 교점 (intersections): 곡선 교차점
6. 의미 설명 (semantic_description): 문제 해결에 필요한 정보

JSON 형식으로 반환해주세요:
{{
  "trend": "increase",
  "extremum": "maximum",
  "comparison": "greater",
  "intervals": [
    {{"type": "increase", "range": "0~2"}},
    {{"type": "decrease", "range": "2~5"}}
  ],
  "intersections": [
    {{"point": [2, 3], "description": "x=2에서 교차"}}
  ],
  "semantic_description": "이 함수는 x가 0에서 2까지 증가하다가 2에서 5까지 감소합니다."
}}
"""
        
        try:
            patterns = ai_client.analyze_image(image_data, analysis_prompt)
            
            # CV 결과와 병합
            if isinstance(patterns, dict):
                patterns['cv_data'] = cv_results
            else:
                patterns = {
                    'trend': 'stable',
                    'extremum': 'none',
                    'comparison': 'equal',
                    'cv_data': cv_results
                }
            
            return patterns
        except Exception as e:
            print(f"[GraphAnalysisService] LLM 분석 실패: {e}")
            # LLM 실패 시 CV 결과를 패턴으로 변환
            return self._cv_to_patterns(cv_results)
    
    def _summarize_cv_results(self, cv_results: Dict) -> str:
        """CV 결과를 텍스트로 요약"""
        summary_parts = []
        
        # 좌표계
        coord = cv_results.get('coordinate_system', {})
        if coord:
            summary_parts.append(f"좌표계: x축 {coord.get('x_axis', {}).get('min', 0)}~{coord.get('x_axis', {}).get('max', 0)}, y축 {coord.get('y_axis', {}).get('min', 0)}~{coord.get('y_axis', {}).get('max', 0)}")
        
        # 곡선
        curves = cv_results.get('curves', [])
        if curves:
            for i, curve in enumerate(curves):
                trend = curve.get('trend', 'unknown')
                extremum = curve.get('extremum')
                summary_parts.append(f"곡선 {i+1}: 추세={trend}, 극값={extremum}")
        
        # 구간
        intervals = cv_results.get('intervals', [])
        if intervals:
            interval_strs = [f"{iv['type']} ({iv.get('range', '')})" for iv in intervals]
            summary_parts.append(f"증감 구간: {', '.join(interval_strs)}")
        
        # 교점
        intersections = cv_results.get('intersections', [])
        if intersections:
            summary_parts.append(f"교점 {len(intersections)}개 발견")
        
        return '\n'.join(summary_parts) if summary_parts else "CV 분석 결과 없음"
    
    def _cv_to_patterns(self, cv_results: Dict) -> Dict:
        """CV 결과를 기본 패턴으로 변환"""
        patterns = {
            'trend': 'stable',
            'extremum': 'none',
            'comparison': 'equal',
            'cv_data': cv_results
        }
        
        # 곡선에서 추세 추출
        curves = cv_results.get('curves', [])
        if curves:
            first_curve = curves[0]
            patterns['trend'] = first_curve.get('trend', 'stable')
            extremum = first_curve.get('extremum')
            if extremum:
                patterns['extremum'] = extremum.get('type', 'none')
        
        # 구간 정보
        intervals = cv_results.get('intervals', [])
        if intervals:
            patterns['intervals'] = [
                {
                    'type': iv.get('type', 'stable'),
                    'range': iv.get('range', '')
                }
                for iv in intervals
            ]
        
        return patterns


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
        (기존 메서드 유지 - 하위 호환성)
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
    
    def convert_with_semantic_chunking(
        self,
        unit_id: int,
        subject: str = None,
        create_chunks: bool = True
    ) -> Dict:
        """
        의미 청킹을 사용한 점자 변환 (새로운 메서드)
        
        Args:
            unit_id: 단원 ID
            subject: 과목
            create_chunks: BrailleChunk 모델 생성 여부
        
        Returns:
            {
                'unit_id': unit_id,
                'status': 'completed',
                'cells': [...],
                'chunks': [...],  # 3-cell 패킷 리스트
                'strategy': strategy
            }
        """
        from .braille_encoding_engine import BrailleEncodingEngine
        from .models import Unit
        
        try:
            unit = Unit.objects.get(id=unit_id)
        except Unit.DoesNotExist:
            raise ValueError(f"Unit {unit_id} not found")
        
        # 과목 자동 감지
        if not subject:
            subject = unit.textbook.subject or 'korean'
        
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
            strategy = 'korean'
        
        # 기존 점자 데이터 확인
        existing = BrailleContent.objects.filter(
            unit=unit,
            strategy=strategy,
            status='completed'
        ).first()
        
        if existing and not create_chunks:
            return {
                'unit_id': unit_id,
                'status': 'completed',
                'cells': existing.cells,
                'strategy': existing.strategy,
            }
        
        # Braille Encoding Engine 사용
        encoding_engine = BrailleEncodingEngine()
        semantic_chunks = encoding_engine.encode_semantic_chunks(unit.content, strategy)
        
        # 모든 셀 수집
        all_cells = []
        for chunk in semantic_chunks:
            all_cells.extend(chunk['cells'])
        
        # BrailleContent 생성/업데이트
        braille_content, created = BrailleContent.objects.get_or_create(
            unit=unit,
            strategy=strategy,
            defaults={
                'status': 'converting',
                'cells': all_cells,
            }
        )
        
        if not created:
            braille_content.cells = all_cells
            braille_content.status = 'converting'
            braille_content.save()
        
        # BrailleChunk 생성
        chunks_data = []
        if create_chunks:
            chunks = encoding_engine.create_braille_chunks(
                braille_content,
                unit.content,
                strategy
            )
            chunks_data = [
                {
                    'id': chunk.id,
                    'chunk_index': chunk.chunk_index,
                    'cells': chunk.cells,
                    'semantic_type': chunk.semantic_type,
                    'original_text': chunk.original_text
                }
                for chunk in chunks
            ]
        
        # 변환 완료
        braille_content.status = 'completed'
        braille_content.converted_at = timezone.now()
        braille_content.error_message = ''
        braille_content.save()
        
        return {
            'unit_id': unit_id,
            'status': 'completed',
            'cells': all_cells,
            'chunks': chunks_data,
            'strategy': strategy,
            'converted_at': braille_content.converted_at.isoformat(),
        }
    
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

