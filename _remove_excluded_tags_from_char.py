# -*- coding: utf-8 -*-
"""
char.yml 파일의 'char' 필드에서 EXCLUDED_TAGS에 해당하는 태그를 제거
"""
import sys
import os
import re

# 스크립트가 있는 디렉토리를 Python 경로에 추가
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from ruamel.yaml import YAML
from tag_utils import load_excluded_tags, is_tag_excluded, load_config, normalize_tag, load_dress_tags, extract_dress_tags_from_string, remove_excluded_tags_from_string

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

# dress 필드로 이동할 태그 목록 (config.yml 파일에서 로드)
DRESS_TAGS = load_dress_tags()

def extract_tags_from_dress_field(dress_value):
    """
    dress 필드 값에서 태그를 추출합니다.
    형식: '{  태그1, 태그2 |4::__dress__},' 또는 '{   |4::__dress__},'
    
    Args:
        dress_value: dress 필드 값 문자열
    
    Returns:
        추출된 태그 리스트
    """
    if not dress_value or not isinstance(dress_value, str):
        return []
    
    # '{  태그1, 태그2 |4::__dress__},' 형식에서 태그 부분 추출
    # '{' 와 '|' 사이의 부분을 추출
    match = re.search(r'\{([^|]+)\|', dress_value)
    if match:
        tags_str = match.group(1).strip()
        if tags_str:
            # 쉼표로 분리하여 태그 리스트 만들기
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            return tags
    return []

def merge_dress_tags(existing_tags, new_tags):
    """
    기존 dress 태그와 새로운 dress 태그를 병합합니다.
    중복을 제거하고 정규화된 태그로 확인합니다.
    
    Args:
        existing_tags: 기존 태그 리스트
        new_tags: 새로운 태그 리스트
    
    Returns:
        병합된 태그 리스트 (중복 제거됨)
    """
    merged_tags = []
    seen_normalized = set()
    
    # 기존 태그 추가
    for tag in existing_tags:
        if not tag:
            continue
        normalized = normalize_tag(tag)
        if normalized not in seen_normalized:
            seen_normalized.add(normalized)
            merged_tags.append(tag)
    
    # 새로운 태그 추가 (중복 제거)
    for tag in new_tags:
        if not tag:
            continue
        normalized = normalize_tag(tag)
        if normalized not in seen_normalized:
            seen_normalized.add(normalized)
            merged_tags.append(tag)
    
    return merged_tags

def process_char_yml(yml_path, excluded_tags, dress_tags):
    """
    char.yml 파일을 읽어서 char 필드에서 제외 태그를 제거하고,
    dress 태그를 dress 필드로 이동하며, dress 키가 없으면 추가합니다.
    주석은 보존됩니다.
    
    Args:
        yml_path: char.yml 파일 경로
        excluded_tags: 제외 태그 목록
        dress_tags: dress 태그 목록
    
    Returns:
        (수정된 YAML 데이터, 수정된 키 개수, 제거된 태그 총 개수, 추가/수정된 dress 키 개수)
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
    
    # 각 키의 positive.char 필드에서 제외 태그 제거 및 dress 태그 이동
    modified_count = 0
    total_removed_tags = 0
    modified_dress_count = 0
    
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
                    # dress 태그 추출
                    dress_tag_list = extract_dress_tags_from_string(char_value, dress_tags) if dress_tags else []
                    
                    # 제외 태그 및 dress 태그 제거
                    filtered_char, removed_count = remove_excluded_tags_from_string(
                        char_value, excluded_tags, dress_tags
                    )
                    
                    # char 필드 업데이트
                    char_modified = False
                    if removed_count > 0 or dress_tag_list:
                        yml_data[key]['positive']['char'] = filtered_char
                        char_modified = True
                        modified_count += 1
                        total_removed_tags += removed_count
                        
                        if dress_tag_list:
                            print(f"    - {key}: {removed_count}개 태그 제거, {len(dress_tag_list)}개 dress 태그 이동")
                        else:
                            print(f"    - {key}: {removed_count}개 태그 제거")
                    
                    # dress 필드 처리 (char 키가 있으면 항상 체크)
                    has_dress = 'dress' in positive_dict
                    existing_dress_value = positive_dict.get('dress', '')
                    
                    if dress_tag_list:
                        # 기존 dress 필드에서 태그 추출 (있으면)
                        existing_dress_tags = []
                        if has_dress and existing_dress_value:
                            existing_dress_tags = extract_tags_from_dress_field(existing_dress_value)
                        
                        # 기존 태그와 새로운 태그 병합
                        merged_dress_tags = merge_dress_tags(existing_dress_tags, dress_tag_list)
                        
                        # 병합된 태그들을 문자열로 변환
                        if merged_dress_tags:
                            dress_tags_str = ', '.join(merged_dress_tags)
                            dress_value = f'{{  {dress_tags_str} |4::__dress__}},'
                        else:
                            dress_value = '{   |4::__dress__},'
                        
                        # dress 키가 있으면 업데이트, 없으면 추가
                        if has_dress:
                            # 기존 태그와 병합된 태그가 다르면 업데이트
                            if set(normalize_tag(tag) for tag in merged_dress_tags) != set(normalize_tag(tag) for tag in existing_dress_tags):
                                yml_data[key]['positive']['dress'] = dress_value
                                modified_dress_count += 1
                                if existing_dress_tags:
                                    print(f"      → dress 필드 업데이트: 기존 {len(existing_dress_tags)}개 + 신규 {len(dress_tag_list)}개 → 총 {len(merged_dress_tags)}개 태그")
                                else:
                                    print(f"      → dress 필드 업데이트: {len(merged_dress_tags)}개 태그 추가")
                        else:
                            yml_data[key]['positive']['dress'] = dress_value
                            modified_dress_count += 1
                            print(f"      → dress 필드 추가: {len(merged_dress_tags)}개 태그")
                    elif not has_dress:
                        # dress 태그가 없지만 dress 키가 없으면 기본값 추가
                        yml_data[key]['positive']['dress'] = '{   |4::__dress__},'
                        modified_dress_count += 1
                        if not char_modified:
                            print(f"    - {key}: dress 키 추가")
                        else:
                            print(f"      → dress 키 추가 (기본값)")
    
    return yml_data, modified_count, total_removed_tags, modified_dress_count

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
    print(f"  dress 태그 개수: {len(DRESS_TAGS)}개")
    
    # char.yml 파일 처리
    modified_data, modified_count, total_removed_tags, modified_dress_count = process_char_yml(
        yml_path, EXCLUDED_TAGS, DRESS_TAGS
    )
    
    if modified_data is None:
        return
    
    if modified_count == 0 and modified_dress_count == 0:
        print(f"  [OK] 수정할 항목이 없습니다.")
        return
    
    # 수정된 내용 저장
    print(f"\n  수정된 내용 저장 중...")
    if save_char_yml(yml_path, modified_data):
        messages = []
        if modified_count > 0:
            messages.append(f"{modified_count}개 키에서 총 {total_removed_tags}개 태그 제거")
        if modified_dress_count > 0:
            messages.append(f"{modified_dress_count}개 키의 dress 필드 추가/수정")
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
    print(f"dress 태그 목록 (config.yml에서 로드): {len(DRESS_TAGS)}개")
    
    for type_name in types:
        process_type(type_name)
    
    print(f"\n{'='*80}")
    print("모든 처리 완료!")
    print(f"{'='*80}")

