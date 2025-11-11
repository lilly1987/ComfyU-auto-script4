# -*- coding: utf-8 -*-
"""
태그 처리 관련 공용 유틸리티 함수
"""
import re
import yaml
import os

def normalize_tag(tag):
    """
    태그를 정규화합니다. 언더스코어를 공백으로 변환하고 소문자로 변환합니다.
    
    Args:
        tag: 정규화할 태그 문자열
    
    Returns:
        정규화된 태그 문자열 (소문자, 언더스코어를 공백으로 변환, 여러 공백 통일)
    """
    if not tag:
        return ''
    # 언더스코어를 공백으로 변환 후 소문자로 변환
    normalized = tag.replace('_', ' ').lower()
    # 여러 공백을 하나로 통일
    normalized = ' '.join(normalized.split())
    return normalized

def is_tag_excluded(tag, excluded_patterns):
    """
    태그가 제외 패턴에 해당하는지 확인합니다.
    정규식 패턴과 문자열 패턴을 모두 지원합니다.
    
    Args:
        tag: 확인할 태그 문자열
        excluded_patterns: 제외 패턴 리스트 (문자열 또는 정규식 패턴)
    
    Returns:
        제외되어야 하면 True, 아니면 False
    """
    normalized_tag = normalize_tag(tag)
    
    for pattern in excluded_patterns:
        # re.Pattern 객체인 경우 (컴파일된 정규식)
        if isinstance(pattern, re.Pattern):
            if pattern.search(normalized_tag):
                return True
        # 문자열이 "/.../" 형태로 시작하고 끝나는 경우 (정규식 패턴)
        elif isinstance(pattern, str) and pattern.startswith('/') and pattern.endswith('/'):
            try:
                regex_pattern = pattern[1:-1]  # 앞뒤 '/' 제거
                if re.search(regex_pattern, normalized_tag, re.IGNORECASE):
                    return True
            except re.error:
                # 정규식 오류 발생 시 문자열로 처리
                if normalize_tag(pattern[1:-1]) == normalized_tag:
                    return True
        # 일반 문자열인 경우
        else:
            if normalize_tag(pattern) == normalized_tag:
                return True
    
    return False

