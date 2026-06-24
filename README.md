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

## 테스트

```bash
python3 -m unittest discover -s tests -v
```
