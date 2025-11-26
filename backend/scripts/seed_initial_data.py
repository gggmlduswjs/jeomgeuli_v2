"""
초기 데이터 시드 스크립트
샘플 교재, 문제, 어휘 데이터 생성
"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeomgeuli_backend.settings')
django.setup()

from apps.exam.models import Textbook, Unit, Question
from apps.vocab.models import Vocabulary, VocabQueue, SisaWord
from apps.analytics.models import BrailleSpeedLog
from datetime import date


def seed_textbooks():
    """샘플 교재 데이터 생성"""
    print("교재 데이터 생성 중...")
    
    textbooks_data = [
        {
            'title': '수능특강 국어',
            'publisher': 'EBS',
            'year': 2024,
            'subject': '국어',
            'units': [
                {'title': '1단원: 현대시', 'order': 1, 'content': '현대시의 특징과 주요 작품 분석. 시적 화자의 정서와 표현 기법을 중심으로 학습합니다.'},
                {'title': '2단원: 고전시가', 'order': 2, 'content': '고전시가의 이해와 감상. 고전 문학의 미적 가치와 현대적 의미를 탐구합니다.'},
                {'title': '3단원: 현대소설', 'order': 3, 'content': '현대소설의 구조와 주제. 인물, 사건, 배경의 관계를 통해 작품을 분석합니다.'},
                {'title': '4단원: 고전소설', 'order': 4, 'content': '고전소설의 서사 구조와 주제 의식. 전통적 서사 기법을 학습합니다.'},
                {'title': '5단원: 수필', 'order': 5, 'content': '수필의 특성과 표현 기법. 작가의 사상과 감정을 담은 글쓰기를 이해합니다.'},
            ]
        },
        {
            'title': '수능특강 수학',
            'publisher': 'EBS',
            'year': 2024,
            'subject': '수학',
            'units': [
                {'title': '1단원: 함수', 'order': 1, 'content': '함수의 개념과 성질. 일대일 대응, 합성함수, 역함수를 학습합니다.'},
                {'title': '2단원: 미적분', 'order': 2, 'content': '미분과 적분의 기본 개념. 도함수와 부정적분, 정적분의 활용을 다룹니다.'},
                {'title': '3단원: 확률과 통계', 'order': 3, 'content': '확률의 기본 개념과 통계적 분석. 조건부 확률과 이항분포를 학습합니다.'},
            ]
        },
        {
            'title': '수능특강 영어',
            'publisher': 'EBS',
            'year': 2024,
            'subject': '영어',
            'units': [
                {'title': '1단원: 문법', 'order': 1, 'content': '영어 문법의 핵심 개념. 시제, 조동사, 수동태 등을 학습합니다.'},
                {'title': '2단원: 독해', 'order': 2, 'content': '영문 독해 전략. 주제 파악, 세부 정보 이해, 추론 능력을 기릅니다.'},
            ]
        },
        {
            'title': '수능특강 한국사',
            'publisher': 'EBS',
            'year': 2024,
            'subject': '한국사',
            'units': [
                {'title': '1단원: 선사시대', 'order': 1, 'content': '한반도의 선사시대와 고대 국가의 형성 과정을 학습합니다.'},
                {'title': '2단원: 고려시대', 'order': 2, 'content': '고려의 정치, 경제, 사회, 문화를 종합적으로 이해합니다.'},
            ]
        },
        {
            'title': '수능특강 사회문화',
            'publisher': 'EBS',
            'year': 2024,
            'subject': '사회문화',
            'units': [
                {'title': '1단원: 사회와 문화', 'order': 1, 'content': '사회와 문화의 개념, 사회화 과정, 문화의 특성을 학습합니다.'},
                {'title': '2단원: 사회 구조', 'order': 2, 'content': '사회 계층, 사회 집단, 사회 제도의 이해를 다룹니다.'},
            ]
        },
    ]
    
    created_count = 0
    for textbook_data in textbooks_data:
        units_data = textbook_data.pop('units')
        textbook, created = Textbook.objects.get_or_create(
            title=textbook_data['title'],
            defaults=textbook_data
        )
        
        if created:
            for unit_data in units_data:
                Unit.objects.create(
                    textbook=textbook,
                    **unit_data
                )
            created_count += 1
            print(f"  [OK] {textbook.title} 생성 완료 ({len(units_data)}개 단원)")
        else:
            print(f"  [-] {textbook.title} 이미 존재")
    
    print(f"총 {created_count}개 교재 생성 완료")


def seed_questions():
    """샘플 문제 데이터 생성"""
    print("문제 데이터 생성 중...")
    
    questions_data = [
        {
            'question_text': '다음 시의 화자의 심경을 가장 잘 나타낸 것은?',
            'choice1': '기쁨',
            'choice2': '슬픔',
            'choice3': '그리움',
            'choice4': '분노',
            'choice5': '두려움',
            'correct_answer': 3,
            'explanation': '시의 전체적인 분위기와 화자의 감정을 종합적으로 고려하면 그리움이 가장 적절합니다.',
            'difficulty': 2,
            'subject': '국어',
        },
        {
            'question_text': '다음 중 함수 f(x) = x² + 2x + 1의 최솟값은?',
            'choice1': '0',
            'choice2': '1',
            'choice3': '-1',
            'choice4': '2',
            'choice5': '-2',
            'correct_answer': 1,
            'explanation': 'f(x) = (x+1)²이므로 최솟값은 x=-1일 때 0입니다.',
            'difficulty': 2,
            'subject': '수학',
        },
        {
            'question_text': '다음 중 영어 문장 "I have been studying"의 시제는?',
            'choice1': '현재시제',
            'choice2': '과거시제',
            'choice3': '현재완료진행시제',
            'choice4': '과거완료시제',
            'choice5': '미래시제',
            'correct_answer': 3,
            'explanation': 'have been + -ing 형태는 현재완료진행시제입니다.',
            'difficulty': 1,
            'subject': '영어',
        },
        {
            'question_text': '고려시대의 대표적인 불교 사찰은?',
            'choice1': '불국사',
            'choice2': '해인사',
            'choice3': '부석사',
            'choice4': '석굴암',
            'choice5': '법주사',
            'correct_answer': 2,
            'explanation': '해인사는 고려시대에 대장경을 보관한 대표적인 사찰입니다.',
            'difficulty': 2,
            'subject': '한국사',
        },
        {
            'question_text': '사회화 과정에서 가장 중요한 기관은?',
            'choice1': '학교',
            'choice2': '가족',
            'choice3': '종교',
            'choice4': '직장',
            'choice5': '미디어',
            'correct_answer': 2,
            'explanation': '가족은 1차 사회화의 핵심 기관으로 가장 중요한 역할을 합니다.',
            'difficulty': 1,
            'subject': '사회문화',
        },
    ]
    
    created_count = 0
    for q_data in questions_data:
        subject = q_data.pop('subject')
        textbook = Textbook.objects.filter(subject=subject).first()
        if not textbook:
            continue
        
        unit = Unit.objects.filter(textbook=textbook).first()
        if not unit:
            continue
        
        question, created = Question.objects.get_or_create(
            question_text=q_data['question_text'],
            defaults={
                'unit': unit,
                **q_data
            }
        )
        
        if created:
            created_count += 1
    
    print(f"  [OK] {created_count}개 문제 생성 완료")


def seed_vocab():
    """샘플 어휘 데이터 생성"""
    print("어휘 데이터 생성 중...")
    
    vocab_words = [
        {'word': '추상', 'meaning': '구체적인 형태나 내용이 없는 것', 'example': '추상적인 개념을 구체적으로 설명하기 어렵다.', 'difficulty': 2, 'category': '문학'},
        {'word': '구체', 'meaning': '실제로 존재하거나 경험할 수 있는 것', 'example': '구체적인 예시를 들어 설명하겠습니다.', 'difficulty': 1, 'category': '일반'},
        {'word': '함축', 'meaning': '표면적으로 드러나지 않은 깊은 의미를 포함함', 'example': '이 시는 깊은 함축적 의미를 담고 있다.', 'difficulty': 3, 'category': '문학'},
        {'word': '상징', 'meaning': '어떤 의미나 개념을 나타내는 표시나 기호', 'example': '장미는 사랑의 상징이다.', 'difficulty': 2, 'category': '문학'},
        {'word': '은유', 'meaning': '직접적으로 말하지 않고 비유를 통해 의미를 전달하는 표현법', 'example': '그의 목소리는 꿀처럼 달콤하다는 은유적 표현이다.', 'difficulty': 2, 'category': '문학'},
        {'word': '직유', 'meaning': '비유를 사용하되 "~처럼", "~같이" 등의 비유어를 사용하는 표현법', 'example': '그는 사자처럼 용맹하다는 직유적 표현이다.', 'difficulty': 2, 'category': '문학'},
        {'word': '의인', 'meaning': '사람이 아닌 것을 사람처럼 표현하는 수사법', 'example': '바람이 노래한다는 의인법 표현이다.', 'difficulty': 2, 'category': '문학'},
        {'word': '대조', 'meaning': '두 대상을 비교하여 차이를 드러내는 표현법', 'example': '밝음과 어둠의 대조를 통해 주제를 강조한다.', 'difficulty': 2, 'category': '문학'},
        {'word': '반복', 'meaning': '같은 말이나 표현을 되풀이하는 수사법', 'example': '반복을 통해 강조 효과를 얻는다.', 'difficulty': 1, 'category': '문학'},
        {'word': '점층', 'meaning': '점점 강해지거나 약해지는 순서로 배열하는 표현법', 'example': '점층법을 통해 긴장감을 높인다.', 'difficulty': 2, 'category': '문학'},
        {'word': '도함수', 'meaning': '함수의 미분계수를 함수로 나타낸 것', 'example': 'f(x) = x²의 도함수는 f\'(x) = 2x이다.', 'difficulty': 3, 'category': '수학'},
        {'word': '적분', 'meaning': '미분의 역연산으로, 함수의 면적을 구하는 연산', 'example': '적분을 통해 곡선 아래의 넓이를 구할 수 있다.', 'difficulty': 3, 'category': '수학'},
        {'word': '확률', 'meaning': '어떤 사건이 일어날 가능성을 수치로 나타낸 것', 'example': '동전을 던졌을 때 앞면이 나올 확률은 1/2이다.', 'difficulty': 2, 'category': '수학'},
        {'word': '통계', 'meaning': '데이터를 수집하고 분석하여 일반적인 경향을 파악하는 학문', 'example': '통계를 통해 데이터의 패턴을 발견할 수 있다.', 'difficulty': 2, 'category': '수학'},
        {'word': '사회화', 'meaning': '개인이 사회의 가치와 규범을 내면화하는 과정', 'example': '사회화를 통해 개인은 사회의 구성원이 된다.', 'difficulty': 2, 'category': '사회'},
        {'word': '문화', 'meaning': '한 사회의 구성원들이 공유하는 가치, 규범, 생활양식', 'example': '문화는 사회의 정체성을 형성한다.', 'difficulty': 1, 'category': '사회'},
        {'word': '계층', 'meaning': '사회적 지위나 경제적 수준에 따라 구분되는 집단', 'example': '사회 계층은 경제적 불평등과 관련이 있다.', 'difficulty': 2, 'category': '사회'},
        {'word': '제도', 'meaning': '사회의 안정과 질서를 유지하기 위한 규칙과 관행', 'example': '법률 제도는 사회 질서를 유지한다.', 'difficulty': 2, 'category': '사회'},
        {'word': 'present perfect', 'meaning': '현재완료시제: 과거의 행동이 현재까지 영향을 미치는 시제', 'example': 'I have finished my homework.', 'difficulty': 2, 'category': '영어'},
        {'word': 'passive voice', 'meaning': '수동태: 주어가 행동을 받는 형태', 'example': 'The book was written by him.', 'difficulty': 2, 'category': '영어'},
    ]
    
    created_count = 0
    for vocab_data in vocab_words:
        vocab, created = Vocabulary.objects.get_or_create(
            word=vocab_data['word'],
            defaults=vocab_data
        )
        if created:
            created_count += 1
    
    print(f"  [OK] {created_count}개 어휘 생성 완료")
    
    # 오늘의 어휘 큐 생성
    today = date.today()
    vocab_list = Vocabulary.objects.all()[:10]
    queue_count = 0
    
    for idx, vocab in enumerate(vocab_list, 1):
        queue, created = VocabQueue.objects.get_or_create(
            vocab=vocab,
            date=today,
            defaults={'order': idx}
        )
        if created:
            queue_count += 1
    
    print(f"  [OK] {queue_count}개 어휘 큐 항목 생성 완료")


def seed_sisa():
    """샘플 시사 용어 데이터 생성"""
    print("시사 용어 데이터 생성 중...")
    
    sisa_words = [
        {
            'word': '디플레이션',
            'meaning': '물가가 지속적으로 하락하는 현상',
            'context': '경기 침체로 인한 디플레이션 우려가 커지고 있다.',
            'source': '경제 용어',
        },
        {
            'word': '인플레이션',
            'meaning': '물가가 지속적으로 상승하는 현상',
            'context': '원유 가격 상승으로 인플레이션 압력이 증가했다.',
            'source': '경제 용어',
        },
        {
            'word': '디지털 전환',
            'meaning': '아날로그 방식에서 디지털 방식으로 전환하는 과정',
            'context': '코로나19로 인해 디지털 전환이 가속화되었다.',
            'source': 'IT 용어',
        },
        {
            'word': '탄소 중립',
            'meaning': '이산화탄소 배출량과 흡수량을 같게 만드는 것',
            'context': '2050년 탄소 중립 목표를 달성하기 위한 노력이 진행 중이다.',
            'source': '환경 용어',
        },
        {
            'word': '메타버스',
            'meaning': '가상과 현실이 결합된 3차원 가상 공간',
            'context': '메타버스 플랫폼이 새로운 비즈니스 모델로 주목받고 있다.',
            'source': 'IT 용어',
        },
        {
            'word': '블록체인',
            'meaning': '분산 원장 기술로 거래 기록을 안전하게 저장하는 시스템',
            'context': '블록체인 기술이 금융 분야에 혁신을 가져오고 있다.',
            'source': 'IT 용어',
        },
        {
            'word': 'ESG',
            'meaning': '환경(Environment), 사회(Social), 지배구조(Governance)를 고려한 경영',
            'context': 'ESG 경영이 기업의 지속가능성을 평가하는 기준이 되고 있다.',
            'source': '경영 용어',
        },
        {
            'word': 'K-콘텐츠',
            'meaning': '한국에서 제작된 영화, 드라마, 음악 등의 문화 콘텐츠',
            'context': 'K-콘텐츠가 전 세계적으로 큰 인기를 끌고 있다.',
            'source': '문화 용어',
        },
        {
            'word': '양극화',
            'meaning': '사회가 극단적으로 두 갈래로 나뉘는 현상',
            'context': '소득 양극화가 심화되면서 사회 갈등이 커지고 있다.',
            'source': '사회 용어',
        },
        {
            'word': '포용 성장',
            'meaning': '모든 구성원이 성장의 혜택을 공유하는 성장 방식',
            'context': '포용 성장을 통해 사회 통합을 이루어야 한다.',
            'source': '경제 용어',
        },
    ]
    
    created_count = 0
    for sisa_data in sisa_words:
        sisa, created = SisaWord.objects.get_or_create(
            word=sisa_data['word'],
            defaults=sisa_data
        )
        if created:
            created_count += 1
    
    print(f"  [OK] {created_count}개 시사 용어 생성 완료")


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("초기 데이터 시드 시작")
    print("=" * 50)
    
    seed_textbooks()
    seed_questions()
    seed_vocab()
    seed_sisa()
    
    print("=" * 50)
    print("초기 데이터 시드 완료")
    print("=" * 50)


if __name__ == '__main__':
    main()

