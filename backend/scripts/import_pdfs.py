"""
PDF 교재 배치 임포트 스크립트
backend/data/pdfs/ 폴더의 모든 PDF 파일을 처리하여 Textbook/Unit 데이터로 변환

사용법:
    python scripts/import_pdfs.py           # 기본 모드 (패턴 매칭)
    python scripts/import_pdfs.py --ai     # AI 모드 (OpenAI API 기본, 환경변수로 변경 가능)
"""
import os
import sys
import django
from pathlib import Path
import PyPDF2
import re
import json

# Django 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeomgeuli_backend.settings')
django.setup()

from apps.exam.models import Textbook, Unit
from apps.exam.repositories import TextbookRepository, UnitRepository
from core.ai.factory import AIClientFactory

# PDF 폴더 경로
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "pdfs"


def extract_textbook_info(filename: str) -> dict:
    """
    파일명에서 교재 정보 추출
    예: "수능특강_국어_2024.pdf" → {title: "수능특강 국어", subject: "국어", year: 2024}
    """
    # 확장자 제거
    name = filename.replace('.pdf', '').replace('.PDF', '')
    
    # 패턴 매칭
    patterns = [
        r'(.+?)_(\w+)_(\d{4})',  # 수능특강_국어_2024
        r'(.+?)\s+(\w+)\s+(\d{4})',  # 수능특강 국어 2024
        r'(.+?)_(\d{4})',  # 수능특강_2024
        r'(.+?)\s+(\d{4})',  # 수능특강 2024
    ]
    
    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            if len(match.groups()) == 3:
                title, subject, year = match.groups()
                return {
                    'title': f"{title} {subject}",
                    'subject': subject,
                    'year': int(year),
                    'publisher': 'EBS'  # 기본값
                }
            elif len(match.groups()) == 2:
                title, year = match.groups()
                # year가 숫자인지 확인
                if year.isdigit():
                    return {
                        'title': title,
                        'subject': '',
                        'year': int(year),
                        'publisher': 'EBS'
                    }
                else:
                    # year가 과목일 수도 있음
                    return {
                        'title': f"{title} {year}",
                        'subject': year,
                        'year': None,
                        'publisher': 'EBS'
                    }
    
    # 매칭 실패 시 파일명을 그대로 사용
    return {
        'title': name,
        'subject': '',
        'year': None,
        'publisher': 'EBS'
    }


def extract_units_from_text(text: str, ai_client=None) -> list:
    """
    텍스트에서 단원 정보 추출
    AI를 사용하여 단원별로 분리 (선택적)
    """
    units = []
    
    # 간단한 패턴 매칭: "1단원", "제1장", "Chapter 1" 등
    unit_patterns = [
        r'(\d+)단원[:\s]+(.+?)(?=\d+단원|$|제\d+장|Chapter\s+\d+)',
        r'제(\d+)장[:\s]+(.+?)(?=제\d+장|$|\d+단원|Chapter\s+\d+)',
        r'Chapter\s+(\d+)[:\s]+(.+?)(?=Chapter\s+\d+|$|\d+단원|제\d+장)',
        r'제(\d+)과[:\s]+(.+?)(?=제\d+과|$|\d+단원)',
    ]
    
    for pattern in unit_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            order = int(match.group(1))
            content = match.group(2).strip()[:2000]  # 최대 2000자
            if content and len(content) > 50:  # 최소 50자 이상
                units.append({
                    'order': order,
                    'title': f"{order}단원",
                    'content': content
                })
    
    # 중복 제거 (order 기준)
    seen_orders = set()
    unique_units = []
    for unit in units:
        if unit['order'] not in seen_orders:
            seen_orders.add(unit['order'])
            unique_units.append(unit)
    units = sorted(unique_units, key=lambda x: x['order'])
    
    # AI를 사용한 더 정확한 추출 (선택적, 단원이 없을 때만)
    if ai_client and ai_client.is_available() and not units:
        try:
            prompt = f"""
다음 교재 텍스트를 단원별로 분리해주세요.
각 단원은 제목과 내용을 포함합니다.

텍스트:
{text[:5000]}  # 처음 5000자만

JSON 형식으로 반환:
[
  {{"order": 1, "title": "1단원: 제목", "content": "내용..."}},
  {{"order": 2, "title": "2단원: 제목", "content": "내용..."}}
]

단원이 명확하지 않으면 빈 배열 []을 반환하세요.
"""
            response = ai_client.generate_text(prompt)
            # JSON 파싱
            try:
                json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                if json_match:
                    parsed_units = json.loads(json_match.group())
                    if isinstance(parsed_units, list) and len(parsed_units) > 0:
                        units = parsed_units
            except json.JSONDecodeError:
                pass
        except Exception as e:
            print(f"  [경고] AI 추출 실패: {e}")
    
    return units


