"""
tests/test_quiz_and_app.py
quiz_manager v2 단위 테스트 (750문항·난이도·5문제 랜덤 추출·전수 채점) 및 Streamlit AppTest UI 통합 테스트
"""

import random
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.quiz_manager import (
    DEFAULT_QUIZ_SAMPLE_SIZE,
    DIFFICULTY_LABELS,
    QUIZ_BANK,
    QUIZ_TYPE_LABELS,
    SQL_CATEGORY_ID,
    calculate_quiz_summary,
    get_quiz_categories,
    get_quizzes,
    grade_answer,
    sample_quizzes,
)


def test_quiz_bank_750_structure_uniqueness_and_all_grade_answer():
    expected_categories = [
        "python_basics",
        "numpy",
        "pandas",
        "visualization",
        "statistics",
        "eda_advanced",
        "preprocessing",
        "machine_learning",
        "model_evaluation",
        "sql",
    ]
    counts = {cid: {"easy": 0, "medium": 0, "hard": 0} for cid in expected_categories}
    seen_ids = set()
    seen_questions = set()

    assert len(QUIZ_BANK) == 750, f"Expected 750 questions, got {len(QUIZ_BANK)}"

    for q in QUIZ_BANK:
        qid = q["id"]
        assert qid not in seen_ids, f"Duplicate id: {qid}"
        seen_ids.add(qid)

        qtext = q["question"].strip()
        assert qtext, f"Empty question for {qid}"
        assert qtext not in seen_questions, f"Duplicate question text in {qid}: {qtext}"
        seen_questions.add(qtext)

        assert q["type"] in QUIZ_TYPE_LABELS, f"Invalid type in {qid}"
        assert q["difficulty"] in DIFFICULTY_LABELS, f"Invalid difficulty in {qid}"
        assert q["unit_keys"], f"Empty unit_keys in {qid}"
        assert q["hint"].strip(), f"Empty hint in {qid}"
        assert len(q["answers"]) >= 1, f"Empty answers in {qid}"
        assert q["explanation"].strip(), f"Empty explanation in {qid}"

        # 전수 grade_answer 검증: 모든 문항의 대표 정답들이 채점 통과해야 함
        for ans in q["answers"]:
            res = grade_answer(q, ans)
            assert res["is_correct"] is True, f"grade_answer failed for {qid} with answer={ans!r}"

        cid = q["category_id"]
        assert cid in counts, f"Unexpected category_id: {cid}"
        counts[cid][q["difficulty"]] += 1

    for cid, diff_counts in counts.items():
        total_cat = sum(diff_counts.values())
        assert total_cat == 75, f"{cid} has {total_cat} questions (expected 75)"
        for diff in ("easy", "medium", "hard"):
            assert diff_counts[diff] == 25, f"{cid} {diff} has {diff_counts[diff]} (expected 25)"


def test_grade_answer_flexible_matching():
    len_q = next(q for q in QUIZ_BANK if q["id"] == "py_q1")
    assert grade_answer(len_q, "len")["is_correct"] is True
    assert grade_answer(len_q, "  LEN()  ")["is_correct"] is True
    assert grade_answer(len_q, "len ( )")["is_correct"] is True
    assert grade_answer(len_q, "   ")["is_empty"] is True
    assert grade_answer(len_q, "   ")["is_correct"] is False
    assert grade_answer(len_q, "count")["is_correct"] is False

    sql_q = next(q for q in QUIZ_BANK if q["id"] == "sql_q2")
    assert grade_answer(sql_q, "  group   by ")["is_correct"] is True
    assert grade_answer(sql_q, "ORDER BY")["is_correct"] is False

    pd_q = next(q for q in QUIZ_BANK if q["id"] == "pd_q3")
    assert grade_answer(pd_q, "isnull()")["is_correct"] is True
    assert grade_answer(pd_q, "isna")["is_correct"] is True

    # vis_q2 회귀 테스트: Seaborn scatterplot만 허용 (plt.scatter / scatter 제외)
    vis_q2 = next(q for q in QUIZ_BANK if q["id"] == "vis_q2")
    assert grade_answer(vis_q2, "scatterplot")["is_correct"] is True
    assert grade_answer(vis_q2, "sns.scatterplot")["is_correct"] is True
    assert grade_answer(vis_q2, "scatter")["is_correct"] is False
    assert grade_answer(vis_q2, "plt.scatter")["is_correct"] is False


