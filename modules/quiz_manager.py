"""
quiz_manager.py
Code Study — 초보자 친화적 개념 퀴즈 Bank 및 유연한 채점 엔진 (v2)

[0] Python Basics ~ [8] Model_Evaluation 및 SQL 기초를 커버하는
10개 챕터별 모듈(총 750문항, easy/medium/hard 각 25문항)과
난이도·릴리즈 버전(v1.0~v1.3) 필터링, 5문제 랜덤 추출 및 유연한 채점 로직을 제공합니다.
"""

import random
import re
from typing import Any, Dict, Iterable, List, Optional

from modules.notebook_loader import get_curriculum_by_version
from modules.quiz_bank import QUIZ_BANK

SQL_CATEGORY_ID = "sql"
SQL_CATEGORY_LABEL = "🗄️ SQL 기초"

QUIZ_TYPE_LABELS: Dict[str, str] = {
    "fill_blank": "빈칸 넣기",
    "short_answer": "주관식",
    "ox": "O / X",
}

DIFFICULTY_LABELS: Dict[str, str] = {
    "easy": "쉬움",
    "medium": "중간",
    "hard": "어려움",
}

DIFFICULTY_OPTIONS: Dict[str, str] = {
    "all": "전체",
    **DIFFICULTY_LABELS,
}

DEFAULT_QUIZ_SAMPLE_SIZE = 5


def _normalize_text(text: str) -> str:
    """앞뒤 공백 제거, 연속 공백 단일화, 소문자 변환."""
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    return cleaned.casefold()


def _normalize_compact(text: str) -> str:
    """함수 호출 괄호 앞뒤 공백 등 불필요한 공백을 제거한 보조 정규화."""
    normalized = _normalize_text(text)
    return re.sub(r"\s*([().])\s*", r"\1", normalized)


def grade_answer(question: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
    """사용자 답안을 복수 정답 및 공백/대소문자 유연 규칙으로 채점합니다."""
    raw = user_answer or ""
    norm = _normalize_text(raw)
    compact = _normalize_compact(raw)

    if not norm:
        return {
            "is_correct": False,
            "is_empty": True,
            "normalized_input": "",
            "accepted_answers": list(question.get("answers", [])),
            "explanation": question.get("explanation", ""),
        }

    accepted_raw = list(question.get("answers", []))
    accepted_norms = {_normalize_text(ans) for ans in accepted_raw}
    accepted_compacts = {_normalize_compact(ans) for ans in accepted_raw}

    is_correct = (norm in accepted_norms) or (compact in accepted_compacts)

    return {
        "is_correct": is_correct,
        "is_empty": False,
        "normalized_input": norm,
        "accepted_answers": accepted_raw,
        "explanation": question.get("explanation", ""),
    }


def _get_version_scope(version_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """선택된 릴리즈 버전의 활성 카테고리 및 단원 키 집합을 반환합니다."""
    if not version_id:
        return None
    categories = get_curriculum_by_version(version_id)
    cat_ids = {c["id"] for c in categories}
    unit_keys = {u["key"] for c in categories for u in c.get("units", [])}
    return {"category_ids": cat_ids, "unit_keys": unit_keys}


def get_quiz_categories(
    version_id: Optional[str] = None,
    include_sql: bool = True,
) -> List[Dict[str, str]]:
    """버전 필터를 반영한 퀴즈 카테고리 목록을 반환합니다."""
    scope = _get_version_scope(version_id)
    seen: Dict[str, str] = {}

    for q in QUIZ_BANK:
        cid = q["category_id"]
        if cid == SQL_CATEGORY_ID and not include_sql:
            continue
        if scope is not None and cid != SQL_CATEGORY_ID:
            if cid not in scope["category_ids"]:
                continue
        if cid not in seen:
            seen[cid] = q["category_label"]

    return [{"id": cid, "label": label} for cid, label in seen.items()]


def get_quizzes(
    category_id: Optional[str] = None,
    unit_key: Optional[str] = None,
    version_id: Optional[str] = None,
    include_sql: bool = True,
    difficulty: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """카테고리, 단원 키, 릴리즈 버전, 난이도에 맞는 퀴즈 문항 목록을 반환합니다."""
    scope = _get_version_scope(version_id)
    filtered: List[Dict[str, Any]] = []

    for q in QUIZ_BANK:
        cid = q["category_id"]
        if cid == SQL_CATEGORY_ID and not include_sql:
            continue
        if category_id and category_id != "all" and cid != category_id:
            continue
        if difficulty and difficulty != "all" and q.get("difficulty") != difficulty:
            continue
        if scope is not None and cid != SQL_CATEGORY_ID:
            if cid not in scope["category_ids"]:
                continue
            # 해당 버전에서 활성화된 단원 키가 하나도 겹치지 않으면 제외
            q_units = set(q.get("unit_keys", []))
            if q_units and not (q_units & scope["unit_keys"]):
                continue
        filtered.append(q)

    if unit_key:
        # 현재 소단원에 직접 매칭된 문항을 우선 배치하고, 없으면 대단원 전체 문항 반환
        exact = [q for q in filtered if unit_key in q.get("unit_keys", [])]
        if exact:
            others = [q for q in filtered if unit_key not in q.get("unit_keys", [])]
            return exact + others

    return filtered


def sample_quizzes(
    questions: List[Dict[str, Any]],
    count: int = DEFAULT_QUIZ_SAMPLE_SIZE,
    rng: Optional[random.Random] = None,
    unit_key: Optional[str] = None,
    exclude_ids: Optional[Iterable[str]] = None,
) -> List[Dict[str, Any]]:
    """문항 풀에서 최대 count개의 문항을 중복 없이 랜덤 추출합니다.

    - exclude_ids: 재출제 시 후보 풀이 충분하면(len(pool) - len(prev_ids_in_pool) >= k) 직전 문항을 제외합니다.
    - unit_key: 지정 시 해당 소단원 일치 문항을 우선 추첨하고 부족분만 같은 대단원 풀에서 보충합니다.
    """
    if not questions or count <= 0:
        return []
    picker = rng if rng is not None else random
    k = min(count, len(questions))

    exclude_set = set(exclude_ids) if exclude_ids else set()
    if exclude_set:
        candidates = [q for q in questions if q["id"] not in exclude_set]
        if len(candidates) < k:
            candidates = list(questions)
    else:
        candidates = list(questions)

    if unit_key:
        exact = [q for q in candidates if unit_key in q.get("unit_keys", [])]
        if len(exact) >= k:
            return picker.sample(exact, k)
        others = [q for q in candidates if unit_key not in q.get("unit_keys", [])]
        needed = min(k - len(exact), len(others))
        return exact + picker.sample(others, needed)

    return picker.sample(candidates, k)


def calculate_quiz_summary(
    questions: List[Dict[str, Any]],
    results_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """퀴즈 문항 리스트와 채점 결과 딕셔너리로부터 점수 및 정답률을 계산합니다."""
    total = len(questions)
    answered = 0
    correct = 0

    for q in questions:
        res = results_by_id.get(q["id"])
        if res and not res.get("is_empty", False):
            answered += 1
            if res.get("is_correct", False):
                correct += 1

    accuracy = round((correct / total) * 100, 1) if total > 0 else 0.0
    return {
        "total": total,
        "answered": answered,
        "correct": correct,
        "accuracy": accuracy,
    }
