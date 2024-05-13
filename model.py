import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# 프로그램 정보 데이터프레임
program_df = pd.read_csv('/Users/mac/Desktop/airich/program .csv')

@app.route('/')
def index():
    return render_template('web.html')

@app.route('/submit', methods=['POST'])
def submit():
    # 사용자 입력 받기
    region = request.form['region']
    category = request.form['category']
    age = request.form['age']
    gender = request.form['gender']
    
    # 사용자 정보 데이터프레임 생성
    user_df = pd.DataFrame({
        '지역': [region],
        '카테고리': [category],
        '나이': [age],
        '성별': [gender]
    })

    # 각 사용자에 대해 상위 10개 프로그램 출력
    result=calculate_user_match(user_df)

    return render_template('result.html', result=result)

def calculate_match(user, program):
    # 각 특성에 대한 가중치 설정
    weights = {'지역': 0.15, '카테고리': 0.6, '나이': 0.15, '성별': 0.1}

    # 각 특성에 대한 일치 정도 계산
    location_match = 1 if user['지역'] == program['지역'] else 0
    if location_match == 0:
        location_match = 0.1

    if user['카테고리'] == '기타':
        category_weight = 0.3  # 기타 카테고리의 가중치는 0.5로 설정
    else:
        category_weight = 0.6  # 다른 카테고리의 가중치는 0.5로 설정

    category_match = 1 if user['카테고리'] == program['카테고리'] else 0

    # 프로그램의 성별 정보 가져오기
    program_gender = program['성별']
    if ',' in program_gender:
        gender_match = 1
    else:
        gender_match = 1 if user['성별'] == program_gender else 0

    # 프로그램의 연령 범위를 가져옴
    program_age_ranges = program['연령']

    # 연령 범위를 쉼표로 분리하여 처리
    for age_range in program_age_ranges.split(','):
        # 연령 범위를 공백을 기준으로 분리하여 시작 나이와 끝 나이 추출
        age_parts = age_range.strip().split('-')

        # 시작 나이와 끝 나이를 추출
        if len(age_parts) == 2:
            start_age, end_age = map(int, age_parts)
        elif len(age_parts) == 1:
            start_age = int(age_parts[0])
            end_age = start_age  # 시작 나이만 존재하는 경우에는 끝 나이를 시작 나이로 설정
        else:
            # 처리할 수 없는 형식의 연령 범위이므로 건너뜀
            continue

        # 사용자의 나이가 현재 연령 범위 내에 있는지 확인
        if start_age <= int(user['나이']) <= end_age:
            age_match = 1
            break  # 일치하는 범위를 찾았으므로 더 이상 검사할 필요 없음
    else:
        age_match = 0  # 모든 연령 범위에서 일치하는 범위를 찾지 못한 경우

    # 각 특성의 일치 정도에 가중치를 곱하여 총 일치 정도 계산
    total_match = sum([location_match * weights['지역'],
                       category_match * category_weight,
                       age_match * weights['나이'],
                       gender_match * weights['성별']])

    # 백분율로 변환하여 반환
    return total_match * 100

def calculate_user_match(user_df):
    user_program_matches = []
    for user_index, user_row in user_df.iterrows():
        for program_index, program_row in program_df.iterrows():
            match_percentage = calculate_match(user_row, program_row)
            user_program_matches.append((user_index + 1, program_row['제목'], match_percentage))

    # 일치도가 높은 순서대로 정렬
    user_program_matches.sort(key=lambda x: x[2], reverse=True)
    return user_program_matches[:10]  # 상위 10개 프로그램 반환

if __name__ == '__main__':
    app.run(debug=True)