def test_version_difficulty_filtering_sampling_and_summary():
    v10_cats = {c["id"] for c in get_quiz_categories(version_id="v1.0", include_sql=False)}
    assert "python_basics" in v10_cats
    assert "preprocessing" in v10_cats
    assert "machine_learning" not in v10_cats
    assert "model_evaluation" not in v10_cats

    v10_prep = get_quizzes(category_id="preprocessing", version_id="v1.0", include_sql=False)
    assert len(v10_prep) > 0
    assert all(set(q["unit_keys"]) & {"prep_1", "prep_2", "prep_3", "prep_4"} for q in v10_prep)

    v11_cats = {c["id"] for c in get_quiz_categories(version_id="v1.1", include_sql=False)}
    assert "machine_learning" in v11_cats
    assert "model_evaluation" not in v11_cats

    v13_cats = {c["id"] for c in get_quiz_categories(version_id="v1.3", include_sql=True)}
    assert "model_evaluation" in v13_cats
    assert SQL_CATEGORY_ID in v13_cats

    # 난이도 필터링 테스트
    for diff in ("easy", "medium", "hard"):
        sql_diff = get_quizzes(category_id="sql", version_id="v1.3", include_sql=True, difficulty=diff)
        assert len(sql_diff) == 25
        assert all(q["difficulty"] == diff for q in sql_diff)

    all_sql = get_quizzes(category_id="sql", version_id="v1.3", include_sql=True, difficulty="all")
    assert len(all_sql) == 75

    # 랜덤 5문제 추출 테스트
    drawn = sample_quizzes(all_sql, count=DEFAULT_QUIZ_SAMPLE_SIZE, rng=random.Random(42))
    assert len(drawn) == 5
    assert len({q["id"] for q in drawn}) == 5

    # 요약 계산 테스트
    results = {
        drawn[0]["id"]: grade_answer(drawn[0], drawn[0]["answers"][0]),
        drawn[1]["id"]: grade_answer(drawn[1], "definitely_wrong_answer_xyz"),
        drawn[2]["id"]: grade_answer(drawn[2], ""),
    }
    summary = calculate_quiz_summary(drawn, results)
    assert summary["total"] == 5
    assert summary["answered"] == 2
    assert summary["correct"] == 1
    assert summary["accuracy"] == 20.0


def test_sample_quizzes_unit_key_priority_and_exclude_ids():
    # 1) unit_key 지정 시 소단원 일치 문항 우선 추첨 및 부족분 대단원 보충 확인
    synthetic_pool = [
        {"id": "u1_a", "unit_keys": ["u1"]},
        {"id": "u1_b", "unit_keys": ["u1"]},
        {"id": "u2_a", "unit_keys": ["u2"]},
        {"id": "u2_b", "unit_keys": ["u2"]},
        {"id": "u2_c", "unit_keys": ["u2"]},
        {"id": "u2_d", "unit_keys": ["u2"]},
        {"id": "u2_e", "unit_keys": ["u2"]},
    ]
    picked_u1 = sample_quizzes(synthetic_pool, count=5, rng=random.Random(1), unit_key="u1")
    picked_u1_ids = [q["id"] for q in picked_u1]
    assert len(picked_u1_ids) == 5
    assert "u1_a" in picked_u1_ids and "u1_b" in picked_u1_ids

    # 소단원 문항이 5개 이상이면 해당 소단원에서만 추출
    picked_u2 = sample_quizzes(synthetic_pool, count=5, rng=random.Random(1), unit_key="u2")
    assert all("u2" in q["unit_keys"] for q in picked_u2)

    # 2) exclude_ids: 후보 풀이 충분하면 직전 출제 문항 제외
    sql_pool = get_quizzes(category_id="sql", version_id="v1.3", include_sql=True, difficulty="easy")
    first_5 = sample_quizzes(sql_pool, count=5, rng=random.Random(10))
    first_ids = {q["id"] for q in first_5}
    second_5 = sample_quizzes(sql_pool, count=5, rng=random.Random(10), exclude_ids=first_ids)
    second_ids = {q["id"] for q in second_5}
    assert len(second_ids) == 5
    assert first_ids.isdisjoint(second_ids)

    # 후보 풀이 부족하면 fallback으로 정상 5개 반환
    small_pool = sql_pool[:7]
    prev_5 = {q["id"] for q in small_pool[:5]}
    fallback_5 = sample_quizzes(small_pool, count=5, rng=random.Random(3), exclude_ids=prev_5)
    assert len(fallback_5) == 5


