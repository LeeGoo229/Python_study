"""
app.py
Code Study — 파이썬 및 SQL 인터랙티브 학습 플랫폼 & 대시보드
Version: 1.3.0 (2026-11-24, Ref: Python Cheat Sheet, [0] Python Basics ~ [8] Model_Evaluation)
"""

import os
import streamlit as st
import pandas as pd
from pathlib import Path

# 모듈 임포트
from modules.notebook_loader import (
    CURRICULUM,
    get_unit_by_key,
    get_release_versions,
    get_default_version_id,
    get_curriculum_by_version,
    load_version_description,
    load_theory_content,
    load_practice_and_answers,
    load_cheat_sheet_sections,
    BASE_DIR
)
from modules.python_runner import run_python_code
from modules.sql_runner import SQLEngine, SQL_CURRICULUM
from modules.diff_viewer import generate_diff_html
from modules.quiz_manager import (
    DEFAULT_QUIZ_SAMPLE_SIZE,
    DIFFICULTY_LABELS,
    DIFFICULTY_OPTIONS,
    QUIZ_TYPE_LABELS,
    calculate_quiz_summary,
    get_quiz_categories,
    get_quizzes,
    grade_answer,
    sample_quizzes,
)

# 페이지 기본 설정
st.set_page_config(
    page_title="Code Study — 파이썬 & SQL 학습 플랫폼",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모던 CSS 스타일 주입
st.markdown("""
<style>
    /* 전체 폰트 및 여백 */
    .main { background-color: #f8fafc; }
    h1, h2, h3 { color: #0f172a; font-weight: 700; }
    
    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #2563eb !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* 카드 컴포넌트 */
    .study-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* 결과 콘솔 */
    .console-box {
        background-color: #0f172a;
        color: #38bdf8;
        padding: 14px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 13px;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화 (진도율 및 사용자 작성 코드 보존)
if "user_codes" not in st.session_state:
    st.session_state["user_codes"] = {}
if "completed_units" not in st.session_state:
    st.session_state["completed_units"] = set()
if "sql_engine" not in st.session_state:
    st.session_state["sql_engine"] = SQLEngine()
if "quiz_results" not in st.session_state:
    st.session_state["quiz_results"] = {}
if "quiz_drawn" not in st.session_state:
    st.session_state["quiz_drawn"] = {}


def _get_quiz_user_input(q: dict, input_key: str) -> str:
    """퀴즈 문항 유형에 맞는 입력 위젯을 렌더링하고 사용자 입력값을 반환합니다."""
    if q.get("type") == "ox":
        choice = st.radio(
            "정답 선택 (O / X):",
            options=["선택 안 함", "O", "X"],
            horizontal=True,
            key=input_key,
        )
        return "" if choice == "선택 안 함" else choice
    return st.text_input(
        "정답 입력:",
        key=input_key,
        placeholder="정답을 입력하세요 (대소문자·앞뒤 공백 무관)",
    )


def _reset_quiz_scope(questions: list, scope_key: str) -> None:
    """해당 퀴즈 스코프의 입력값과 채점 결과를 초기화합니다."""
    st.session_state["quiz_results"].pop(scope_key, None)
    for q in questions:
        input_key = f"quiz_input_{scope_key}_{q['id']}"
        hint_key = f"quiz_hint_{scope_key}_{q['id']}"
        if q.get("type") == "ox":
            st.session_state[input_key] = "선택 안 함"
        else:
            st.session_state[input_key] = ""
        st.session_state[hint_key] = False


def render_quiz_section(
    pool_questions: list,
    scope_key: str,
    unit_key: str | None = None,
) -> None:
    """퀴즈 풀에서 5문제를 랜덤 출제해 세션에 고정하고 점수판, 힌트 토글, 채점, 재출제 UI를 렌더링합니다."""
    if not pool_questions:
        st.info("선택한 조건에 해당하는 퀴즈 문항이 없습니다.")
        return

    drawn_map = st.session_state["quiz_drawn"]
    drawn_questions = drawn_map.get(scope_key)

    draw_col1, draw_col2 = st.columns([2.2, 5.8])
    with draw_col1:
        draw_label = (
            "🎲 다시 출제하기 (새 5문제)"
            if drawn_questions is not None
            else "🎯 출제하기 (5문제)"
        )
        if st.button(
            draw_label,
            type="primary",
            use_container_width=True,
            key=f"draw_quiz_{scope_key}",
        ):
            prev_ids = [q["id"] for q in drawn_questions] if drawn_questions else None
            if drawn_questions is not None:
                _reset_quiz_scope(drawn_questions, scope_key)
            drawn_map[scope_key] = sample_quizzes(
                pool_questions,
                count=DEFAULT_QUIZ_SAMPLE_SIZE,
                unit_key=unit_key,
                exclude_ids=prev_ids,
            )
            st.rerun()
    with draw_col2:
        st.caption(
            f"선택된 조건의 전체 문항 풀: **{len(pool_questions)}문항** (출제 시 최대 {DEFAULT_QUIZ_SAMPLE_SIZE}문항 랜덤 추출)"
        )

    if drawn_questions is None:
        st.info("위의 **[🎯 출제하기 (5문제)]** 버튼을 눌러 랜덤 5문제를 출제해 보세요.")
        return

    questions = drawn_questions
    scope_results = st.session_state["quiz_results"].setdefault(scope_key, {})
    summary_placeholder = st.container()

    act_col1, act_col2, _ = st.columns([1.6, 1.6, 4.8])
    with act_col1:
        grade_all_clicked = st.button(
            "✅ 전체 채점하기",
            type="primary",
            use_container_width=True,
            key=f"grade_all_{scope_key}",
        )
    with act_col2:
        if st.button(
            "🔄 다시 풀기",
            use_container_width=True,
            key=f"reset_all_{scope_key}",
        ):
            _reset_quiz_scope(questions, scope_key)
            st.rerun()

    st.markdown("---")

    for idx, q in enumerate(questions, start=1):
        q_id = q["id"]
        type_badge = QUIZ_TYPE_LABELS.get(q.get("type", ""), "퀴즈")
        diff_badge = DIFFICULTY_LABELS.get(q.get("difficulty", ""), "기본")
        st.markdown(
            f'<div class="study-card"><strong>Q{idx}. [{type_badge}] [{diff_badge}]</strong> · {q["category_label"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(q["question"])

        show_hint = st.toggle("💡 힌트 보기", key=f"quiz_hint_{scope_key}_{q_id}")
        if show_hint and q.get("hint"):
            st.info(f"힌트: {q['hint']}")

        input_key = f"quiz_input_{scope_key}_{q_id}"
        user_val = _get_quiz_user_input(q, input_key)

        check_clicked = st.button(
            "채점하기",
            key=f"quiz_check_{scope_key}_{q_id}",
        )
        prev_res = scope_results.get(q_id)
        if prev_res is not None and prev_res.get("submitted_answer") != user_val:
            scope_results.pop(q_id, None)

        if check_clicked or grade_all_clicked:
            graded = grade_answer(q, user_val)
            graded["submitted_answer"] = user_val
            scope_results[q_id] = graded

        res = scope_results.get(q_id)
        if res is not None:
            if res["is_empty"]:
                st.warning("답안을 입력한 뒤 채점해 주세요.")
            elif res["is_correct"]:
                st.success(f"정답입니다! 🎉\n\n**해설:** {res['explanation']}")
            else:
                sample_ans = res["accepted_answers"][0] if res["accepted_answers"] else ""
                st.error(f"아쉽습니다. 정답 예시: `{sample_ans}`")
                st.info(f"**해설:** {res['explanation']}")

        st.markdown("")

    # 채점 결과를 반영한 최신 점수판을 상단 컨테이너에 렌더링
    summary = calculate_quiz_summary(questions, scope_results)
    with summary_placeholder:
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("총 문항", f"{summary['total']}문항")
        with m_col2:
            st.metric("현재 점수", f"{summary['correct']} / {summary['total']}")
        with m_col3:
            st.metric("정답률", f"{summary['accuracy']:.1f}%")
        st.progress(summary["correct"] / summary["total"] if summary["total"] > 0 else 0.0)

# ----------------------------------------------------
# 1. 상단 글로벌 네비게이션 (과목 전환)
# ----------------------------------------------------
top_col1, top_col2 = st.columns([2.4, 1.6])
with top_col1:
    st.title("💻 Code Study 실습 플랫폼")
    st.caption("파이썬 데이터 분석, 시각화, 기초통계 및 SQL 쿼리를 웹에서 직접 실습하고 정답을 확인하세요.")
with top_col2:
    selected_subject = st.segmented_control(
        "과목 선택",
        options=["🐍 Python 실습실", "🗄️ SQL 실습실", "📝 퀴즈 풀기"],
        default="🐍 Python 실습실"
    )

st.divider()

# ====================================================
# [모드 1] 🐍 Python 실습실
# ====================================================
if selected_subject == "🐍 Python 실습실":
    # 사이드바: 릴리즈 버전 & 커리큘럼 네비게이션
    with st.sidebar:
        st.header("🏷️ 릴리즈 버전 (Step)")
        release_versions = get_release_versions()
        default_ver_id = get_default_version_id()
        version_ids = [v["id"] for v in release_versions]
        default_ver_idx = version_ids.index(default_ver_id) if default_ver_id in version_ids else len(version_ids) - 1
        version_labels = {v["id"]: v["label"] for v in release_versions}

        selected_version_id = st.selectbox(
            "교육 Step / 버전 선택",
            options=version_ids,
            index=default_ver_idx,
            format_func=lambda vid: version_labels.get(vid, vid),
            key="selected_release_version",
        )
        version_desc = load_version_description(selected_version_id)
        st.caption(
            f"📦 {version_desc.get('category_count', 0)}개 대단원 · "
            f"{version_desc.get('unit_count', 0)}개 학습 항목"
        )
        with st.expander("📋 버전 설명 요약 보기", expanded=False):
            if version_desc.get("summary"):
                st.markdown(f"**요약:** {version_desc['summary']}")
                st.markdown("---")
            st.markdown(version_desc.get("markdown", ""))

        st.markdown("---")
        st.header("📚 Python 커리큘럼")

        categories = get_curriculum_by_version(selected_version_id)
        cat_names = [c["name"] for c in categories]
        selected_cat_name = st.selectbox(
            "대단원 선택",
            cat_names,
            key=f"cat_select_{selected_version_id}",
        )

        selected_cat = next(c for c in categories if c["name"] == selected_cat_name)
        unit_names = [u["title"] for u in selected_cat["units"]]
        selected_unit_title = st.selectbox(
            "소단원 선택",
            unit_names,
            key=f"unit_select_{selected_version_id}_{selected_cat['id']}",
        )

        unit_info = next(u for u in selected_cat["units"] if u["title"] == selected_unit_title)

        st.markdown("---")
        # 학습 완료 체크
        is_done = unit_info["key"] in st.session_state["completed_units"]
        if st.checkbox("✅ 이 단원 학습 완료 체크", value=is_done, key=f"done_{unit_info['key']}"):
            st.session_state["completed_units"].add(unit_info["key"])
        else:
            st.session_state["completed_units"].discard(unit_info["key"])

        # 전체 진도율 계산 (선택된 버전 기준)
        total_units = sum(len(c["units"]) for c in categories)
        done_count = sum(
            1
            for c in categories
            for u in c["units"]
            if u["key"] in st.session_state["completed_units"]
        )
        progress_pct = done_count / total_units if total_units > 0 else 0
        st.write(f"📊 **전체 학습 진도율 ({selected_version_id})**: {done_count}/{total_units} ({int(progress_pct*100)}%)")
        st.progress(progress_pct)

        st.markdown("---")
        st.info(f"💡 **배포 안내**: GitHub `main` 브랜치 기준 `{selected_version_id}` 스냅샷으로 실행 중입니다.")

    # [케이스 A] 치트시트 단원
    if unit_info.get("type") == "html_md":
        st.subheader(f"📌 {unit_info['title']}")
        cheat_tabs = st.tabs(["📄 마크다운 가이드", "🌐 원본 HTML 리포트"])
        
        with cheat_tabs[0]:
            sections = load_cheat_sheet_sections(unit_info.get("md_path"))
            section_keys = list(sections.keys())
            
            st.caption("💡 아래 주제 태그를 클릭하면 원하는 치트시트로 즉시 이동할 수 있습니다.")
            selected_sec = st.pills(
                "치트시트 주제 바로가기",
                options=section_keys,
                default=section_keys[0],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            target_content = sections.get(selected_sec, sections[section_keys[0]])
            st.markdown(target_content, unsafe_allow_html=True)
            
            if selected_sec != section_keys[0]:
                st.markdown("---")
                if st.button("📖 전체 가이드북 보기로 돌아가기", use_container_width=True):
                    st.rerun()
            
        with cheat_tabs[1]:
            html_path = unit_info.get("html_path")
            if html_path and html_path.exists():
                html_bytes = html_path.read_text(encoding="utf-8")
                st.components.v1.html(html_bytes, height=900, scrolling=True)
            else:
                st.warning("HTML 파일을 찾을 수 없습니다.")

    # [케이스 B] 일반 실습 단원 (Pandas, Visualization, Statistics)
    else:
        st.subheader(f"{selected_cat_name} ➔ {unit_info['title']}")
        
        tab_theory, tab_practice, tab_answer, tab_quiz = st.tabs([
            "📖 1. 핵심 개념 & 이론",
            "✍️ 2. 연습문제 & 코드 실행기",
            "💡 3. 모범 답안 & 해설",
            "📝 4. 개념 퀴즈",
        ])
        
        # ----------------------------------------------------
        # 탭 1: 핵심 개념 & 이론
        # ----------------------------------------------------
        with tab_theory:
            with st.spinner("이론 노트북 불러오는 중..."):
                theory_md = load_theory_content(unit_info)
                st.markdown(theory_md)
                
            # 데이터 폴더 미리보기 (Pandas 단원인 경우)
            data_dir = unit_info.get("data_dir")
            if data_dir and Path(data_dir).exists():
                with st.expander("📂 제공 실습 데이터셋 목록 및 미리보기"):
                    files = list(Path(data_dir).glob("*.*"))
                    for f in files:
                        st.write(f"• `{f.name}` ({f.stat().st_size / 1024:.1f} KB)")
                        if f.suffix == ".csv":
                            try:
                                sample_df = pd.read_csv(f, nrows=5)
                                st.dataframe(sample_df, use_container_width=True)
                            except Exception:
                                pass

        # ----------------------------------------------------
        # 탭 2: 연습문제 & 코드 실행기
        # ----------------------------------------------------
        with tab_practice:
            data_bundle = load_practice_and_answers(unit_info)
            setup_code = data_bundle.get("setup_code", "")
            questions = data_bundle.get("questions", [])
            data_dir_str = data_bundle.get("data_dir", "")
            
            if not questions:
                st.warning("이 단원에 등록된 연습문제가 없습니다.")
            else:
                # 문제 선택 셀렉트박스
                q_options = [f"Q{q['id']}. {q['title']}" for q in questions]
                selected_q_label = st.selectbox("풀이할 문제를 선택하세요:", q_options)
                q_idx = int(selected_q_label.split(".")[0].replace("Q", "")) - 1
                curr_q = questions[q_idx]
                
                # 문제 지시문 카드
                st.markdown(f'<div class="study-card"><h4>🎯 {curr_q["title"]}</h4></div>', unsafe_allow_html=True)
                st.markdown(curr_q["description"])
                
                # 코드 에디터
                code_key = f"code_{unit_info['key']}_{curr_q['id']}"
                if code_key not in st.session_state["user_codes"]:
                    st.session_state["user_codes"][code_key] = curr_q["starter_code"]
                    
                user_code = st.text_area(
                    "💻 나의 풀이 코드 작성:",
                    value=st.session_state["user_codes"][code_key],
                    height=200,
                    key=f"editor_{code_key}"
                )
                st.session_state["user_codes"][code_key] = user_code
                
                btn_col1, btn_col2, btn_col3 = st.columns([1.5, 1.5, 5])
                with btn_col1:
                    run_clicked = st.button("▶ 코드 실행", type="primary", use_container_width=True)
                with btn_col2:
                    if st.button("↺ 초기화", use_container_width=True):
                        st.session_state["user_codes"][code_key] = curr_q["starter_code"]
                        st.rerun()
                        
                # 실행 결과 출력
                if run_clicked:
                    st.markdown("#### 🚀 실행 결과")
                    with st.spinner("파이썬 코드를 실행 중입니다..."):
                        res = run_python_code(
                            code=user_code,
                            setup_code=setup_code,
                            data_dir=data_dir_str
                        )
                        
                        if res["success"]:
                            if res["stdout"].strip():
                                st.markdown(f'<div class="console-box">{res["stdout"]}</div>', unsafe_allow_html=True)
                            if res["dataframe"] is not None:
                                st.markdown("**출력 데이터프레임:**")
                                st.dataframe(res["dataframe"], use_container_width=True)
                            if res["figures"]:
                                st.markdown("**시각화 차트:**")
                                for fig in res["figures"]:
                                    st.pyplot(fig)
                            if not res["stdout"].strip() and res["dataframe"] is None and not res["figures"]:
                                st.success("코드가 오류 없이 성공적으로 실행되었습니다. (출력값 없음)")
                        else:
                            st.error("코드 실행 중 에러가 발생했습니다.")
                            st.code(res["error"], language="python")

        # ----------------------------------------------------
        # 탭 3: 모범 답안 & 해설
        # ----------------------------------------------------
        with tab_answer:
            data_bundle = load_practice_and_answers(unit_info)
            questions = data_bundle.get("questions", [])
            
            if not questions:
                st.info("정답지가 준비 중입니다.")
            else:
                ans_q_options = [f"Q{q['id']}. {q['title']}" for q in questions]
                ans_selected_label = st.selectbox("정답을 확인할 문제 선택:", ans_q_options, key="ans_select")
                ans_idx = int(ans_selected_label.split(".")[0].replace("Q", "")) - 1
                target_q = questions[ans_idx]
                
                st.markdown(f"### 💡 {target_q['title']} 정답 및 해설")
                
                show_ans = st.checkbox("모범 답안 코드 확인하기", value=False)
                if show_ans:
                    st.markdown("#### 📝 모범 답안 코드")
                    st.code(target_q["solution_code"], language="python")
                    
                    if target_q["interpretation"].strip():
                        st.markdown("#### 🔍 결과 해석 및 주요 체크포인트")
                        st.markdown(target_q["interpretation"])
                        
                    # 작성한 코드와 모범 답안 Diff 비교
                    code_key = f"code_{unit_info['key']}_{target_q['id']}"
                    current_user_code = st.session_state["user_codes"].get(code_key, "")
                    if current_user_code.strip():
                        with st.expander("🔍 내 작성 코드 vs 모범 답안 라인별 비교 (Diff)"):
                            diff_html = generate_diff_html(current_user_code, target_q["solution_code"])
                            st.markdown(diff_html, unsafe_allow_html=True)

        # ----------------------------------------------------
        # 탭 4: 개념 퀴즈
        # ----------------------------------------------------
        with tab_quiz:
            st.markdown(f"### 📝 {unit_info['title']} 개념 확인 퀴즈")
            st.caption("난이도를 고른 뒤 [출제하기]를 눌러 5문제를 랜덤으로 풀어보세요.")
            unit_diff = st.selectbox(
                "난이도 선택",
                options=list(DIFFICULTY_OPTIONS.keys()),
                format_func=lambda d: DIFFICULTY_OPTIONS.get(d, d),
                key=f"unit_quiz_diff_{selected_version_id}_{unit_info['key']}",
            )
            unit_quizzes = get_quizzes(
                category_id=selected_cat["id"],
                unit_key=unit_info["key"],
                version_id=selected_version_id,
                include_sql=False,
                difficulty=unit_diff,
            )
            render_quiz_section(
                unit_quizzes,
                scope_key=f"unit_{selected_version_id}_{unit_info['key']}_{unit_diff}",
                unit_key=unit_info["key"],
            )

# ====================================================
# [모드 2] 🗄️ SQL 실습실 (추후 확장 및 DuckDB 엔진)
# ====================================================
elif selected_subject == "🗄️ SQL 실습실":
    sql_engine = st.session_state["sql_engine"]
    
    with st.sidebar:
        st.header("🗄️ SQL 실습 데이터베이스")
        st.caption("인메모리 분석 엔진(DuckDB/SQLite)으로 작동합니다.")
        
        with st.expander("📋 고객(customers) 테이블 구조"):
            st.code("""
customer_id (INT)
name (VARCHAR)
gender (VARCHAR)
age (INT)
city (VARCHAR)
grade (VARCHAR)
join_date (DATE)
            """)
            
        with st.expander("📦 상품(products) 테이블 구조"):
            st.code("""
product_id (INT)
product_name (VARCHAR)
category (VARCHAR)
price (INT)
stock (INT)
            """)
            
        with st.expander("🛒 주문(orders) 테이블 구조"):
            st.code("""
order_id (INT)
customer_id (INT)
product_id (INT)
quantity (INT)
order_date (DATE)
status (VARCHAR)
            """)
            
        st.markdown("---")
        st.info("💡 **확장 로드맵**: 추후 `Study_SQL/` 폴더에 교재 문서를 추가하면 자동으로 커리큘럼에 등록됩니다.")

    st.subheader("🗄️ SQL 쿼리 인터랙티브 실습실")
    
    sql_q_options = [q["title"] for q in SQL_CURRICULUM]
    selected_sql_title = st.selectbox("실습할 SQL 문제를 선택하세요:", sql_q_options)
    sql_q = next(q for q in SQL_CURRICULUM if q["title"] == selected_sql_title)
    
    st.markdown(f"""
    <div class="study-card">
        {sql_q['desc']}
    </div>
    """, unsafe_allow_html=True)
    
    sql_editor_key = f"sql_code_{sql_q['id']}"
    if sql_editor_key not in st.session_state["user_codes"]:
        st.session_state["user_codes"][sql_editor_key] = sql_q["starter"]
        
    user_sql = st.text_area(
        "SQL 쿼리 작성:",
        value=st.session_state["user_codes"][sql_editor_key],
        height=180,
        key=f"editor_{sql_editor_key}"
    )
    st.session_state["user_codes"][sql_editor_key] = user_sql
    
    col1, col2, col3 = st.columns([1.5, 1.5, 5])
    with col1:
        run_sql = st.button("▶ SQL 실행", type="primary", use_container_width=True)
    with col2:
        if st.button("↺ 초기화", key="sql_reset", use_container_width=True):
            st.session_state["user_codes"][sql_editor_key] = sql_q["starter"]
            st.rerun()
            
    if run_sql:
        st.markdown("#### 📊 쿼리 실행 결과")
        res = sql_engine.run_query(user_sql)
        if res["success"]:
            st.success(f"조회 성공: 총 **{res['row_count']}건**의 레코드가 반환되었습니다.")
            st.dataframe(res["df"], use_container_width=True)
        else:
            st.error(f"SQL 오류: {res['error']}")
            
    st.divider()
    with st.expander("💡 모범 SQL 정답 쿼리 및 해설 확인"):
        st.code(sql_q["solution"], language="sql")
        st.markdown(f"**해설:** {sql_q['explanation']}")

# ====================================================
# [모드 3] 📝 퀴즈 풀기 (글로벌 퀴즈 모드)
# ====================================================
else:
    with st.sidebar:
        st.header("📝 퀴즈 필터 설정")
        release_versions = get_release_versions()
        default_ver_id = get_default_version_id()
        version_ids = [v["id"] for v in release_versions]
        default_ver_idx = version_ids.index(default_ver_id) if default_ver_id in version_ids else len(version_ids) - 1
        version_labels = {v["id"]: v["label"] for v in release_versions}

        quiz_version_id = st.selectbox(
            "교육 Step / 버전 선택",
            options=version_ids,
            index=default_ver_idx,
            format_func=lambda vid: version_labels.get(vid, vid),
            key="quiz_release_version",
        )

        include_sql_quiz = st.checkbox(
            "🗄️ SQL 기초 문항 포함",
            value=True,
            key="quiz_include_sql",
        )

        quiz_categories = get_quiz_categories(
            version_id=quiz_version_id,
            include_sql=include_sql_quiz,
        )
        cat_option_ids = ["all"] + [c["id"] for c in quiz_categories]
        cat_option_labels = {"all": "📚 전체 대단원"}
        cat_option_labels.update({c["id"]: c["label"] for c in quiz_categories})

        selected_quiz_cat = st.selectbox(
            "카테고리 선택",
            options=cat_option_ids,
            format_func=lambda cid: cat_option_labels.get(cid, cid),
            key=f"quiz_cat_select_{quiz_version_id}_{int(include_sql_quiz)}",
        )

        selected_quiz_diff = st.selectbox(
            "난이도 선택",
            options=list(DIFFICULTY_OPTIONS.keys()),
            format_func=lambda d: DIFFICULTY_OPTIONS.get(d, d),
            key="quiz_difficulty_select",
        )

    st.subheader("📝 개념 확인 퀴즈 풀기")
    st.caption(
        f"현재 필터: **{version_labels.get(quiz_version_id, quiz_version_id)}** · "
        f"**{cat_option_labels.get(selected_quiz_cat, selected_quiz_cat)}** · "
        f"난이도 **{DIFFICULTY_OPTIONS.get(selected_quiz_diff, selected_quiz_diff)}**"
    )

    global_quizzes = get_quizzes(
        category_id=selected_quiz_cat,
        version_id=quiz_version_id,
        include_sql=include_sql_quiz,
        difficulty=selected_quiz_diff,
    )
    render_quiz_section(
        global_quizzes,
        scope_key=f"global_{quiz_version_id}_{selected_quiz_cat}_{int(include_sql_quiz)}_{selected_quiz_diff}",
    )
