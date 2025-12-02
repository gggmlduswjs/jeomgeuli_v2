"""
그래프 분석 관련 뷰
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .. import exam_services
from core.decorators import handle_api_errors
from core.exceptions import ValidationException

GraphAnalysisService = exam_services.GraphAnalysisService


@csrf_exempt
@handle_api_errors
def analyze_graph(request):
    """그래프/도표 분석 및 패턴 추출"""
    if request.method != 'POST':
        raise ValidationException('POST만 지원', user_message='POST 요청만 지원됩니다.')
    
    image_file = request.FILES.get('image')
    title = request.POST.get('title', '')
    
    if not image_file:
        raise ValidationException(
            '이미지 파일이 필요합니다',
            user_message='그래프 이미지 파일을 업로드해주세요.'
        )
    
    # 이미지 데이터 읽기
    image_data = image_file.read()
    
    service = GraphAnalysisService()
    result = service.analyze_graph(image_data, title)
    
    return JsonResponse({
        'ok': True,
        **result,
    })

