"""광운대학교 포켓몬 상성 체육관 - Streamlit entry point."""

from __future__ import annotations

import base64
import copy
import html
import json
import random
from pathlib import Path

import streamlit as st

from database import (
    authenticate,
    create_user,
    get_user,
    grant_partner_pokemon,
    initialize_database,
    record_battle,
    set_nickname,
)
from ui import apply_global_styles, hp_panel, student_ribbon, type_chips


ROOT = Path(__file__).parent
QUIZ_PATH = ROOT / "data" / "quiz_data.json"
MONSTER_PATH = ROOT / "assets" / "junhyeonmon.png"
PARTNER_PATH = ROOT / "assets" / "lumibolt.png"
BADGE_PATH = ROOT / "assets" / "kw-gym-badge.png"
START_MUSIC = ROOT / "start.mp3"
BATTLE_MUSIC = ROOT / "battle.mp3"
CLICK_SOUND = ROOT / "click_sound.mp3"
DAMAGE_SOUND = ROOT / "damg.mp3"
GREAT_SOUND = ROOT / "great.mp3"
WRONG_SOUND = ROOT / "god-dammit-augghhh.mp3"
EARN_SOUND = ROOT / "earn.mp3"
PARTNER_NAME = "루미볼트"
TOTAL_QUESTIONS = 20