def _answer_question_in_apptest(at: AppTest, q: dict, scope_key: str, value: str) -> None:
    input_key = f"quiz_input_{scope_key}_{q['id']}"
    if q.get("type") == "ox":
        radio = next(r for r in at.radio if r.key == input_key)
        radio.set_value(value).run()
    else:
        ti = next(t for t in at.text_input if t.key == input_key)
        ti.set_value(value).run()


def test_apptest_unit_quiz_tab_draw_fix_grade_and_redraw():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=20)
    at.run()
    assert not at.exception

    cat_select = next(sb for sb in at.sidebar.selectbox if sb.label == "대단원 선택")
    cat_select.set_value("🐍 [0] Python Basics").run()
    assert not at.exception

    assert "📝 4. 개념 퀴즈" in [t.label for t in at.tabs]

    # 난이도 선택 ('easy')
    unit_diff_sb = next(sb for sb in at.selectbox if sb.key and sb.key.startswith("unit_quiz_diff_"))
    unit_diff_sb.set_value("easy").run()
    assert not at.exception

    draw_btn = next(b for b in at.button if b.key and b.key.startswith("draw_quiz_unit_"))
    scope_key = draw_btn.key.removeprefix("draw_quiz_")
    draw_btn.click().run()
    assert not at.exception

    drawn = at.session_state["quiz_drawn"][scope_key]
    assert len(drawn) == 5
    assert all(q["difficulty"] == "easy" for q in drawn)
    assert any("0 / 5" == m.value for m in at.metric)

    # 첫 번째 문제에 정답 입력 후 채점 -> 리런 중에도 5문제 고정 유지
    first_q = drawn[0]
    _answer_question_in_apptest(at, first_q, scope_key, first_q["answers"][0])
    check_btn = next(b for b in at.button if b.key == f"quiz_check_{scope_key}_{first_q['id']}")
    check_btn.click().run()
    assert not at.exception
    assert [q["id"] for q in at.session_state["quiz_drawn"][scope_key]] == [q["id"] for q in drawn]
    assert any("1 / 5" == m.value for m in at.metric)
    assert any("정답입니다" in s.value for s in at.success)

    # 다시 출제하기 클릭 시 직전 5문항 제외 후 새 5문제 출제 및 채점 결과 초기화 확인
    prev_ids = {q["id"] for q in drawn}
    redraw_btn = next(b for b in at.button if b.key == f"draw_quiz_{scope_key}")
    redraw_btn.click().run()
    assert not at.exception
    new_drawn = at.session_state["quiz_drawn"][scope_key]
    assert len(new_drawn) == 5
    assert prev_ids.isdisjoint({q["id"] for q in new_drawn})
    assert any("0 / 5" == m.value for m in at.metric)
    assert not any("정답입니다" in s.value for s in at.success)