def process_pdf_file(pdf_path: Path, ai_client=None) -> dict:
    """
    PDF 파일 하나를 처리하여 Textbook/Unit 데이터 반환
    """
    print(f"\n처리 중: {pdf_path.name}")
    
    try:
        # PDF 읽기
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            page_count = len(pdf_reader.pages)
            
            print(f"  페이지 수: {page_count}")
            
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    # 진행 상황 표시 (10페이지마다)
                    if (i + 1) % 10 == 0:
                        print(f"  진행: {i + 1}/{page_count} 페이지")
                except Exception as e:
                    print(f"  [경고] 페이지 {i + 1} 추출 실패: {e}")
                    continue
        
        if not text.strip():
            print(f"  [오류] 텍스트를 추출할 수 없습니다")
            return None
        
        print(f"  추출된 텍스트 길이: {len(text)}자")
        
        # 교재 정보 추출
        textbook_info = extract_textbook_info(pdf_path.name)
        print(f"  교재명: {textbook_info['title']}")
        print(f"  과목: {textbook_info['subject']}")
        print(f"  연도: {textbook_info['year']}")
        
        # 단원 추출
        print(f"  단원 추출 중...")
        units = extract_units_from_text(text, ai_client)
        
        if not units:
            # 단원을 찾지 못한 경우 전체를 하나의 단원으로
            print(f"  [경고] 단원을 찾지 못했습니다. 전체를 하나의 단원으로 처리합니다.")
            units = [{
                'order': 1,
                'title': '전체',
                'content': text[:5000]  # 처음 5000자
            }]
        
        print(f"  추출된 단원 수: {len(units)}개")
        
        return {
            'textbook': textbook_info,
            'units': units,
            'text_length': len(text),
            'page_count': page_count
        }
        
    except PyPDF2.errors.PdfReadError as e:
        print(f"  [오류] PDF 파일이 손상되었거나 읽을 수 없습니다: {e}")
        return None
    except Exception as e:
        print(f"  [오류] 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def import_pdfs(use_ai: bool = False):
    """
    PDF 폴더의 모든 PDF 파일을 처리하여 데이터베이스에 저장
    """
    # PDF 폴더 확인
    if not PDF_DIR.exists():
        print(f"[오류] PDF 폴더가 없습니다: {PDF_DIR}")
        print(f"      폴더를 생성합니다...")
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        print(f"      폴더 생성 완료: {PDF_DIR}")
        print(f"      이 폴더에 PDF 파일을 넣고 다시 실행해주세요.")
        return
    
    # PDF 파일 목록
    pdf_files = list(PDF_DIR.glob("*.pdf")) + list(PDF_DIR.glob("*.PDF"))
    
    if not pdf_files:
        print(f"[오류] PDF 파일이 없습니다: {PDF_DIR}")
        print(f"      이 폴더에 PDF 파일을 넣어주세요.")
        return
    
    print(f"[시작] {len(pdf_files)}개 PDF 파일 처리 시작")
    print(f"      폴더: {PDF_DIR}")
    
    # AI 클라이언트 (선택적)
    ai_client = None
    if use_ai:
        # 환경변수에서 AI 제공자 확인 (기본값: openai)
        provider = os.getenv('DEFAULT_AI_PROVIDER', 'openai')
        provider_name = 'OpenAI (ChatGPT)' if provider == 'openai' else 'Gemini'
        print(f"[AI] {provider_name} API를 사용하여 단원 추출")
        ai_client = AIClientFactory.create(provider=provider)
        if not ai_client or not ai_client.is_available():
            print("[경고] AI 클라이언트를 사용할 수 없습니다. 기본 추출 방식 사용")
            ai_client = None
    else:
        print(f"[기본] 패턴 매칭 방식으로 단원 추출")
    
    # Repository
    textbook_repo = TextbookRepository()
    unit_repo = UnitRepository()
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for pdf_path in pdf_files:
        result = process_pdf_file(pdf_path, ai_client)
        
        if not result:
            error_count += 1
            continue
        
        # Textbook 생성 또는 조회
        try:
            textbook, created = Textbook.objects.get_or_create(
                title=result['textbook']['title'],
                year=result['textbook']['year'],
                defaults={
                    'publisher': result['textbook']['publisher'],
                    'subject': result['textbook']['subject'],
                }
            )
            
            if not created:
                print(f"  [-] {textbook.title} 이미 존재 (건너뜀)")
                skip_count += 1
                continue
            
            # Unit 생성
            unit_count = 0
            for unit_data in result['units']:
                Unit.objects.create(
                    textbook=textbook,
                    title=unit_data['title'],
                    order=unit_data['order'],
                    content=unit_data['content']
                )
                unit_count += 1
            
            print(f"  [OK] {textbook.title} 생성 완료 ({unit_count}개 단원)")
            success_count += 1
            
        except Exception as e:
            print(f"  [오류] 데이터베이스 저장 실패: {e}")
            error_count += 1
    
    print(f"\n[완료] 성공: {success_count}개, 건너뜀: {skip_count}개, 오류: {error_count}개")
    
    if success_count > 0:
        print(f"\n[안내] Textbook 페이지에서 확인할 수 있습니다.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='PDF 교재 배치 임포트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python scripts/import_pdfs.py           # 기본 모드 (패턴 매칭)
  python scripts/import_pdfs.py --ai     # AI 모드 (OpenAI API 기본, 환경변수로 변경 가능)
  
파일명 규칙:
  - 수능특강_국어_2024.pdf
  - 수능특강_수학_2024.pdf
  - 교재명_과목_연도.pdf 형식 권장
  
AI 제공자 설정:
  - 기본값: OpenAI (ChatGPT)
  - 환경변수 DEFAULT_AI_PROVIDER=gemini 로 Gemini 사용 가능
        """
    )
    parser.add_argument('--ai', action='store_true', 
                       help='AI를 사용하여 단원 추출 (기본: OpenAI, 환경변수로 변경 가능)')
    
    args = parser.parse_args()
    
    import_pdfs(use_ai=args.ai)