st.set_page_config(
    page_title="광운대 상성 체육관",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_global_styles()
initialize_database()


@st.cache_data(show_spinner="상성 도감을 불러오는 중...")
def load_quiz_data(path: str, modified_at: float) -> list[dict]:
    """Read and validate quiz JSON once; mtime invalidates cache after edits."""
    del modified_at
    with open(path, encoding="utf-8") as quiz_file:
        questions = json.load(quiz_file)
    if len(questions) != TOTAL_QUESTIONS:
        raise ValueError(f"퀴즈는 정확히 {TOTAL_QUESTIONS}문제여야 합니다.")
    for question in questions:
        if question["answer"] not in question["options"]:
            raise ValueError(f"{question['id']}번 문제의 정답이 선택지에 없습니다.")
    return questions


@st.cache_data(show_spinner=False)
def image_data_url(path: str, modified_at: float) -> str:
    """Cache large local image encoding used by the custom battle stage."""
    del modified_at
    suffix = Path(path).suffix.lstrip(".")
    encoded = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:image/{suffix};base64,{encoded}"


@st.cache_data(show_spinner=False)
def audio_data_url(path: str, modified_at: float) -> str:
    """Cache MP3 encoding for the layered battle soundscape component."""
    del modified_at
    encoded = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:audio/mpeg;base64,{encoded}"


QUESTIONS = load_quiz_data(str(QUIZ_PATH), QUIZ_PATH.stat().st_mtime)
MONSTER_DATA_URL = image_data_url(str(MONSTER_PATH), MONSTER_PATH.stat().st_mtime)
PARTNER_DATA_URL = image_data_url(str(PARTNER_PATH), PARTNER_PATH.stat().st_mtime)
BADGE_DATA_URL = image_data_url(str(BADGE_PATH), BADGE_PATH.stat().st_mtime)
BATTLE_AUDIO_URL = audio_data_url(str(BATTLE_MUSIC), BATTLE_MUSIC.stat().st_mtime)
CLICK_AUDIO_URL = audio_data_url(str(CLICK_SOUND), CLICK_SOUND.stat().st_mtime)
DAMAGE_AUDIO_URL = audio_data_url(str(DAMAGE_SOUND), DAMAGE_SOUND.stat().st_mtime)
GREAT_AUDIO_URL = audio_data_url(str(GREAT_SOUND), GREAT_SOUND.stat().st_mtime)
WRONG_AUDIO_URL = audio_data_url(str(WRONG_SOUND), WRONG_SOUND.stat().st_mtime)


def initialize_session() -> None:
    defaults = {
        "page": "auth",
        "logged_in": False,
        "user_id": None,
        "username": None,
        "nickname": None,
        "partner_pokemon": None,
        "music_on": True,
        "question_index": 0,
        "score": 0,
        "wrong_count": 0,
        "opponent_hp": 100,
        "player_hp": 100,
        "answer_locked": False,
        "last_correct": None,
        "last_choice": None,
        "sound_event": None,
        "battle_id": 0,
        "battle_questions": [],
        "result_recorded": False,
        "celebrated": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def play_music(path: Path) -> None:
    if st.session_state.music_on and path.exists():
        st.audio(str(path), format="audio/mpeg", loop=True, autoplay=True)


def play_once(path: Path) -> None:
    if st.session_state.music_on and path.exists():
        st.audio(str(path), format="audio/mpeg", autoplay=True)


def play_battle_soundscape(event: str | None) -> None:
    """Persist BGM position across reruns and pause it for result SFX."""
    if not st.session_state.music_on:
        return
    event_type = event or ""
    result_url = WRONG_AUDIO_URL if event == "wrong" else GREAT_AUDIO_URL
    battle_id = int(st.session_state.battle_id)
    event_token = f"{battle_id}-{st.session_state.question_index}-{event_type}"
    script = f"""
    <audio id="bgm" src="{BATTLE_AUDIO_URL}" loop preload="auto"></audio>
    <audio id="click" src="{CLICK_AUDIO_URL}" preload="auto"></audio>
    <audio id="damage" src="{DAMAGE_AUDIO_URL}" preload="auto"></audio>
    <audio id="result" src="{result_url}" preload="auto"></audio>
    <script>
      (() => {{
        const bgm = document.getElementById('bgm');
        const result = document.getElementById('result');
        const timeKey = 'kw-battle-bgm-time-{battle_id}';
        const eventKey = 'kw-battle-last-event-{battle_id}';
        const eventType = '{event_type}';
        const eventToken = '{event_token}';
        let savedTime = 0;

        const readStorage = (key) => {{
          try {{ return localStorage.getItem(key); }} catch (_) {{ return null; }}
        }};
        const writeStorage = (key, value) => {{
          try {{ localStorage.setItem(key, value); }} catch (_) {{}}
        }};
        const parsedTime = Number.parseFloat(readStorage(timeKey) || '0');
        if (Number.isFinite(parsedTime) && parsedTime >= 0) savedTime = parsedTime;

        const rememberPosition = () => {{
          if (Number.isFinite(bgm.currentTime)) writeStorage(timeKey, String(bgm.currentTime));
        }};
        const resumeBattle = () => bgm.play().catch(() => {{}});

        bgm.volume = 0.34;
        const startPlayback = () => {{
          if (bgm.duration && savedTime >= bgm.duration) savedTime %= bgm.duration;
          try {{ bgm.currentTime = savedTime; }} catch (_) {{}}

          const isNewResult = eventType && readStorage(eventKey) !== eventToken;
          if (!isNewResult) {{
            resumeBattle();
            return;
          }}

          writeStorage(eventKey, eventToken);
          document.getElementById('click').play().catch(() => {{}});
          document.getElementById('damage').play().catch(() => {{}});
          result.addEventListener('ended', resumeBattle, {{once:true}});
          result.play().catch(resumeBattle);
        }};
        if (bgm.readyState >= 1) startPlayback();
        else bgm.addEventListener('loadedmetadata', startPlayback, {{once:true}});

        setInterval(rememberPosition, 150);
        window.addEventListener('pagehide', rememberPosition);
        window.addEventListener('beforeunload', rememberPosition);
      }})();
    </script>
    """
    st.iframe(script, height=1, tab_index=-1)


def account_header(music_path: Path | None = None) -> None:
    name = html.escape(st.session_state.nickname or st.session_state.username or "도전자")
    left, sound, logout = st.columns([6, 1.3, 1.3])
    with left:
        st.markdown(f"**⚡ 광운대 상성 체육관** &nbsp; · &nbsp; 도전자 `{name}`")
    with sound:
        icon = "🔊 BGM" if st.session_state.music_on else "🔇 BGM"
        if st.button(icon, key=f"music_{st.session_state.page}"):
            st.session_state.music_on = not st.session_state.music_on
            st.rerun()
    with logout:
        if st.button("로그아웃", key=f"logout_{st.session_state.page}"):
            logout_user()
    if music_path:
        play_music(music_path)


def logout_user() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def sign_in(user: dict) -> None:
    st.session_state.logged_in = True
    st.session_state.user_id = user["id"]
    st.session_state.username = user["username"]
    st.session_state.nickname = user["nickname"]
    st.session_state.partner_pokemon = user.get("partner_pokemon")
    if not user["nickname"]:
        st.session_state.page = "nickname"
    elif not user.get("partner_pokemon"):
        st.session_state.page = "partner"
    else:
        st.session_state.page = "lobby"
    st.rerun()


def prepare_battle() -> None:
    questions = copy.deepcopy(QUESTIONS)
    random.SystemRandom().shuffle(questions)
    for question in questions:
        random.SystemRandom().shuffle(question["options"])
    st.session_state.battle_questions = questions
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.wrong_count = 0
    st.session_state.opponent_hp = 100
    st.session_state.player_hp = 100
    st.session_state.answer_locked = False
    st.session_state.last_correct = None
    st.session_state.last_choice = None
    st.session_state.sound_event = None
    st.session_state.battle_id += 1
    st.session_state.result_recorded = False
    st.session_state.celebrated = False
    st.session_state.page = "intro"
    st.rerun()


def finish_battle() -> None:
    won = st.session_state.score == TOTAL_QUESTIONS
    if won:
        st.session_state.opponent_hp = 0
    else:
        st.session_state.player_hp = 0
    if not st.session_state.result_recorded:
        record_battle(st.session_state.user_id, st.session_state.score, won)
        st.session_state.result_recorded = True
    st.session_state.page = "result"
    st.rerun()


def render_battle_stage() -> None:
    nickname = html.escape(st.session_state.nickname or "도전자")
    partner = html.escape(st.session_state.partner_pokemon or PARTNER_NAME)
    enemy_hit = " took-hit" if st.session_state.sound_event == "correct" else ""
    partner_hit = " took-hit" if st.session_state.sound_event == "wrong" else ""
    st.markdown(
        f"""
        <div class="battle-stage">
          {hp_panel("준현몬", st.session_state.opponent_hp, "enemy")}
          <img class="monster-img{enemy_hit}" src="{MONSTER_DATA_URL}" alt="오리지널 상대 몬스터 준현몬">
          <img class="partner-img{partner_hit}" src="{PARTNER_DATA_URL}" alt="도전자의 파트너 루미볼트">
          <div class="trainer-name">TRAINER {nickname}</div>
          {hp_panel(partner, st.session_state.player_hp, "player")}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_auth() -> None:
    student_ribbon()
    st.markdown(
        """
        <section class="hero">
          <span class="hero-kicker">KWANGWOON TYPE MASTERS</span>
          <h1>광운대 상성 체육관</h1>
          <p>18개 타입의 빈틈을 읽고, 관장 백준현과 준현몬을 쓰러뜨려라.<br>단 한 문제의 실수도 허용되지 않는 20턴 퍼펙트 배틀!</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    left, center, right = st.columns([1, 1.45, 1])
    with center:
        signup_tab, login_tab = st.tabs(["🪪 회원가입", "🔑 로그인"])
        with signup_tab:
            st.caption("처음 온 도전자는 트레이너 카드를 만들어 주세요.")
            with st.form("signup_form", clear_on_submit=False):
                username = st.text_input("아이디", placeholder="영문·숫자·밑줄 4~20자")
                password = st.text_input("비밀번호", type="password", placeholder="영문+숫자 8자 이상")
                confirm = st.text_input("비밀번호 확인", type="password")
                submitted = st.form_submit_button("트레이너 등록")
            if submitted:
                if password != confirm:
                    st.error("비밀번호 확인이 일치하지 않습니다.")
                else:
                    success, message = create_user(username, password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        with login_tab:
            st.caption("등록한 트레이너 카드로 입장합니다.")
            with st.form("login_form"):
                username = st.text_input("아이디", key="login_username")
                password = st.text_input("비밀번호", type="password", key="login_password")
                submitted = st.form_submit_button("체육관 입장")
            if submitted:
                user = authenticate(username, password)
                if user:
                    sign_in(user)
                else:
                    st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
    st.markdown(
        '<p style="text-align:center;color:#91a7d4;margin-top:1.5rem">계정 정보는 외부 전송 없이 로컬 SQLite DB에 안전하게 해시되어 저장됩니다.</p>',
        unsafe_allow_html=True,
    )


def show_nickname() -> None:
    student_ribbon()
    account_header()
    st.markdown(
        """
        <section class="hero"><span class="hero-kicker">TRAINER SETUP</span>
        <h1>도전자 이름을 정하자!</h1><p>이 이름은 배틀 대사와 전적 카드에 표시됩니다.</p></section>
        """,
        unsafe_allow_html=True,
    )
    left, center, right = st.columns([1, 1.3, 1])
    with center:
        with st.form("nickname_form"):
            nickname = st.text_input("닉네임", max_chars=12, placeholder="예: 번개마스터")
            submitted = st.form_submit_button("닉네임 결정")
        if submitted:
            success, message = set_nickname(st.session_state.user_id, nickname)
            if success:
                st.session_state.nickname = message
                st.session_state.page = "partner"
                st.rerun()
            st.error(message)


def show_partner() -> None:
    account_header(START_MUSIC)
    user = get_user(st.session_state.user_id)
    if not user:
        logout_user()
        return
    already_granted = bool(user.get("partner_pokemon"))
    image_class = "partner-reveal" if already_granted else "partner-mystery"
    title = "너의 첫 파트너가 기다리고 있다!" if not already_granted else f"{PARTNER_NAME}, 너로 정했다!"
    st.markdown(
        f"""
        <section class="hero"><span class="hero-kicker">FIRST PARTNER</span>
        <h1>{title}</h1><p>광운대 신입 트레이너에게 지급되는 특별한 전기/에스퍼 파트너입니다.</p></section>
        """,
        unsafe_allow_html=True,
    )
    left, center, right = st.columns([1, 1.25, 1])
    with center:
        st.markdown(
            f'<div class="{image_class}"><img src="{PARTNER_DATA_URL}" alt="지급될 파트너 포켓몬"></div>',
            unsafe_allow_html=True,
        )
        if not already_granted:
            st.markdown(
                '<div class="dialogue">광운대학교 트레이너 지원 센터에서<br><b>파트너 몬스터볼</b>을 지급했다!<br>버튼을 눌러 새로운 동료를 만나 보자.</div>',
                unsafe_allow_html=True,
            )
            st.write("")
            if st.button("🔴 지급 몬스터볼 열기!"):
                st.session_state.partner_pokemon = grant_partner_pokemon(st.session_state.user_id)
                st.rerun()
        else:
            st.session_state.partner_pokemon = user["partner_pokemon"]
            st.markdown(
                f'<div class="dialogue">전기/에스퍼타입 <b>{PARTNER_NAME}</b>를 받았다!<br>이제 {html.escape(st.session_state.nickname)}와 함께 체육관에 도전할 수 있다.</div>',
                unsafe_allow_html=True,
            )
            st.write("")
            if st.button(f"⚡ {PARTNER_NAME}와 로비로 가기"):
                st.session_state.page = "lobby"
                st.rerun()


def show_lobby() -> None:
    account_header(START_MUSIC)
    user = get_user(st.session_state.user_id)
    if not user:
        logout_user()
        return
    st.session_state.nickname = user["nickname"]
    st.session_state.partner_pokemon = user["partner_pokemon"]
    nickname = html.escape(user["nickname"])
    st.markdown(
        f"""
        <section class="hero"><span class="hero-kicker">KWANGWOON GYM LOBBY</span>
        <h1>{nickname}의 도전 준비</h1>
        <p>복합타입의 함정을 간파하고 20문제를 모두 맞히면 광운대 체육관 배지를 획득합니다.</p></section>
        """,
        unsafe_allow_html=True,
    )
    info, partner, badge = st.columns([1.4, .85, .85], gap="large")
    with info:
        st.markdown(
            f"""
            <div class="game-card"><span class="mini-label">TRAINER RECORD</span><h2>{nickname}</h2>
              <div class="stat-grid">
                <div class="stat"><b>{user['attempts']}</b><small>도전</small></div>
                <div class="stat"><b>{user['wins']}</b><small>승리</small></div>
                <div class="stat"><b>{user['best_score']}/20</b><small>최고 기록</small></div>
              </div>
              <p>배틀 규칙 · 정답 시 준현몬에게 5 DAMAGE · 오답 시 도전자 DAMAGE · 승리 조건은 오직 20/20</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("⚔️ 문제 풀기 · 관장에게 도전", type="primary"):
            prepare_battle()
    with partner:
        st.markdown('<span class="mini-label">MY PARTNER</span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="partner-card"><img src="{PARTNER_DATA_URL}" alt="나의 파트너 {PARTNER_NAME}"><b>{PARTNER_NAME}</b><small>전기 / 에스퍼</small></div>',
            unsafe_allow_html=True,
        )
    with badge:
        st.markdown('<span class="mini-label">GYM BADGE</span>', unsafe_allow_html=True)
        css_class = "badge-glow" if user["has_badge"] else "locked-badge"
        label = "광운대 체육관 배지 획득 완료!" if user["has_badge"] else "아직 잠겨 있는 광운대 체육관 배지"
        st.markdown(
            f'<div class="{css_class}"><img src="{BADGE_DATA_URL}" alt="광운대 체육관 배지"></div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<p class="badge-label">{label}</p>', unsafe_allow_html=True)


def show_intro() -> None:
    account_header()
    play_battle_soundscape(None)
    nickname = html.escape(st.session_state.nickname)
    st.markdown(
        "<section class='hero'><span class='hero-kicker'>A CHALLENGER APPEARS</span><h1>관장전 개막!</h1></section>",
        unsafe_allow_html=True,
    )
    picture, story = st.columns([1, 1.15], gap="large")
    with picture:
        st.image(str(MONSTER_PATH), width="stretch")
    with story:
        st.markdown(
            f"""
            <div class="dialogue">🎵 배틀 음악이 울려 퍼진다!<br><br>
            광운대학교 포켓몬 관장 <b>백준현</b>이<br><b>{nickname}</b>에게 승부를 걸어 왔다!<br><br>
            <b>{nickname}</b>은(는) <b>{PARTNER_NAME}</b>를 내보냈다!<br><br>
            “상성은 암기가 아니라 계산이다.<br>준현몬의 HP를 전부 깎아 보아라!”</div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("⚡ 승부를 받아들인다!"):
            st.session_state.page = "battle"
            st.rerun()


def submit_answer(choice: str | None, question: dict) -> None:
    if choice is None:
        st.warning("기술을 선택한 뒤 공격해 주세요.")
        return
    is_correct = choice == question["answer"]
    st.session_state.last_choice = choice
    st.session_state.last_correct = is_correct
    st.session_state.answer_locked = True
    st.session_state.sound_event = "correct" if is_correct else "wrong"
    if is_correct:
        st.session_state.score += 1
        st.session_state.opponent_hp = max(0, st.session_state.opponent_hp - 5)
    else:
        st.session_state.wrong_count += 1
        st.session_state.player_hp = max(5, 100 - st.session_state.wrong_count * 15)
    st.rerun()


def show_battle() -> None:
    if not st.session_state.battle_questions:
        prepare_battle()
        return
    account_header()
    play_battle_soundscape(st.session_state.sound_event)
    render_battle_stage()
    index = st.session_state.question_index
    question = st.session_state.battle_questions[index]
    st.markdown(
        f"""
        <div class="question-head"><span class="question-no">TURN {index + 1:02d} / {TOTAL_QUESTIONS}</span>
        <span class="difficulty">{question['difficulty']}</span>{type_chips(question['types'])}</div>
        <div class="game-card"><h3>{html.escape(question['question'])}</h3></div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if not st.session_state.answer_locked:
        with st.form(f"question_form_{index}"):
            choice = st.radio(
                "가장 정확한 답을 선택하세요.",
                question["options"],
                index=None,
                key=f"answer_{index}",
            )
            submitted = st.form_submit_button("⚡ 기술 사용!")
        if submitted:
            submit_answer(choice, question)
    else:
        correct = st.session_state.last_correct
        class_name = "feedback-ok" if correct else "feedback-no"
        headline = "효과는 굉장했다! 준현몬에게 5 DAMAGE!" if correct else "효과를 잘못 읽었다! 준현몬의 반격!"
        chosen = html.escape(st.session_state.last_choice)
        answer = html.escape(question["answer"])
        explanation = html.escape(question["explanation"])
        st.markdown(
            f'<div class="{class_name}"><b>{headline}</b><br>선택: {chosen} · 정답: {answer}<br><small>{explanation}</small></div>',
            unsafe_allow_html=True,
        )
        is_last = index == TOTAL_QUESTIONS - 1
        button_label = "🏁 배틀 결과 확인" if is_last else "다음 턴 ▶"
        if st.button(button_label):
            if is_last:
                finish_battle()
            else:
                st.session_state.question_index += 1
                st.session_state.answer_locked = False
                st.session_state.last_choice = None
                st.session_state.last_correct = None
                st.session_state.sound_event = None
                st.rerun()


def show_result() -> None:
    account_header()
    won = st.session_state.score == TOTAL_QUESTIONS
    play_once(EARN_SOUND) if won else play_battle_soundscape(None)
    if won and not st.session_state.celebrated:
        st.balloons()
        st.session_state.celebrated = True
    render_battle_stage()
    left, center, right = st.columns([1, 1.5, 1])
    with center:
        if won:
            st.markdown('<h1 class="perfect">PERFECT VICTORY!</h1>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="badge-glow"><img src="{BADGE_DATA_URL}" alt="획득한 광운대 체육관 배지"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div class="dialogue">신난다! 광운대 포켓몬 관장 <b>백준현</b>을 이겼다!<br><br>
                🏅 <b>광운대 체육관 배지를 얻었다!</b><br>
                20개의 상성을 모두 꿰뚫은 완벽한 승리다!</div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<h1 class='perfect' style='color:#b9c4dc'>BATTLE LOST</h1>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="dialogue">눈앞이 컴컴해진다.<br>다시 도전해 보도록 하자....<br><br>
                최종 기록 <b>{st.session_state.score} / {TOTAL_QUESTIONS}</b><br>
                준현몬의 남은 HP <b>{st.session_state.opponent_hp}</b></div>
                """,
                unsafe_allow_html=True,
            )
        st.write("")
        if st.button("🔁 재도전"):
            prepare_battle()
        if st.button("🏠 로비로 돌아가기"):
            st.session_state.page = "lobby"
            st.rerun()


def main() -> None:
    initialize_session()
    page = st.session_state.page
    protected_pages = {"nickname", "partner", "lobby", "intro", "battle", "result"}
    if page in protected_pages and not st.session_state.logged_in:
        st.session_state.page = "auth"
        page = "auth"
    routes = {
        "auth": show_auth,
        "nickname": show_nickname,
        "partner": show_partner,
        "lobby": show_lobby,
        "intro": show_intro,
        "battle": show_battle,
        "result": show_result,
    }
    routes.get(page, show_auth)()


if __name__ == "__main__":
    main()
