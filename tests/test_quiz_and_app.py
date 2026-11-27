"""
tests/test_quiz_and_app.py
quiz_manager 단위 테스트 및 Streamlit AppTest UI 통합 테스트
"""

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.quiz_manager import (
    QUIZ_BANK,
    QUIZ_TYPE_LABELS,
    SQL_CATEGORY_ID,
    calculate_quiz_summary,
    get_quiz_categories,
    get_quizzes,
    grade_answer,
)


def test_quiz_bank_covers_all_required_categories():
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
    counts = {cid: 0 for cid in expected_categories}
    seen_ids = set()

    for q in QUIZ_BANK:
        assert q["id"] not in seen_ids
        seen_ids.add(q["id"])
        assert q["type"] in QUIZ_TYPE_LABELS
        assert q["question"].strip()
        assert q["hint"].strip()
        assert len(q["answers"]) >= 1
        assert q["explanation"].strip()
        if q["category_id"] in counts:
            counts[q["category_id"]] += 1

    for cid, cnt in counts.items():
        assert cnt >= 3, f"{cid} has only {cnt} questions (expected >= 3)"


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


def test_version_filtering_and_summary():
    v10_cats = {c["id"] for c in get_quiz_categories(version_id="v1.0", include_sql=False)}
    assert "python_basics" in v10_cats
    assert "preprocessing" in v10_cats
    assert "machine_learning" not in v10_cats
    assert "model_evaluation" not in v10_cats

    v10_prep = get_quizzes(category_id="preprocessing", version_id="v1.0", include_sql=False)
    assert [q["id"] for q in v10_prep] == ["prep_q1", "prep_q2"]

    v11_cats = {c["id"] for c in get_quiz_categories(version_id="v1.1", include_sql=False)}
    assert "machine_learning" in v11_cats
    assert "model_evaluation" not in v11_cats

    v13_cats = {c["id"] for c in get_quiz_categories(version_id="v1.3", include_sql=True)}
    assert "model_evaluation" in v13_cats
    assert SQL_CATEGORY_ID in v13_cats

    sample_qs = get_quizzes(category_id="python_basics", version_id="v1.3", include_sql=False)
    results = {
        sample_qs[0]["id"]: grade_answer(sample_qs[0], "len"),
        sample_qs[1]["id"]: grade_answer(sample_qs[1], "wrong"),
        sample_qs[2]["id"]: grade_answer(sample_qs[2], ""),
    }
    summary = calculate_quiz_summary(sample_qs, results)
    assert summary["total"] == 3
    assert summary["answered"] == 2
    assert summary["correct"] == 1
    assert summary["accuracy"] == 33.3


def test_apptest_unit_quiz_tab_renders_and_grades():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=20)
    at.run()
    assert not at.exception

    # 기본 선택은 Cheat Sheet이므로 일반 실습 단원([0] Python Basics)으로 전환
    cat_select = next(sb for sb in at.sidebar.selectbox if sb.label == "대단원 선택")
    cat_select.set_value("🐍 [0] Python Basics").run()
    assert not at.exception

    tab_labels = [t.label for t in at.tabs]
    assert "📝 4. 개념 퀴즈" in tab_labels

    # 단원 내 개념 퀴즈의 첫 번째 문항(py_q1)에 정답 입력 후 채점
    py_q1_input = next(ti for ti in at.text_input if ti.key and ti.key.endswith("_py_q1"))
    py_q1_input.set_value("len()").run()

    check_btn = next(b for b in at.button if b.key and b.key.endswith("_py_q1"))
    check_btn.click().run()
    assert not at.exception
    assert any("정답입니다" in s.value for s in at.success)


def test_apptest_global_quiz_mode_filter_hint_grade_reset():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=20)
    at.run()
    assert not at.exception

    # 상단 글로벌 [📝 퀴즈 풀기] 모드로 전환
    subj = next(sc for sc in at.get("segmented_control") if sc.label == "과목 선택")
    subj.set_value("📝 퀴즈 풀기").run()
    assert not at.exception

    # 버전 v1.0 및 SQL 카테고리 선택 테스트
    ver_sb = next(sb for sb in at.sidebar.selectbox if sb.label == "교육 Step / 버전 선택")
    ver_sb.set_value("v1.0").run()
    assert not at.exception

    cat_sb = next(sb for sb in at.sidebar.selectbox if sb.label == "카테고리 선택")
    cat_sb.set_value("sql").run()
    assert not at.exception

    # 힌트 토글 활성화 확인
    hint_toggle = next(tg for tg in at.toggle if tg.key and tg.key.endswith("_sql_q1"))
    hint_toggle.set_value(True).run()
    assert any("힌트:" in inf.value for inf in at.info)

    # 정답 입력 후 전체 채점
    sql_q1_input = next(ti for ti in at.text_input if ti.key and ti.key.endswith("_sql_q1"))
    sql_q1_input.set_value("where").run()

    grade_all_btn = next(b for b in at.button if b.key and b.key.startswith("grade_all_"))
    grade_all_btn.click().run()
    assert not at.exception
    assert any("1 / 3" == m.value for m in at.metric)

    # 다시 풀기(초기화) 버튼 클릭 시 점수 0 / 3 복귀
    reset_btn = next(b for b in at.button if b.key and b.key.startswith("reset_all_"))
    reset_btn.click().run()
    assert not at.exception
    assert any("0 / 3" == m.value for m in at.metric)


def test_apptest_answer_edit_invalidates_previous_grade():
    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=20)
    at.run()
    assert not at.exception

    subj = next(sc for sc in at.get("segmented_control") if sc.label == "과목 선택")
    subj.set_value("📝 퀴즈 풀기").run()
    cat_sb = next(sb for sb in at.sidebar.selectbox if sb.label == "카테고리 선택")
    cat_sb.set_value("sql").run()

    # 정답 입력 후 채점 -> 1 / 3 및 정답 메시지 확인
    sql_q1_input = next(ti for ti in at.text_input if ti.key and ti.key.endswith("_sql_q1"))
    sql_q1_input.set_value("WHERE").run()
    check_btn = next(b for b in at.button if b.key and b.key.endswith("_sql_q1"))
    check_btn.click().run()
    assert not at.exception
    assert any("1 / 3" == m.value for m in at.metric)
    assert any("정답입니다" in s.value for s in at.success)

    # 입력값 변경 시 이전 채점 결과 무효화 -> 점수 0 / 3 및 정답 메시지 제거 확인
    sql_q1_input = next(ti for ti in at.text_input if ti.key and ti.key.endswith("_sql_q1"))
    sql_q1_input.set_value("ORDER BY").run()
    assert not at.exception
    assert any("0 / 3" == m.value for m in at.metric)
    assert not any("정답입니다" in s.value for s in at.success)
