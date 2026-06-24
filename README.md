# 광운대학교 포켓몬 상성 체육관

> 학번 **2022508121** · 이름 **백준현**

복합타입 상성을 계산하는 고난도 20문제 Streamlit 배틀 퀴즈입니다. 회원가입과 로그인 후 닉네임을 정하고 첫 파트너 `루미볼트`를 지급받아, 광운대학교 포켓몬 관장 백준현의 `준현몬`과 대결합니다. 20문제를 모두 맞혀야만 상대 HP가 0이 되고 광운대 체육관 배지를 얻을 수 있습니다.

## 실행 방법

Python 3.10 이상을 권장합니다. 이 프로젝트는 Streamlit `1.58.0`으로 검증합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 안내되는 로컬 주소(기본 `http://localhost:8501`)를 엽니다. 브라우저 정책상 자동 음악이 차단되면 화면의 `BGM` 버튼을 껐다가 다시 켜 주세요.

## 과제 필수 기능

- **첫 화면 제출자 정보**: 로그인 화면 최상단에 학번 `2022508121`과 이름 `백준현` 표시
- **실제 로그인**: 회원가입, PBKDF2 비밀번호 해시, 로그인 성공/실패 처리, 세션별 로그인 상태 분리
- **파트너 지급/전적 저장**: 로그인 후 오리지널 전기·에스퍼 파트너 `루미볼트` 지급. SQLite에 닉네임, 파트너, 도전 횟수, 승리, 최고 점수, 배지 보유 여부 저장
- **의미 있는 캐싱**: `@st.cache_data`로 JSON 퀴즈 파일 읽기·검증 결과와 큰 PNG의 Base64 변환 결과를 캐시. 파일 수정 시 수정 시각 인자로 캐시가 자동 무효화됨
- **퀴즈**: 18개 타입, 복합타입, 무효 상성, 프리즈드라이와 플라잉프레스까지 포함한 고난도 객관식 20문제
- **결과 계산**: 정답마다 준현몬 HP -5, 20/20이면 승리·배지 획득, 그 외에는 사용자 HP 0·재도전 가능
- **BGM/SFX**: 로비 `start.mp3`, 관장전 `battle.mp3` 반복. 정답은 `click_sound.mp3`+`damg.mp3` 후 `great.mp3`, 오답은 `god-dammit-augghhh.mp3`, 배지 획득은 `earn.mp3` 재생
- **사운드 연출**: 배틀 BGM의 재생 위치를 브라우저에 수시로 기억해 답을 제출해도 처음으로 돌아가지 않음. 정답·오답 결과음 동안에는 BGM을 잠시 멈추고, 결과음이 끝나면 기억한 지점부터 이어서 재생. 클릭·피격음은 결과음과 함께 레이어링

## 프로젝트 구조

```text
.
├── app.py                  # Streamlit 메인 실행 파일
├── database.py             # 인증·전적 SQLite 처리
├── ui.py                   # 배틀 UI/CSS 구성요소
├── data/quiz_data.json     # 캐시로 읽는 20문제
├── assets/                 # 오리지널 준현몬·루미볼트·배지 이미지
├── start.mp3 / battle.mp3  # 로비·배틀 BGM
├── great.mp3 / damg.mp3    # 정답·피격 효과음
├── click_sound.mp3         # 기술 사용 버튼 효과음
├── god-dammit-augghhh.mp3  # 오답 효과음
├── earn.mp3                # 배지 획득 효과음
├── requirements.txt
└── tests/test_quiz_data.py
```

실행 중 생성되는 `data/pokemon_quiz.db`와 로컬 참고문서 `과제 안내.md`는 `.gitignore`로 제출 대상에서 제외됩니다.

## 테스트

```bash
python3 -m unittest discover -s tests -v
```
