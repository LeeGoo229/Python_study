# 💻 Code Study — 인터랙티브 코딩 & 데이터 분석 학습 플랫폼

> **Python 데이터 분석 & 시각화 & 기초 통계 & SQL 쿼리 실습을 한곳에서 제공하는 인터랙티브 웹 대시보드**
>
> 🌐 **GitHub Repository**: [https://github.com/LeeGoo229/Python_study](https://github.com/LeeGoo229/Python_study)

---

## 🌟 주요 특징

1. **원스톱 인터랙티브 학습 환경 (Zero-Setup)**:
   - 로컬에 Python이나 Jupyter Notebook을 설치하지 않아도, 웹 브라우저에서 바로 **이론 학습 ➔ 문제 풀이 ➔ 실시간 코드 실행 ➔ 모범 답안 비교**가 가능합니다.
2. **검증된 주피터 노트북 189종 연동**:
   - `Study_Python`의 핵심 개념과 연습문제(`_Practice.ipynb`), 그리고 `Study_Python_Answer`의 모범 답안(`_Answer.ipynb`)이 실시간 동기화됩니다.
   - 현재 저장소에는 학습자용 126개와 관리자 정답용 63개, 총 189개 노트북(63개 실습 단원 + Reference 1개 = 총 64개 카탈로그 항목)이 있습니다.
   - 사이드바에서 릴리즈 버전(`v1.0`, `v1.1`, `v1.2`, `v1.3`, `v1.4`)을 전환하며 단계별 커리큘럼과 버전 설명을 열람할 수 있습니다.
3. **인메모리 SQL 실습실 (DuckDB/SQLite 내장)**:
   - 복잡한 데이터베이스 서버 설치 없이도 브라우저에서 바로 `SELECT`, `JOIN`, `GROUP BY` 등 실전 SQL 쿼리를 실행하고 결과를 데이터프레임으로 확인할 수 있습니다.
4. **라인별 코드 Diff 비교**:
   - 내가 작성한 코드와 모범 답안을 한눈에 비교해 다른 점과 개선점을 파악할 수 있습니다.
5. **학습 진도율 관리**:
   - 단원별 완료 체크박스와 실시간 프로그레스 바를 지원합니다.
6. **초보자 친화적 개념 퀴즈 v2 (`📝 퀴즈 풀기` & `[📝 4. 개념 퀴즈]` 탭)**:
   - `[0] Python_Basics`~`[8] Model_Evaluation` 및 `SQL 기초`를 아우르는 10개 챕터 모듈(`modules/quiz_bank/`, 각 챕터 `easy`/`medium`/`hard` 25문항씩 **총 750문항**)을 제공합니다.
   - 단원 내 `[📝 4. 개념 퀴즈]` 탭과 상단 글로벌 `[📝 퀴즈 풀기]` 모드에서 릴리즈 버전(`v1.0`~`v1.4`)·카테고리·난이도(`전체`/`쉬움`/`중간`/`어려움`) 필터링과 **`[출제하기]` 5문제 랜덤 추출(`st.session_state` 고정 및 다시 출제하기)**, 힌트 토글, 유연한 채점, 해설, 점수·정답률·다시풀기를 지원합니다.

---

## 📚 커리큘럼 구성

```text
Code_Study/
├── app.py                      # 메인 Streamlit 웹 대시보드
├── requirements.txt            # 클라우드 배포용 의존성 목록
├── modules/
│   ├── notebook_loader.py      # .ipynb 파서 및 커리큘럼 카탈로그
│   ├── python_runner.py        # 파이썬 코드 안전 실행 & 시각화/표 캡처
│   ├── sql_runner.py           # DuckDB/SQLite 인메모리 쿼리 엔진
│   ├── diff_viewer.py          # 사용자 코드 vs 정답 비교 (Diff Viewer)
│   ├── quiz_manager.py         # 개념 퀴즈 v2 필터링, 5문제 랜덤 추출 및 유연한 채점 엔진
│   └── quiz_bank/              # 10개 챕터별 개념 퀴즈 Bank (총 750문항, easy/medium/hard 각 25문항)
│
├── tests/
│   └── test_quiz_and_app.py    # 퀴즈 채점 단위 테스트 및 Streamlit AppTest UI 통합 테스트
│
├── Study_Python/               # [학습자용/업로드용] 교재 및 실습 문제
│   ├── Reference_CheatSheet/   # Python 핵심 문법 가이드 (HTML / MD / PDF 등)
│   ├── [0] Python_Basics/      # 기본 문법, 제어 흐름, 함수, 자료 분류, 라이브러리
│   ├── [1] Numpy/              # 배열과 벡터화 연산
│   ├── [2] Pandas/             # 데이터 확인, 병합, 집계, 정렬, 종합 EDA
│   ├── [3] Visualization/      # 분포, 관계, 비교, 추세, 텍스트/지도 시각화
│   ├── [4] Statistics/         # 기술통계, 정규분포/CLT, 확률, 통계적 추론
│   ├── [5] EDA_Advanced/       # 이커머스, 헬스케어, HR, 다변량 분석
│   ├── [6] Preprocessing/      # 결측/이상치, 스케일링, 인코딩, 파이프라인
│   ├── [7] Machine_Learning/   # 분류, 회귀, 트리/랜덤포레스트, 군집, PCA, 앙상블 및 실습 데이터 (Drive [11]_ML_1, [13]_ML_2, [14]_ML_3 반영)
│   └── [8] Model_Evaluation/   # 혼동 행렬, 분류 지표, 로지스틱 회귀, 평가 PDF 및 데이터 (Drive [12]_Evaluation 반영)
│
├── Study_Python_Answer/        # [관리자용/정답] 모든 실습의 모범 정답지 (.ipynb)
└── README.md                   # 프로젝트, 커리큘럼, Drive 동기화 및 백업 지침
```

---

## 🚀 배포 및 로컬 실행 방법

### 1. Streamlit Community Cloud를 통한 무료 웹 호스팅 (추천)

1. [Streamlit Community Cloud](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인합니다.
2. **`New app`** 버튼을 클릭합니다.
3. 설정 입력:
   - **Repository**: `LeeGoo229/Python_study`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: 원하는 도메인 입력 (예: `code-study.streamlit.app`)
4. **`Deploy!`** 버튼을 클릭하면 1~2분 내에 고유 URL이 발급되며 누구나 접속할 수 있습니다.
5. 이후 GitHub에 `git push`할 때마다 웹사이트가 자동으로 업데이트됩니다.

### 2. 로컬(Local)에서 실행하기

```bash
# 1. 리포지토리 클론
git clone https://github.com/LeeGoo229/Python_study.git
cd Python_study

# 2. 가상환경 생성 및 패키지 설치
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 대시보드 실행
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 대시보드를 사용할 수 있습니다.

---

## ☁️ Google Drive 연동 구조 (`Study_code`)

Google Drive의 특정 폴더인 **`Study_code`** 내부는 용도에 따라 3개로 명확히 분리 관리됩니다:

| 구분 | Google Drive 폴더명 | 설명 | 포함 내용 |
| :--- | :--- | :--- | :--- |
| **[1] 업로드용** | `업로드용` | 학습자 공유 및 대외 배포용 | `Study_Python` (치트시트, 실습 문제, 데이터셋) |
| **[2] 관리용** | `관리용` | 날짜별 교재·문제·정답 및 실행 소스 | `YYYY-MM-DD/Study_Python`, `YYYY-MM-DD/Answer`, `Sever` |
| **[3] 백업용** | `백업용` | 교체 직전 버전 압축 보관 | `YYYY-MM-DD` 아래 단계별 `_Backup` 폴더와 해당 Answer를 함께 담은 ZIP |

### 동기화 및 백업 규칙

- 상세 규칙은 [Study_code 폴더 관리 지침](Study_code_폴더관리지침.md)을 따릅니다.
- 교체 전에 이전 버전의 단계 폴더에 `_Backup`을 붙이고 같은 버전의 Answer와 함께 압축하여 업데이트 날짜 폴더에 보관합니다.
- 업로드용은 최신 자료, 관리용 날짜 폴더는 그 버전의 설명·연습문제·Answer, `Sever`는 실행 소스를 보관합니다. 저장소의 실제 답안 경로는 `Study_Python_Answer`를 유지합니다.
- 파일명·개수·해시와 앱 참조 경로를 확인하고, GitHub 및 Streamlit 배포 상태는 별도로 기록합니다.

---

## 📈 추후 SQL 확장 가이드

- `modules/sql_runner.py`에 DuckDB 기반 인메모리 테이블(`customers`, `products`, `orders`)이 기본 구성되어 있습니다.
- 새로운 SQL 실습 문제를 추가하려면 `modules/sql_runner.py`의 `SQL_CURRICULUM` 리스트에 문제 제목, 설명, 템플릿 쿼리, 모범 정답을 추가하면 웹 화면에 자동으로 반영됩니다.
- 향후 `Study_SQL/` 폴더에 `.ipynb` 또는 마크다운 문서를 추가하여 대단원을 확장할 수 있습니다.