def load_excluded_tags(yml_path=None):
    """
    config.yml 파일에서 제외 태그 목록을 로드합니다.
    
    Args:
        yml_path: yml 파일 경로 (None이면 스크립트 디렉토리의 config.yml 사용)
    
    Returns:
        제외 태그 목록 리스트
    """
    if yml_path is None:
        # 스크립트 파일이 있는 디렉토리 기준으로 config.yml 찾기
        script_dir = os.path.dirname(os.path.abspath(__file__))
        yml_path = os.path.join(script_dir, 'config.yml')
    
    if not os.path.exists(yml_path):
        print(f"  경고: config.yml 파일이 존재하지 않습니다: {yml_path}")
        return []
    
    try:
        with open(yml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'excluded_tags' in data:
                return data['excluded_tags']
            else:
                print(f"  경고: config.yml에 'excluded_tags' 키가 없습니다.")
                return []
    except Exception as e:
        print(f"  오류: config.yml 파일 읽기 실패: {e}")
        return []

def load_dress_tags(yml_path=None):
    """
    config.yml 파일에서 dress 태그 목록을 로드합니다.
    
    Args:
        yml_path: yml 파일 경로 (None이면 스크립트 디렉토리의 config.yml 사용)
    
    Returns:
        dress 태그 목록 리스트
    """
    if yml_path is None:
        # 스크립트 파일이 있는 디렉토리 기준으로 config.yml 찾기
        script_dir = os.path.dirname(os.path.abspath(__file__))
        yml_path = os.path.join(script_dir, 'config.yml')
    
    if not os.path.exists(yml_path):
        print(f"  경고: config.yml 파일이 존재하지 않습니다: {yml_path}")
        return []
    
    try:
        with open(yml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'dress_tags' in data:
                return data['dress_tags']
            else:
                return []
    except Exception as e:
        print(f"  오류: config.yml 파일 읽기 실패: {e}")
        return []

def load_config(yml_path=None):
    """
    config.yml 파일에서 설정을 로드합니다.
    
    Args:
        yml_path: yml 파일 경로 (None이면 스크립트 디렉토리의 config.yml 사용)
    
    Returns:
        설정 딕셔너리
    """
    if yml_path is None:
        # 스크립트 파일이 있는 디렉토리 기준으로 config.yml 찾기
        script_dir = os.path.dirname(os.path.abspath(__file__))
        yml_path = os.path.join(script_dir, 'config.yml')
    
    if not os.path.exists(yml_path):
        print(f"  경고: config.yml 파일이 존재하지 않습니다: {yml_path}")
        return {}
    
    try:
        with open(yml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if data else {}
    except Exception as e:
        print(f"  오류: config.yml 파일 읽기 실패: {e}")
        return {}

def extract_dress_tags_from_string(tag_string, dress_tags):
    """
    태그 문자열에서 dress 태그를 추출합니다.
    중복을 제거하고 정규화된 태그로 확인합니다.
    
    Args:
        tag_string: 쉼표로 구분된 태그 문자열
        dress_tags: dress 태그 목록
    
    Returns:
        추출된 dress 태그 리스트 (중복 제거됨)
    """
    if not tag_string or not tag_string.strip() or not dress_tags:
        return []
    
    # 쉼표로 분리하여 태그 리스트 만들기
    tags = [tag.strip() for tag in tag_string.split(',')]
    
    # dress 태그 추출 (중복 제거)
    dress_tag_list = []
    seen_normalized = set()  # 정규화된 태그를 추적하여 중복 제거
    
    for tag in tags:
        if not tag:
            continue
        if is_tag_excluded(tag, dress_tags):  # dress_tags에 해당하는 태그
            normalized = normalize_tag(tag)
            if normalized not in seen_normalized:
                seen_normalized.add(normalized)
                dress_tag_list.append(tag)  # 원본 태그 유지
    
    return dress_tag_list

def remove_excluded_tags_from_string(tag_string, excluded_tags, dress_tags=None):
    """
    태그 문자열에서 제외 태그와 중복 태그를 제거합니다.
    dress 태그도 제거할 수 있습니다.
    
    Args:
        tag_string: 쉼표로 구분된 태그 문자열 (예: "1girl, 2d, belt, smile")
        excluded_tags: 제외 태그 목록
        dress_tags: dress 태그 목록 (제거할 태그, None이면 제거 안함)
    
    Returns:
        (필터링된 태그 문자열, 제거된 태그 개수)
    """
    if not tag_string or not tag_string.strip():
        return tag_string, 0
    
    # 쉼표로 분리하여 태그 리스트 만들기
    tags = [tag.strip() for tag in tag_string.split(',')]
    
    # 빈 태그 제거 및 제외 태그 필터링, 중복 제거
    filtered_tags = []
    seen_normalized = set()  # 정규화된 태그를 추적하여 중복 제거
    removed_count = 0
    
    for tag in tags:
        if not tag:  # 빈 태그는 제거
            continue
        
        # 제외 태그인지 확인
        if is_tag_excluded(tag, excluded_tags):
            removed_count += 1
            continue
        
        # dress 태그인지 확인 (제거할 경우)
        if dress_tags and is_tag_excluded(tag, dress_tags):
            removed_count += 1
            continue
        
        # 정규화된 태그로 중복 확인 (언더스코어와 공백을 동일하게 처리)
        normalized = normalize_tag(tag)
        if normalized not in seen_normalized:
            seen_normalized.add(normalized)
            filtered_tags.append(tag)  # 원본 태그 유지 (대소문자, 언더스코어 등)
        else:
            removed_count += 1  # 중복 태그 제거
    
    # 필터링된 태그를 다시 쉼표로 연결
    # 태그가 모두 제거된 경우 원래 형식 유지 (예: " , " 또는 "")
    if not filtered_tags:
        # 원본에 태그가 있었지만 모두 제거된 경우
        if tags and any(tag for tag in tags if tag):  # 빈 태그가 아닌 태그가 있었다면
            result = " , "  # 기본 형식 유지
        else:
            result = tag_string  # 원본 그대로
    else:
        result = ', '.join(filtered_tags)
    
    return result, removed_count

