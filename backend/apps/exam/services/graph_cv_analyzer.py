"""
그래프 CV 분석 모듈
OpenCV 기반 그래프 이미지 분석 (좌표계, 곡선, 막대, 점 데이터 추출)
"""
from typing import Dict, List, Optional, Tuple
import io
import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

from core.exceptions import AIAnalysisException


class GraphCVAnalyzer:
    """그래프 CV 분석기"""
    
    def __init__(self):
        if not OPENCV_AVAILABLE:
            raise AIAnalysisException(
                'OpenCV가 설치되지 않았습니다',
                user_message='그래프 분석 라이브러리가 설치되지 않았습니다.'
            )
    
    def analyze_coordinate_system(self, image_data: bytes) -> Dict:
        """
        좌표계 감지
        Returns:
            {
                'x_axis': {'min': 0, 'max': 10, 'label': 'x'},
                'y_axis': {'min': 0, 'max': 100, 'label': 'y'},
                'origin': {'x': 50, 'y': 200},
                'grid_lines': [...]
            }
        """
        if not OPENCV_AVAILABLE:
            return self._default_coordinate_system()
        
        try:
            # 이미지 로드
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 엣지 검출
            edges = cv2.Canny(gray, 50, 150)
            
            # 직선 검출 (Hough Transform)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)
            
            # 좌표축 추정 (수평/수직 선)
            x_axis_lines = []
            y_axis_lines = []
            
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    # 수평선 (x축)
                    if abs(y1 - y2) < 10:
                        x_axis_lines.append((x1, y1, x2, y2))
                    # 수직선 (y축)
                    elif abs(x1 - x2) < 10:
                        y_axis_lines.append((x1, y1, x2, y2))
            
            # 기본 좌표계 정보 반환
            height, width = gray.shape
            return {
                'x_axis': {
                    'min': 0,
                    'max': width,
                    'label': 'x',
                    'position': height - 50  # 하단에서 50픽셀 위
                },
                'y_axis': {
                    'min': 0,
                    'max': height,
                    'label': 'y',
                    'position': 50  # 왼쪽에서 50픽셀 오른쪽
                },
                'origin': {'x': 50, 'y': height - 50},
                'grid_lines': len(x_axis_lines) + len(y_axis_lines)
            }
        except Exception as e:
            # 실패 시 기본값 반환
            return self._default_coordinate_system()
    
    def extract_curve_data(self, image_data: bytes) -> List[Dict]:
        """
        곡선 데이터 추출
        Returns:
            [
                {
                    'type': 'curve',
                    'points': [(x1, y1), (x2, y2), ...],
                    'trend': 'increase' | 'decrease' | 'stable',
                    'extremum': {'type': 'maximum' | 'minimum', 'point': (x, y)}
                },
                ...
            ]
        """
        if not OPENCV_AVAILABLE:
            return []
        
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 컨투어 검출
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            curves = []
            for contour in contours:
                if len(contour) > 10:  # 충분한 점이 있는 경우만
                    points = [(int(p[0][0]), int(p[0][1])) for p in contour]
                    
                    # 추세 분석
                    trend = self._analyze_trend(points)
                    
                    # 극값 찾기
                    extremum = self._find_extremum(points)
                    
                    curves.append({
                        'type': 'curve',
                        'points': points[:50],  # 최대 50개 점만
                        'trend': trend,
                        'extremum': extremum
                    })
            
            return curves
        except Exception as e:
            return []
    
    def extract_bar_data(self, image_data: bytes) -> List[Dict]:
        """
        막대 그래프 데이터 추출
        Returns:
            [
                {
                    'type': 'bar',
                    'x': 100,
                    'y': 150,
                    'width': 50,
                    'height': 200,
                    'value': 75
                },
                ...
            ]
        """
        if not OPENCV_AVAILABLE:
            return []
        
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 직사각형 검출
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            bars = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # 막대 그래프는 일반적으로 높이가 넓이보다 큼
                if h > w * 1.5 and w > 10 and h > 20:
                    bars.append({
                        'type': 'bar',
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'value': h  # 높이를 값으로 추정
                    })
            
            return bars
        except Exception as e:
            return []
    
    def extract_point_data(self, image_data: bytes) -> List[Dict]:
        """
        점 데이터 추출 (산점도)
        Returns:
            [
                {
                    'type': 'point',
                    'x': 100,
                    'y': 150,
                    'value': (x_val, y_val)
                },
                ...
            ]
        """
        if not OPENCV_AVAILABLE:
            return []
        
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 원형 검출 (HoughCircles)
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=20,
                param1=50,
                param2=30,
                minRadius=5,
                maxRadius=50
            )
            
            points = []
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for circle in circles[0, :]:
                    x, y, r = circle
                    points.append({
                        'type': 'point',
                        'x': int(x),
                        'y': int(y),
                        'radius': int(r),
                        'value': (x, y)  # 실제 값은 좌표계 변환 필요
                    })
            
            return points
        except Exception as e:
            return []
    
    def analyze_intervals(self, curves: List[Dict]) -> List[Dict]:
        """
        증감 구간 분석
        Returns:
            [
                {
                    'type': 'increase' | 'decrease' | 'stable',
                    'start': (x1, y1),
                    'end': (x2, y2),
                    'range': '0~2'
                },
                ...
            ]
        """
        intervals = []
        
        for curve in curves:
            points = curve.get('points', [])
            if len(points) < 2:
                continue
            
            # 점들을 x 좌표로 정렬
            sorted_points = sorted(points, key=lambda p: p[0])
            
            current_interval = None
            for i in range(len(sorted_points) - 1):
                p1 = sorted_points[i]
                p2 = sorted_points[i + 1]
                
                # 추세 판단
                if p2[1] < p1[1]:  # y가 감소 = 증가 추세 (그래프는 위로 올라감)
                    interval_type = 'increase'
                elif p2[1] > p1[1]:  # y가 증가 = 감소 추세
                    interval_type = 'decrease'
                else:
                    interval_type = 'stable'
                
                if current_interval is None or current_interval['type'] != interval_type:
                    if current_interval:
                        intervals.append(current_interval)
                    current_interval = {
                        'type': interval_type,
                        'start': p1,
                        'end': p2,
                        'range': f"{p1[0]}~{p2[0]}"
                    }
                else:
                    current_interval['end'] = p2
                    current_interval['range'] = f"{current_interval['start'][0]}~{p2[0]}"
            
            if current_interval:
                intervals.append(current_interval)
        
        return intervals
    
    def find_intersections(self, curves: List[Dict]) -> List[Dict]:
        """
        교점 찾기
        Returns:
            [
                {
                    'point': (x, y),
                    'curves': [0, 1]  # 교차하는 곡선 인덱스
                },
                ...
            ]
        """
        intersections = []
        
        # 간단한 구현: 두 곡선의 점들 중 가장 가까운 점 찾기
        for i in range(len(curves)):
            for j in range(i + 1, len(curves)):
                curve1_points = curves[i].get('points', [])
                curve2_points = curves[j].get('points', [])
                
                # 각 점 쌍의 거리 계산
                min_dist = float('inf')
                closest_pair = None
                
                for p1 in curve1_points:
                    for p2 in curve2_points:
                        dist = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
                        if dist < min_dist and dist < 10:  # 10픽셀 이내
                            min_dist = dist
                            closest_pair = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
                
                if closest_pair:
                    intersections.append({
                        'point': closest_pair,
                        'curves': [i, j]
                    })
        
        return intersections
    
    def _analyze_trend(self, points: List[Tuple[int, int]]) -> str:
        """추세 분석"""
        if len(points) < 2:
            return 'stable'
        
        # y 좌표 변화량 분석
        y_values = [p[1] for p in points]
        if y_values[0] > y_values[-1]:
            return 'increase'  # y가 감소 = 그래프가 위로 올라감
        elif y_values[0] < y_values[-1]:
            return 'decrease'
        else:
            return 'stable'
    
    def _find_extremum(self, points: List[Tuple[int, int]]) -> Optional[Dict]:
        """극값 찾기"""
        if len(points) < 3:
            return None
        
        y_values = [p[1] for p in points]
        max_idx = np.argmin(y_values)  # y가 최소 = 그래프 최대값
        min_idx = np.argmax(y_values)  # y가 최대 = 그래프 최소값
        
        if max_idx != 0 and max_idx != len(points) - 1:
            return {
                'type': 'maximum',
                'point': points[max_idx]
            }
        elif min_idx != 0 and min_idx != len(points) - 1:
            return {
                'type': 'minimum',
                'point': points[min_idx]
            }
        
        return None
    
    def _default_coordinate_system(self) -> Dict:
        """기본 좌표계 정보"""
        return {
            'x_axis': {'min': 0, 'max': 100, 'label': 'x'},
            'y_axis': {'min': 0, 'max': 100, 'label': 'y'},
            'origin': {'x': 0, 'y': 0},
            'grid_lines': 0
        }

