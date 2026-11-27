"""
quiz_manager.py
Code Study — 초보자 친화적 개념 퀴즈 Bank 및 유연한 채점 엔진

[0] Python Basics ~ [8] Model_Evaluation 및 SQL 기초를 커버하는
빈칸 넣기(fill_blank), 주관식(short_answer), O/X(ox) 문항과
릴리즈 버전(v1.0~v1.3) 연동 필터링 및 채점 로직을 제공합니다.
"""

import re
from typing import Any, Dict, List, Optional

from modules.notebook_loader import get_curriculum_by_version

SQL_CATEGORY_ID = "sql"
SQL_CATEGORY_LABEL = "🗄️ SQL 기초"

QUIZ_TYPE_LABELS: Dict[str, str] = {
    "fill_blank": "빈칸 넣기",
    "short_answer": "주관식",
    "ox": "O / X",
}

QUIZ_BANK: List[Dict[str, Any]] = [
    # ------------------------------------------------------------
    # [0] Python Basics
    # ------------------------------------------------------------
    {
        "id": "py_q1",
        "category_id": "python_basics",
        "category_label": "🐍 [0] Python Basics",
        "unit_keys": ["py_basic_1", "py_basic_3"],
        "type": "fill_blank",
        "question": "리스트 `nums = [10, 20, 30]`의 길이(원소 개수)를 구하려면 `___(nums)`를 사용합니다. 빈칸에 들어갈 내장 함수 이름은?",
        "hint": "length의 앞 3글자입니다.",
        "answers": ["len", "len()"],
        "explanation": "`len()` 함수는 리스트, 문자열, 딕셔너리 등의 길이(요소 개수)를 반환합니다. 예: `len([10, 20, 30])`은 `3`입니다.",
    },
    {
        "id": "py_q2",
        "category_id": "python_basics",
        "category_label": "🐍 [0] Python Basics",
        "unit_keys": ["py_basic_2"],
        "type": "fill_blank",
        "question": "조건문에서 `if` 조건이 거짓일 때, 추가 조건을 순서대로 검사하려면 `___` 키워드를 사용합니다.",
        "hint": "else if를 줄여서 쓴 파이썬 예약어입니다.",
        "answers": ["elif"],
        "explanation": "파이썬에서는 `else if` 대신 `elif` 키워드를 사용해 여러 조건을 분기합니다.",
    },
    {
        "id": "py_q3",
        "category_id": "python_basics",
        "category_label": "🐍 [0] Python Basics",
        "unit_keys": ["py_basic_4", "py_basic_5"],
        "type": "short_answer",
        "question": "`{'name': 'Kim', 'age': 25}`처럼 키(key)와 값(value) 쌍으로 데이터를 저장하는 파이썬 자료형은 무엇인가요?",
        "hint": "영어로 dictionary의 줄임말(`dict`) 또는 한글로 `딕셔너리`라고 부릅니다.",
        "answers": ["dict", "딕셔너리", "dictionary"],
        "explanation": "딕셔너리(`dict`)는 중괄호 `{}`를 사용해 `key: value` 형태로 데이터를 저장하며, 키로 값을 빠르게 조회할 수 있습니다.",
    },

    # ------------------------------------------------------------
    # [1] NumPy Matrix
    # ------------------------------------------------------------
    {
        "id": "np_q1",
        "category_id": "numpy",
        "category_label": "🔢 [1] NumPy Matrix",
        "unit_keys": ["numpy_1"],
        "type": "fill_blank",
        "question": "NumPy 배열 `arr`의 행과 열 크기(차원 형태)를 튜플로 확인하려면 `arr.___` 속성을 조회합니다.",
        "hint": "배열의 '모양'을 뜻하는 영어 단어입니다.",
        "answers": ["shape", ".shape"],
        "explanation": "`arr.shape`는 2차원 배열일 때 `(행 개수, 열 개수)` 형태의 튜플을 반환합니다.",
    },
    {
        "id": "np_q2",
        "category_id": "numpy",
        "category_label": "🔢 [1] NumPy Matrix",
        "unit_keys": ["numpy_1", "numpy_2"],
        "type": "fill_blank",
        "question": "NumPy에서 0부터 4까지의 연속된 정수 배열 `[0, 1, 2, 3, 4]`를 만들려면 `np.___(5)`를 사용합니다.",
        "hint": "파이썬 내장 `range` 앞에 `a`가 붙은 NumPy 함수입니다.",
        "answers": ["arange", "np.arange", "arange(5)", "np.arange(5)"],
        "explanation": "`np.arange(5)`는 0부터 5 미만(4)까지의 정수를 담은 1차원 NumPy 배열을 생성합니다.",
    },
    {
        "id": "np_q3",
        "category_id": "numpy",
        "category_label": "🔢 [1] NumPy Matrix",
        "unit_keys": ["numpy_2"],
        "type": "ox",
        "question": "[O/X] NumPy 배열은 `for` 반복문 없이도 `arr * 2`처럼 배열 전체에 사칙연산을 한 번에 적용(벡터화 연산)할 수 있다.",
        "hint": "NumPy의 핵심 장점 중 하나가 빠른 벡터화 연산입니다.",
        "answers": ["O", "o", "true", "참", "맞다"],
        "explanation": "맞습니다(O). NumPy 배열은 원소별 벡터화 연산을 지원해 반복문보다 간결하고 빠르게 계산할 수 있습니다.",
    },

    # ------------------------------------------------------------
    # [2] Pandas & EDA
    # ------------------------------------------------------------
    {
        "id": "pd_q1",
        "category_id": "pandas",
        "category_label": "🐼 [2] Pandas & EDA",
        "unit_keys": ["pandas_1", "eda"],
        "type": "fill_blank",
        "question": "Pandas DataFrame `df`의 처음 5개 행을 미리 확인하려면 `df.___()` 메서드를 호출합니다.",
        "hint": "데이터의 '머리' 부분을 본다는 뜻의 영어 단어입니다.",
        "answers": ["head", "head()", ".head()"],
        "explanation": "`df.head()`는 기본값으로 상위 5개 행을 반환하며, `df.head(10)`처럼 개수를 지정할 수도 있습니다.",
    },
    {
        "id": "pd_q2",
        "category_id": "pandas",
        "category_label": "🐼 [2] Pandas & EDA",
        "unit_keys": ["pandas_3", "pandas_4"],
        "type": "fill_blank",
        "question": "특정 컬럼(`category`)별로 데이터를 묶어 평균이나 합계를 구할 때는 `df.___('category').mean()`처럼 작성합니다.",
        "hint": "SQL의 `GROUP BY`와 같은 역할을 하는 Pandas 메서드입니다.",
        "answers": ["groupby", "groupby()", ".groupby()"],
        "explanation": "`groupby()`는 지정한 컬럼 값에 따라 그룹을 나눈 뒤 `mean()`, `sum()`, `count()` 등의 집계를 수행합니다.",
    },
    {
        "id": "pd_q3",
        "category_id": "pandas",
        "category_label": "🐼 [2] Pandas & EDA",
        "unit_keys": ["pandas_2"],
        "type": "short_answer",
        "question": "DataFrame에서 각 값이 결측치(NaN)인지 `True`/`False`로 확인하는 Pandas 메서드 이름은 무엇인가요?",
        "hint": "`is` 뒤에 `na` 또는 `null`이 붙습니다.",
        "answers": ["isna", "isna()", ".isna()", "isnull", "isnull()", ".isnull()"],
        "explanation": "`df.isna()`(또는 `df.isnull()`)는 결측치 위치를 `True`로 표시하며, `df.isna().sum()`으로 열별 결측치 개수를 자주 셉니다.",
    },

    # ------------------------------------------------------------
    # [3] Data Visualization
    # ------------------------------------------------------------
    {
        "id": "vis_q1",
        "category_id": "visualization",
        "category_label": "📊 [3] Data Visualization",
        "unit_keys": ["vis_1"],
        "type": "short_answer",
        "question": "키, 점수 같은 연속형 수치 데이터의 구간별 분포를 막대 형태로 나타내는 대표적인 그래프 이름은 무엇인가요?",
        "hint": "영어로 histogram, 한글로는 `히스토그램`이라고 합니다.",
        "answers": ["히스토그램", "histogram", "hist", "histplot"],
        "explanation": "히스토그램(Histogram)은 연속형 데이터를 여러 구간(bin)으로 나누어 각 구간에 속한 데이터 빈도를 막대로 보여줍니다.",
    },
    {
        "id": "vis_q2",
        "category_id": "visualization",
        "category_label": "📊 [3] Data Visualization",
        "unit_keys": ["vis_2"],
        "type": "fill_blank",
        "question": "Seaborn에서 두 수치형 변수의 관계를 점으로 표현하는 산점도를 그리려면 `sns.___(data=df, x='a', y='b')`를 사용합니다.",
        "hint": "산점도(scatter)와 plot을 합친 함수 이름입니다.",
        "answers": ["scatterplot", "sns.scatterplot"],
        "explanation": "`sns.scatterplot()`은 두 연속형 변수 사이의 상관관계나 군집 패턴을 점으로 시각화합니다.",
    },
    {
        "id": "vis_q3",
        "category_id": "visualization",
        "category_label": "📊 [3] Data Visualization",
        "unit_keys": ["vis_3", "vis_4", "vis_5"],
        "type": "ox",
        "question": "[O/X] 상자 그림(Boxplot)은 데이터의 중앙값, 사분위수(Q1·Q3), 이상치 여부를 한눈에 비교할 때 유용하다.",
        "hint": "상자의 가운데 선이 중앙값, 바깥의 점들이 이상치입니다.",
        "answers": ["O", "o", "true", "참", "맞다"],
        "explanation": "맞습니다(O). Boxplot은 그룹별 분포의 중심과 퍼짐, 이상치를 간결하게 비교하는 데 매우 효과적입니다.",
    },

    # ------------------------------------------------------------
    # [4] Statistics
    # ------------------------------------------------------------
    {
        "id": "stat_q1",
        "category_id": "statistics",
        "category_label": "📐 [4] Statistics",
        "unit_keys": ["stat_1"],
        "type": "short_answer",
        "question": "데이터를 크기 순서대로 나열했을 때 정중앙에 위치하며, 평균보다 극단값(이상치)의 영향을 덜 받는 대표값은 무엇인가요?",
        "hint": "한글로 `중앙값` 또는 `중위수`, 영어로는 `median`입니다.",
        "answers": ["중앙값", "중위수", "median"],
        "explanation": "중앙값(Median)은 정렬된 데이터의 가운데 값이므로 매우 큰 값이나 작은 값이 섞여도 크게 흔들리지 않습니다.",
    },
    {
        "id": "stat_q2",
        "category_id": "statistics",
        "category_label": "📐 [4] Statistics",
        "unit_keys": ["stat_2"],
        "type": "fill_blank",
        "question": "모집단의 분포와 상관없이 표본 크기(n)가 충분히 커지면 표본평균의 분포가 정규분포에 가까워진다는 정리를 `___`라고 합니다.",
        "hint": "약어로 `CLT`라고도 부르는 통계학의 핵심 정리입니다.",
        "answers": ["중심극한정리", "CLT", "Central Limit Theorem"],
        "explanation": "중심극한정리(CLT) 덕분에 표본이 충분히 크면 정규분포를 기반으로 모평균을 추론하고 가설검정을 수행할 수 있습니다.",
    },
    {
        "id": "stat_q3",
        "category_id": "statistics",
        "category_label": "📐 [4] Statistics",
        "unit_keys": ["stat_3", "stat_4"],
        "type": "short_answer",
        "question": "가설검정에서 귀무가설이 참이라고 가정했을 때, 현재 관측된 결과 이상으로 극단적인 결과가 나올 확률을 무엇이라고 하나요?",
        "hint": "보통 0.05보다 작으면 통계적으로 유의하다고 판단하는 `p-value`입니다.",
        "answers": ["p-value", "p value", "pvalue", "유의확률", "p값"],
        "explanation": "유의확률(p-value)이 유의수준(보통 0.05)보다 작으면 귀무가설을 기각하고 대립가설을 채택하는 근거로 삼습니다.",
    },

    # ------------------------------------------------------------
    # [5] EDA 심화 프로젝트
    # ------------------------------------------------------------
    {
        "id": "eda_adv_q1",
        "category_id": "eda_advanced",
        "category_label": "🔍 [5] EDA 심화 프로젝트",
        "unit_keys": ["eda_adv_1", "eda_adv_2"],
        "type": "fill_blank",
        "question": "DataFrame에서 수치형 컬럼들 간의 상관계수 행렬을 구할 때는 `df.___(numeric_only=True)` 메서드를 사용합니다.",
        "hint": "correlation의 앞 4글자입니다.",
        "answers": ["corr", "corr()", ".corr()"],
        "explanation": "`df.corr()`는 각 변수 쌍의 피어슨 상관계수를 -1 ~ +1 사이의 값으로 계산해 줍니다.",
    },
    {
        "id": "eda_adv_q2",
        "category_id": "eda_advanced",
        "category_label": "🔍 [5] EDA 심화 프로젝트",
        "unit_keys": ["eda_adv_3"],
        "type": "short_answer",
        "question": "행과 열 기준으로 범주를 나누어 평균·합계 등 요약 통계표를 만드는 Pandas 함수 이름은 무엇인가요?",
        "hint": "엑셀의 피벗 테이블과 같은 이름(`pivot_table`)입니다.",
        "answers": ["pivot_table", "pd.pivot_table", "pivot_table()", "피벗테이블", "피벗 테이블"],
        "explanation": "`pd.pivot_table()`(또는 `df.pivot_table()`)을 사용하면 두 개 이상의 범주형 변수 조합에 따른 요약 표를 손쉽게 만들 수 있습니다.",
    },
    {
        "id": "eda_adv_q3",
        "category_id": "eda_advanced",
        "category_label": "🔍 [5] EDA 심화 프로젝트",
        "unit_keys": ["eda_adv_4"],
        "type": "ox",
        "question": "[O/X] 다변량 분석(Multivariate Analysis)은 한 번에 하나의 변수만 따로 보는 것이 아니라, 여러 변수 간의 관계와 상호작용을 함께 분석한다.",
        "hint": "'다(Multi)'는 여러 개를 뜻합니다.",
        "answers": ["O", "o", "true", "참", "맞다"],
        "explanation": "맞습니다(O). 다변량 분석은 2개 이상의 변수가 결과에 미치는 복합적인 패턴을 파악할 때 사용합니다.",
    },

    # ------------------------------------------------------------
    # [6] 데이터 전처리 & 파이프라인
    # ------------------------------------------------------------
    {
        "id": "prep_q1",
        "category_id": "preprocessing",
        "category_label": "⚙️ [6] 데이터 전처리 & 파이프라인",
        "unit_keys": ["prep_1", "prep_2"],
        "type": "fill_blank",
        "question": "결측치(NaN)를 삭제하지 않고 0이나 평균값 등 특정 값으로 채울 때는 `df.___(0)` 메서드를 사용합니다.",
        "hint": "`fill`과 결측치를 뜻하는 `na`를 합친 이름입니다.",
        "answers": ["fillna", "fillna()", ".fillna()"],
        "explanation": "`df.fillna(값)`은 결측치를 지정한 값으로 대체하며, `drop` 대신 데이터를 보존하고 싶을 때 활용합니다.",
    },
    {
        "id": "prep_q2",
        "category_id": "preprocessing",
        "category_label": "⚙️ [6] 데이터 전처리 & 파이프라인",
        "unit_keys": ["prep_3", "prep_4"],
        "type": "short_answer",
        "question": "특성(Feature)의 평균을 0, 표준편차를 1로 변환하는 Scikit-learn 스케일러 클래스 이름은 무엇인가요?",
        "hint": "표준화를 뜻하는 Standard와 Scaler를 붙여 씁니다.",
        "answers": ["StandardScaler", "StandardScaler()", "표준화"],
        "explanation": "`StandardScaler`는 각 특성을 평균 0, 표준편차 1로 표준화하여 변수 간 단위 차이를 맞춰 줍니다.",
    },
    {
        "id": "prep_q3",
        "category_id": "preprocessing",
        "category_label": "⚙️ [6] 데이터 전처리 & 파이프라인",
        "unit_keys": ["prep_5", "prep_6"],
        "type": "fill_blank",
        "question": "결측치 처리, 스케일링 같은 전처리 단계와 머신러닝 모델을 하나로 묶어 데이터 누수(Data Leakage)를 막아주는 Scikit-learn 도구는 `___`입니다.",
        "hint": "영어로 '관로/파이프라인'을 뜻하는 클래스입니다.",
        "answers": ["Pipeline", "make_pipeline", "파이프라인"],
        "explanation": "`Pipeline`을 사용하면 학습 데이터에만 전처리 기준(`fit`)을 맞추고 테스트 데이터에는 변환(`transform`)만 적용해 데이터 누수를 예방할 수 있습니다.",
    },

    # ------------------------------------------------------------
    # [7] 머신러닝
    # ------------------------------------------------------------
    {
        "id": "ml_q1",
        "category_id": "machine_learning",
        "category_label": "🤖 [7] 머신러닝",
        "unit_keys": ["ml_1", "ml_2", "ml_3"],
        "type": "fill_blank",
        "question": "데이터를 학습용(train)과 평가용(test)으로 나눌 때 사용하는 Scikit-learn 함수는 `___`입니다.",
        "hint": "train, test, split을 밑줄(`_`)로 연결한 함수입니다.",
        "answers": ["train_test_split", "train_test_split()"],
        "explanation": "`train_test_split(X, y, test_size=0.2)`처럼 호출해 모델이 보지 못한 데이터에서의 일반화 성능을 평가합니다.",
    },
    {
        "id": "ml_q2",
        "category_id": "machine_learning",
        "category_label": "🤖 [7] 머신러닝",
        "unit_keys": ["ml_4", "ml_5", "ml_6", "ml_7", "ml_8", "ml_9", "ml_10", "ml_11"],
        "type": "fill_blank",
        "question": "Scikit-learn에서 생성한 모델 객체 `model`을 학습 데이터 `(X_train, y_train)`으로 훈련시킬 때 `model.___(X_train, y_train)`를 호출합니다.",
        "hint": "데이터에 모델을 '맞춘다'는 뜻의 3글자 메서드입니다.",
        "answers": ["fit", "fit()", ".fit()"],
        "explanation": "Scikit-learn의 모든 지도학습 모델은 `fit(X, y)`로 학습하고, `predict(X)`로 예측하는 일관된 인터페이스를 제공합니다.",
    },
    {
        "id": "ml_q3",
        "category_id": "machine_learning",
        "category_label": "🤖 [7] 머신러닝",
        "unit_keys": ["ml_12", "ml_13", "ml_14", "ml_15", "ml_16", "ml_17"],
        "type": "short_answer",
        "question": "정답(레이블) 없이 비슷한 데이터끼리 K개의 그룹(클러스터)으로 묶는 대표적인 비지도학습 군집화 알고리즘은 무엇인가요?",
        "hint": "K개의 중심점(평균)을 찾는 `K-Means` 알고리즘입니다.",
        "answers": ["K-Means", "KMeans", "k means", "k평균", "k-평균"],
        "explanation": "`K-Means`는 각 군집의 중심점(Centroid)과 데이터 간 거리를 반복적으로 최소화하며 K개 그룹으로 나눕니다.",
    },

    # ------------------------------------------------------------
    # [8] 모델 평가 & 로지스틱 회귀
    # ------------------------------------------------------------
    {
        "id": "eval_q1",
        "category_id": "model_evaluation",
        "category_label": "📏 [8] 모델 평가 & 로지스틱 회귀",
        "unit_keys": ["eval_1"],
        "type": "short_answer",
        "question": "분류 모델의 실제 정답과 예측 결과를 표로 정리해 TP, FP, FN, TN 개수를 한눈에 확인하는 도구는 무엇인가요?",
        "hint": "한글로 `혼동 행렬`, 영어로는 `confusion matrix`입니다.",
        "answers": ["혼동 행렬", "혼동행렬", "confusion matrix", "confusion_matrix"],
        "explanation": "혼동 행렬(Confusion Matrix)을 통해 모델이 어떤 클래스를 얼마나 헷갈렸는지(FP, FN) 구체적으로 파악할 수 있습니다.",
    },
    {
        "id": "eval_q2",
        "category_id": "model_evaluation",
        "category_label": "📏 [8] 모델 평가 & 로지스틱 회귀",
        "unit_keys": ["eval_2"],
        "type": "short_answer",
        "question": "모델이 양성(Positive)이라고 예측한 샘플 중, 실제로도 양성인 비율을 나타내는 분류 평가 지표는 무엇인가요?",
        "hint": "한글로 `정밀도`, 영어로는 `Precision`입니다.",
        "answers": ["정밀도", "Precision"],
        "explanation": "정밀도(Precision = TP / (TP + FP))는 '양성 예측이 얼마나 정확한가'를 측정하며, 스팸 메일 필터 등에서 중요합니다.",
    },
    {
        "id": "eval_q3",
        "category_id": "model_evaluation",
        "category_label": "📏 [8] 모델 평가 & 로지스틱 회귀",
        "unit_keys": ["eval_3", "eval_4"],
        "type": "ox",
        "question": "[O/X] 로지스틱 회귀(Logistic Regression)는 이름에 '회귀'가 들어가지만 실제로는 주로 이진 분류(0 또는 1 예측) 문제에 사용된다.",
        "hint": "시그모이드 함수를 통해 0~1 사이의 확률을 출력합니다.",
        "answers": ["O", "o", "true", "참", "맞다"],
        "explanation": "맞습니다(O). 로지스틱 회귀는 선형 결합 결과를 시그모이드 함수에 통과시켜 클래스 확률을 예측하는 대표적인 분류 모델입니다.",
    },

    # ------------------------------------------------------------
    # SQL 기초
    # ------------------------------------------------------------
    {
        "id": "sql_q1",
        "category_id": SQL_CATEGORY_ID,
        "category_label": SQL_CATEGORY_LABEL,
        "unit_keys": ["sql"],
        "type": "fill_blank",
        "question": "SQL에서 `SELECT * FROM customers ___ city = 'Seoul'`처럼 특정 조건을 만족하는 행만 걸러낼 때 사용하는 절은?",
        "hint": "'어디에'를 뜻하는 영어 단어입니다.",
        "answers": ["WHERE"],
        "explanation": "`WHERE` 절은 테이블에서 조건에 맞는 행(레코드)만 필터링할 때 사용합니다.",
    },
    {
        "id": "sql_q2",
        "category_id": SQL_CATEGORY_ID,
        "category_label": SQL_CATEGORY_LABEL,
        "unit_keys": ["sql"],
        "type": "fill_blank",
        "question": "SQL에서 `grade`별로 고객 수를 세려면 `SELECT grade, COUNT(*) FROM customers ___ grade`처럼 작성합니다.",
        "hint": "그룹으로 묶는다는 뜻의 두 단어(`GROUP BY`)입니다.",
        "answers": ["GROUP BY"],
        "explanation": "`GROUP BY` 절은 지정한 컬럼 값이 같은 행들을 하나의 그룹으로 묶어 `COUNT`, `SUM`, `AVG` 등의 집계를 계산합니다.",
    },
    {
        "id": "sql_q3",
        "category_id": SQL_CATEGORY_ID,
        "category_label": SQL_CATEGORY_LABEL,
        "unit_keys": ["sql"],
        "type": "short_answer",
        "question": "`customers` 테이블과 `orders` 테이블을 공통 컬럼 `customer_id`로 연결해 함께 조회할 때 사용하는 SQL 키워드는 무엇인가요?",
        "hint": "두 테이블을 '결합한다'는 뜻의 키워드(`JOIN`)입니다.",
        "answers": ["JOIN", "INNER JOIN", "LEFT JOIN"],
        "explanation": "`JOIN`(예: `INNER JOIN`, `LEFT JOIN`)은 두 테이블의 공통 키 컬럼을 기준으로 데이터를 가로로 연결합니다.",
    },
]


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
) -> List[Dict[str, Any]]:
    """카테고리, 단원 키, 릴리즈 버전에 맞는 퀴즈 문항 목록을 반환합니다."""
    scope = _get_version_scope(version_id)
    filtered: List[Dict[str, Any]] = []

    for q in QUIZ_BANK:
        cid = q["category_id"]
        if cid == SQL_CATEGORY_ID and not include_sql:
            continue
        if category_id and category_id != "all" and cid != category_id:
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
