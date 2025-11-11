# -*- coding: utf-8 -*-
"""
폴더의 safetensors 파일에서 ss_tag_frequency를 추출하여 char.yml 파일에 추가
"""
import sys
import os
import yaml
import json
from collections import defaultdict
from safetensors import safe_open

# 스크립트가 있는 디렉토리를 Python 경로에 추가
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from tag_utils import load_excluded_tags, is_tag_excluded, load_config

# config.yml에서 설정 로드
config = load_config()

# 작업 디렉토리
base_dir = config.get('base_dir', r'W:\ComfyUI_windows_portable')

# 처리할 타입 리스트 (IL, Pony 등)
types = config.get('types', ['IL', 'Pony'])

# 기본 템플릿 형식
template = {
    'weight': 150,
    'positive': {
        'char': "1girl , ",
        '#dress': "{ , |4::__dress__},"
    }
}

# 태그 최대 개수 제한
MAX_TAGS = 64

# 제거할 태그 목록 (config.yml 파일에서 로드)
EXCLUDED_TAGS = load_excluded_tags()

def extract_ss_tag_frequency(file_path):
    """
    safetensors 파일에서 ss_tag_frequency 메타데이터를 추출합니다.
    
    Args:
        file_path: safetensors 파일 경로
    
    Returns:
        ss_tag_frequency 딕셔너리 또는 None
    """
    try:
        with safe_open(file_path, framework='pt') as f:
            metadata = f.metadata()
            
            if metadata and 'ss_tag_frequency' in metadata:
                # ss_tag_frequency는 JSON 문자열로 저장되어 있음
                tag_frequency_str = metadata['ss_tag_frequency']
                tag_frequency = json.loads(tag_frequency_str)
                return tag_frequency
            else:
                return None
                
    except Exception as e:
        return None

def process_tag_frequency(tag_frequency, max_tags=64, excluded_tags=None):
    """
    ss_tag_frequency를 처리하여 정렬된 태그 문자열을 반환합니다.
    평균 이상인 태그만 기록하고, 최대 개수를 제한합니다.
    
    Args:
        tag_frequency: ss_tag_frequency 딕셔너리
        max_tags: 최대 태그 개수 (기본값: 64)
        excluded_tags: 제거할 태그 목록 (기본값: None)
    
    Returns:
        정렬된 태그 문자열 (예: "1girl, 3d, belt, boots, bare shoulders")
    """
    if not tag_frequency:
        return None
    
    if excluded_tags is None:
        excluded_tags = EXCLUDED_TAGS
    
    # 1차 키가 여러개인 경우 2차의 건수를 합산
    tag_counts = defaultdict(int)
    
    for first_key, second_dict in tag_frequency.items():
        if isinstance(second_dict, dict):
            for tag, count in second_dict.items():
                tag_counts[tag] += count
    
    if not tag_counts:
        return None
    
    # 제거할 태그 필터링 (정규식 패턴과 문자열 패턴 모두 지원)
    tag_counts_filtered = {
        tag: count for tag, count in tag_counts.items() 
        if not is_tag_excluded(tag, excluded_tags)
    }
    
    if not tag_counts_filtered:
        return None
    
    # 건수의 평균 계산
    counts = list(tag_counts_filtered.values())
    average_count = sum(counts) / len(counts) if counts else 0
    
    # 평균 이상인 태그만 필터링
    filtered_tags = [(tag, count) for tag, count in tag_counts_filtered.items() if count >= average_count]
    
    # 값을 기준으로 역순 정렬 (큰 값부터)
    sorted_tags = sorted(filtered_tags, key=lambda x: x[1], reverse=True)
    
    # 최대 개수 제한
    sorted_tags = sorted_tags[:max_tags]
    
    # 키값만 추출하여 쉼표와 공백으로 연결
    tag_names = [tag for tag, count in sorted_tags]
    result = ", ".join(tag_names)
    
    return result

