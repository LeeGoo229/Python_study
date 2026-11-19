"""
python_runner.py
사용자가 입력한 파이썬 코드를 안전하게 실행하고
표준 출력, 에러, Matplotlib/Seaborn 차트, DataFrame을 캡처하여 반환하는 모듈
"""

import ast
import hashlib
import io
import os
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import matplotlib

    matplotlib.use("Agg")  # GUI 없는 환경(웹 서버)용 백엔드
    import matplotlib.pyplot as plt

    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    matplotlib = None
    plt = None

_MAGIC_LINE_RE = re.compile(r"^\s*(?:%%?[A-Za-z_]|!)")


def _strip_magics(source: str) -> str:
    """Jupyter 매직/셸 명령 라인을 빈 줄로 치환해 행 번호를 유지합니다."""
    return "\n".join(
        "" if _MAGIC_LINE_RE.match(line) else line
        for line in source.splitlines()
    )


def _is_pandas_tabular(obj: Any) -> bool:
    """pandas DataFrame 또는 Series 인스턴스 여부를 판별합니다."""
    cls = type(obj)
    return (
        getattr(cls, "__module__", "").startswith("pandas")
        and getattr(cls, "__name__", "") in ("DataFrame", "Series")
    )


def _resolve_target_cwd(data_dir: str, cwd: Optional[str]) -> Optional[str]:
    """실행 시 사용할 작업 디렉터리(CWD)를 결정합니다."""
    if cwd and os.path.isdir(cwd):
        return str(Path(cwd).resolve())
    if data_dir and os.path.isdir(data_dir):
        data_path = Path(data_dir).resolve()
        # 노트북의 상대 경로('data/...')는 보통 data 폴더의 상위 단원 폴더 기준
        if data_path.name == "data":
            return str(data_path.parent)
        return str(data_path)
    return None


def _parse_module_ast(source: str) -> Optional[ast.Module]:
    """소스를 AST로 파싱하며, 구문 오류 시 매직 커맨드 제거 후 재시도합니다."""
    if not source or not source.strip():
        return None
    try:
        return ast.parse(source, mode="exec")
    except SyntaxError:
        cleaned = _strip_magics(source)
        if not cleaned.strip():
            return None
        return ast.parse(cleaned, mode="exec")


def _exec_ast_code(
    source: str,
    exec_globals: Dict[str, Any],
    filename: str = "<user_code>",
    eval_last_expr: bool = True,
) -> Any:
    """AST 기반으로 코드를 실행하고 마지막 문장이 표현식이면 평가 값을 반환합니다."""
    tree = _parse_module_ast(source)
    if tree is None or not tree.body:
        return None

    if eval_last_expr and isinstance(tree.body[-1], ast.Expr):
        last_expr = tree.body.pop()
        if tree.body:
            exec(compile(tree, filename, "exec"), exec_globals)
        expr_ast = ast.Expression(body=last_expr.value)
        ast.fix_missing_locations(expr_ast)
        return eval(compile(expr_ast, filename, "eval"), exec_globals)

    exec(compile(tree, filename, "exec"), exec_globals)
    return None


def run_python_code(
    code: str,
    setup_code: str = "",
    data_dir: str = "",
    cwd: Optional[str] = None,
    namespace: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    제공된 파이썬 코드를 실행하고 결과를 캡처하여 반환합니다.

    - `cwd` 또는 `data_dir` 기준으로 상대 경로(`data/...`) 작업 디렉터리를 임시 전환합니다.
    - `namespace`를 전달하면 단원 내 이전 셀 실행 변수와 setup 상태를 유지합니다.
    - `display(...)` 호출 및 AST 기반 마지막 표현식 평가를 지원합니다.
    """
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    old_cwd = os.getcwd()

    # Matplotlib 이전 플롯 초기화
    if HAS_MPL and plt:
        plt.close("all")

    exec_globals: Dict[str, Any] = namespace if namespace is not None else {}
    exec_globals.setdefault("__name__", "__main__")
    exec_globals.setdefault("Path", Path)

    # 데이터 경로가 있으면 DATA_DIR 환경 설정 (setup이 없을 때도 활용 가능)
    if data_dir and os.path.isdir(data_dir):
        resolved_data_dir = Path(data_dir).resolve()
        exec_globals.setdefault("DATA_DIR", resolved_data_dir)
        exec_globals.setdefault("colab_data", resolved_data_dir)

    figures: List[Any] = []
    dataframes: List[Any] = []
    dataframe_result = None
    success = False
    error_msg = None

    def _display(*objs: Any, **kwargs: Any) -> None:
        nonlocal dataframe_result
        for obj in objs:
            if _is_pandas_tabular(obj):
                dataframes.append(obj)
                dataframe_result = obj
            print(obj)

    # 재사용되는 namespace에서도 항상 현재 호출의 캡처용 display로 바인딩
    exec_globals["display"] = _display

    target_cwd = _resolve_target_cwd(data_dir, cwd)

    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        if target_cwd:
            os.chdir(target_cwd)

        # 1. Setup 코드 사전 실행 (동일 namespace에서는 중복 실행 방지)
        if setup_code and setup_code.strip():
            setup_hashes = exec_globals.setdefault("__runner_setup_hashes__", set())
            setup_hash = hashlib.sha256(setup_code.encode("utf-8")).hexdigest()
            if setup_hash not in setup_hashes:
                _exec_ast_code(
                    setup_code,
                    exec_globals,
                    filename="<setup>",
                    eval_last_expr=False,
                )
                setup_hashes.add(setup_hash)

        # 2. 사용자 작성 코드 실행 (AST 기반 마지막 표현식 안전 평가)
        eval_res = _exec_ast_code(
            code,
            exec_globals,
            filename="<user_code>",
            eval_last_expr=True,
        )
        if eval_res is not None:
            if _is_pandas_tabular(eval_res):
                dataframes.append(eval_res)
                dataframe_result = eval_res
            else:
                print(eval_res)

        success = True

        # 3. 생성된 Matplotlib Figure 캡처
        if HAS_MPL and plt:
            for num in plt.get_fignums():
                fig = plt.figure(num)
                if fig.axes:  # 축이 그려진 유효한 그래프만
                    figures.append(fig)

    except Exception:
        success = False
        error_msg = traceback.format_exc()
    finally:
        os.chdir(old_cwd)
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    return {
        "success": success,
        "stdout": stdout_capture.getvalue(),
        "stderr": stderr_capture.getvalue(),
        "figures": figures,
        "dataframe": dataframe_result,
        "dataframes": dataframes,
        "namespace": exec_globals,
        "error": error_msg,
    }
