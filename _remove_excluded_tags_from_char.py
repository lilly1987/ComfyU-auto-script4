# -*- coding: utf-8 -*-
"""
char.yml 파일의 'char' 필드에서 EXCLUDED_TAGS에 해당하는 태그를 제거
"""
import sys
import os

# 스크립트가 있는 디렉토리를 Python 경로에 추가
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from ruamel.yaml import YAML
from tag_utils import load_excluded_tags, is_tag_excluded, load_config, normalize_tag

# ruamel.yaml 인스턴스 생성 (round-trip 모드로 주석 보존)
yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 1000000  # 매우 큰 width로 설정하여 줄바꿈 방지
yaml.indent(mapping=2, sequence=4, offset=2)

# config.yml에서 설정 로드
config = load_config()

# 작업 디렉토리
base_dir = config.get('base_dir', r'W:\ComfyUI_windows_portable')

# 처리할 타입 리스트 (IL, Pony 등)
types = config.get('types', ['IL', 'Pony'])

# 제거할 태그 목록 (config.yml 파일에서 로드)
EXCLUDED_TAGS = load_excluded_tags()

def remove_excluded_tags_from_string(tag_string, excluded_tags):
    """
    태그 문자열에서 제외 태그와 중복 태그를 제거합니다.
    
    Args:
        tag_string: 쉼표로 구분된 태그 문자열 (예: "1girl, 2d, belt, smile")
        excluded_tags: 제외 태그 목록
    
    Returns:
        (제외 태그와 중복 태그가 제거된 태그 문자열, 제거된 태그 개수)
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

def process_char_yml(yml_path, excluded_tags):
    """
    char.yml 파일을 읽어서 char 필드에서 제외 태그를 제거하고,
    dress 키가 없으면 추가합니다.
    주석은 보존됩니다.
    
    Args:
        yml_path: char.yml 파일 경로
        excluded_tags: 제외 태그 목록
    
    Returns:
        (수정된 YAML 데이터, 수정된 키 개수, 제거된 태그 총 개수, 추가된 dress 키 개수)
    """
    if not os.path.exists(yml_path):
        print(f"  경고: YML 파일이 존재하지 않습니다: {yml_path}")
        return None, 0, 0, 0
    
    # YML 파일 읽기 (ruamel.yaml로 주석 보존)
    print(f"  YML 파일 읽는 중: {yml_path}")
    try:
        with open(yml_path, 'r', encoding='utf-8') as f:
            yml_data = yaml.load(f)
    except Exception as e:
        print(f"  오류: YML 파일 읽기 실패: {e}")
        return None, 0, 0, 0
    
    if not yml_data:
        print(f"  경고: YML 파일이 비어있습니다.")
        return None, 0, 0, 0
    
    # 각 키의 positive.char 필드에서 제외 태그 제거 및 dress 키 추가
    modified_count = 0
    total_removed_tags = 0
    added_dress_count = 0
    
    for key, value in yml_data.items():
        if not isinstance(value, dict):
            continue
        
        # positive 필드 확인
        if 'positive' in value and isinstance(value['positive'], dict):
            positive_dict = value['positive']
            
            # char 필드 처리
            if 'char' in positive_dict:
                char_value = positive_dict['char']
                
                if isinstance(char_value, str):
                    # 제외 태그 제거
                    filtered_char, removed_count = remove_excluded_tags_from_string(char_value, excluded_tags)
                    
                    if removed_count > 0:
                        yml_data[key]['positive']['char'] = filtered_char
                        modified_count += 1
                        total_removed_tags += removed_count
                        print(f"    - {key}: {removed_count}개 태그 제거")
            
            # dress 키가 없으면 추가
            if 'char' in positive_dict:
                # dress 또는 #dress 키가 있는지 확인
                has_dress = 'dress' in positive_dict or '#dress' in positive_dict
                
                if not has_dress:
                    # dress 키 추가
                    yml_data[key]['positive']['dress'] = '{   |4::__dress__},'
                    added_dress_count += 1
                    print(f"    - {key}: dress 키 추가")
    
    return yml_data, modified_count, total_removed_tags, added_dress_count

def save_char_yml(yml_path, yml_data):
    """
    char.yml 파일을 저장합니다.
    주석은 보존됩니다.
    
    Args:
        yml_path: char.yml 파일 경로
        yml_data: 저장할 YML 데이터 (ruamel.yaml 객체)
    """
    try:
        with open(yml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yml_data, f)
        return True
    except Exception as e:
        print(f"  오류: YML 파일 저장 실패: {e}")
        return False

def process_type(type_name):
    """각 타입에 대해 char.yml 파일에서 제외 태그 제거"""
    print(f"\n{'='*80}")
    print(f"[{type_name}] 처리 시작")
    print(f"{'='*80}")
    
    # 경로 설정
    yml_path = os.path.join(base_dir, 'ComfyU-auto-script_data', type_name, 'lora', 'char.yml')
    
    if not EXCLUDED_TAGS:
        print(f"  경고: 제외 태그 목록이 비어있습니다.")
        return
    
    print(f"  제외 태그 개수: {len(EXCLUDED_TAGS)}개")
    
    # char.yml 파일 처리
    modified_data, modified_count, total_removed_tags, added_dress_count = process_char_yml(yml_path, EXCLUDED_TAGS)
    
    if modified_data is None:
        return
    
    if modified_count == 0 and added_dress_count == 0:
        print(f"  [OK] 수정할 항목이 없습니다.")
        return
    
    # 수정된 내용 저장
    print(f"\n  수정된 내용 저장 중...")
    if save_char_yml(yml_path, modified_data):
        messages = []
        if modified_count > 0:
            messages.append(f"{modified_count}개 키에서 총 {total_removed_tags}개 태그 제거")
        if added_dress_count > 0:
            messages.append(f"{added_dress_count}개 키에 dress 키 추가")
        print(f"  [OK] {', '.join(messages)}")
    else:
        print(f"  [실패] 파일 저장에 실패했습니다.")

# 메인 처리
if __name__ == "__main__":
    print("="*80)
    print("char.yml 파일에서 제외 태그 제거")
    print("="*80)
    print(f"작업 디렉토리: {base_dir}")
    print(f"처리할 타입: {', '.join(types)}")
    print(f"제외 태그 목록 (config.yml에서 로드): {len(EXCLUDED_TAGS)}개")
    
    for type_name in types:
        process_type(type_name)
    
    print(f"\n{'='*80}")
    print("모든 처리 완료!")
    print(f"{'='*80}")