def process_type(type_name):
    """각 타입에 대해 누락된 키를 찾아 YML 파일에 추가"""
    print(f"\n{'='*80}")
    print(f"[{type_name}] 처리 시작")
    print(f"{'='*80}")
    
    # 경로 설정
    folder_path = os.path.join(base_dir, 'ComfyUI', 'models', 'loras', type_name, 'char')
    yml_path = os.path.join(base_dir, 'ComfyU-auto-script_data', type_name, 'lora', 'char.yml')
    
    # 경로 존재 확인
    if not os.path.exists(folder_path):
        print(f"  경고: 폴더가 존재하지 않습니다: {folder_path}")
        return
    
    if not os.path.exists(yml_path):
        print(f"  경고: YML 파일이 존재하지 않습니다: {yml_path}")
        return
    
    # YML 파일에서 키값들 읽기
    print(f"  YML 파일 읽는 중: {yml_path}")
    try:
        with open(yml_path, 'r', encoding='utf-8') as f:
            yml_data = yaml.safe_load(f)
            yml_keys = set(yml_data.keys()) if yml_data else set()
    except Exception as e:
        print(f"  오류: YML 파일 읽기 실패: {e}")
        return
    
    print(f"  YML 키 개수: {len(yml_keys)}")
    
    # 폴더에서 파일명들 읽기
    print(f"  폴더 파일 목록 읽는 중: {folder_path}")
    folder_files = {}
    for f in os.listdir(folder_path):
        if f.endswith('.safetensors'):
            file_name_no_ext = f.replace('.safetensors', '')
            folder_files[file_name_no_ext] = os.path.join(folder_path, f)
    
    print(f"  폴더 파일 개수: {len(folder_files)}")
    
    # 확장자 제거한 버전으로 비교
    yml_keys_cleaned = {k for k in yml_keys if k}  # 빈 문자열 제외
    
    # 누락된 키값 찾기
    missing = set(folder_files.keys()) - yml_keys_cleaned
    
    print(f"\n  확장자 제거 후 비교:")
    print(f"    - YML 키 개수 (빈 키 제외): {len(yml_keys_cleaned)}")
    print(f"    - 폴더 파일 개수: {len(folder_files)}")
    print(f"    - 일치하는 키: {len(folder_files.keys() & yml_keys_cleaned)}")
    print(f"    - 누락된 키 개수: {len(missing)}")
    
    if len(missing) == 0:
        print(f"  [OK] 누락된 키가 없습니다.")
        return
    
    # 누락된 키를 YML 파일에 추가
    print(f"\n  누락된 키를 YML 파일에 추가 중...")
    if EXCLUDED_TAGS:
        print(f"    제외 태그 개수: {len(EXCLUDED_TAGS)}개")
    else:
        print(f"    경고: 제외 태그 목록이 비어있습니다.")
    
    added_count = 0
    no_tag_count = 0
    
    try:
        with open(yml_path, 'a', encoding='utf-8') as f:
            # 누락된 키를 정렬해서 추가
            for key in sorted(missing):
                file_path = folder_files[key]
                
                # ss_tag_frequency 추출
                tag_frequency = extract_ss_tag_frequency(file_path)
                sorted_tags = process_tag_frequency(tag_frequency, max_tags=MAX_TAGS, excluded_tags=EXCLUDED_TAGS)
                
                # 키값을 따옴표로 감싸기
                f.write(f'"{key}": # auto\n')
                f.write(f'  weight: {template["weight"]}\n')
                f.write(f'  positive:\n')
                
                if sorted_tags:
                    # 정렬된 태그를 char 필드에 추가
                    # YAML에서 작은따옴표 사용 시 작은따옴표 자체를 이중으로 처리
                    char_value = f"{sorted_tags}"
                    # 작은따옴표가 있으면 두 개로 변경 (YAML 작은따옴표 문자열에서 이스케이프)
                    char_value_escaped = char_value.replace("'", "''")
                    f.write(f'    char: \'{char_value_escaped}\'\n')
                    added_count += 1
                else:
                    # 태그가 없거나 평균 이상인 태그가 없으면 기본값 사용
                    default_char = template["positive"]["char"]
                    default_char_escaped = default_char.replace("'", "''")
                    f.write(f'    char: \'{default_char_escaped}\'\n')
                    no_tag_count += 1
                
                # dress 필드도 작은따옴표 이스케이프 처리
                dress_value = template["positive"]["#dress"]
                dress_value_escaped = dress_value.replace("'", "''")
                f.write(f'    #dress: \'{dress_value_escaped}\'\n')
                f.write('\n')
        
        print(f"  [OK] {len(missing)}개의 누락된 키가 추가되었습니다.")
        print(f"    - 태그 포함: {added_count}개")
        print(f"    - 태그 없음: {no_tag_count}개")
        print(f"  추가된 키 샘플 (처음 10개):")
        for i, key in enumerate(sorted(missing)[:10], 1):
            print(f"    {i}. {key}")
        if len(missing) > 10:
            print(f"    ... 외 {len(missing) - 10}개 더")
            
    except Exception as e:
        print(f"  오류: YML 파일에 추가 실패: {e}")
        import traceback
        traceback.print_exc()
        return

# 메인 처리
if __name__ == "__main__":
    print("="*80)
    print("누락된 키값 찾기 및 ss_tag_frequency로 char.yml 파일에 추가")
    print("="*80)
    print(f"처리할 타입: {', '.join(types)}")
    
    for type_name in types:
        process_type(type_name)
    
    print(f"\n{'='*80}")
    print("모든 처리 완료!")
    print(f"{'='*80}")