def test_apptest_global_quiz_mode_filter_draw_hint_grade_reset():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=20)
    at.run()
    assert not at.exception

    subj = next(sc for sc in at.get("segmented_control") if sc.label == "과목 선택")
    subj.set_value("📝 퀴즈 풀기").run()
    assert not at.exception

    ver_sb = next(sb for sb in at.sidebar.selectbox if sb.label == "교육 Step / 버전 선택")
    ver_sb.set_value("v1.0").run()
    cat_sb = next(sb for sb in at.sidebar.selectbox if sb.label == "카테고리 선택")
    cat_sb.set_value("sql").run()
    diff_sb = next(sb for sb in at.sidebar.selectbox if sb.label == "난이도 선택")
    diff_sb.set_value("medium").run()
    assert not at.exception

    draw_btn = next(b for b in at.button if b.key and b.key.startswith("draw_quiz_global_"))
    scope_key = draw_btn.key.removeprefix("draw_quiz_")
    draw_btn.click().run()
    assert not at.exception

    drawn = at.session_state["quiz_drawn"][scope_key]
    assert len(drawn) == 5
    assert all(q["category_id"] == "sql" and q["difficulty"] == "medium" for q in drawn)

    # 힌트 토글 활성화 확인 (리런 중에도 문제 유지)
    first_q = drawn[0]
    hint_toggle = next(tg for tg in at.toggle if tg.key == f"quiz_hint_{scope_key}_{first_q['id']}")
    hint_toggle.set_value(True).run()
    assert any("힌트:" in inf.value for inf in at.info)
    assert [q["id"] for q in at.session_state["quiz_drawn"][scope_key]] == [q["id"] for q in drawn]

    # 정답 입력 후 전체 채점
    _answer_question_in_apptest(at, first_q, scope_key, first_q["answers"][0])
    grade_all_btn = next(b for b in at.button if b.key == f"grade_all_{scope_key}")
    grade_all_btn.click().run()
    assert not at.exception
    assert any("1 / 5" == m.value for m in at.metric)

    # 다시 풀기(초기화) 버튼 클릭 시 점수 0 / 5 복귀 및 동일 5문제 유지
    reset_btn = next(b for b in at.button if b.key == f"reset_all_{scope_key}")
    reset_btn.click().run()
    assert not at.exception
    assert any("0 / 5" == m.value for m in at.metric)
    assert [q["id"] for q in at.session_state["quiz_drawn"][scope_key]] == [q["id"] for q in drawn]


def test_apptest_answer_edit_invalidates_previous_grade():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=20)
    at.run()
    assert not at.exception

    subj = next(sc for sc in at.get("segmented_control") if sc.label == "과목 선택")
    subj.set_value("📝 퀴즈 풀기").run()
    cat_sb = next(sb for sb in at.sidebar.selectbox if sb.label == "카테고리 선택")
    cat_sb.set_value("sql").run()

    draw_btn = next(b for b in at.button if b.key and b.key.startswith("draw_quiz_global_"))
    scope_key = draw_btn.key.removeprefix("draw_quiz_")
    draw_btn.click().run()

    drawn = at.session_state["quiz_drawn"][scope_key]
    target_q = next(q for q in drawn if q.get("type") != "ox")

    # 정답 입력 후 채점 -> 1 / 5 및 정답 메시지 확인
    _answer_question_in_apptest(at, target_q, scope_key, target_q["answers"][0])
    check_btn = next(b for b in at.button if b.key == f"quiz_check_{scope_key}_{target_q['id']}")
    check_btn.click().run()
    assert not at.exception
    assert any("1 / 5" == m.value for m in at.metric)
    assert any("정답입니다" in s.value for s in at.success)

    # 입력값 변경 시 이전 채점 결과 무효화 -> 점수 0 / 5 및 정답 메시지 제거 확인
    _answer_question_in_apptest(at, target_q, scope_key, "WRONG_ANSWER_XYZ")
    assert not at.exception
    assert any("0 / 5" == m.value for m in at.metric)
    assert not any("정답입니다" in s.value for s in at.success)
