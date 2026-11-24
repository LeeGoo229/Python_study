# Sever 실행 파일 안내 (2026-11-24 / v1.3 / 1.3.0 기준)

| 경로 | 용도 |
| --- | --- |
| `app.py` | Streamlit 앱 시작점 (`v1.3.0`, 2026-11-24 기준) |
| `requirements.txt` | `scikit-learn>=1.3.0`, `mlxtend>=0.23.0`을 포함한 실행 의존성 |
| `modules/notebook_loader.py` | 교재 카탈로그(52개 실습 단원 + Reference 1개 = 총 53항목), 버전별 매니페스트 필터링 및 노트북 로더 |
| `운영문서/release_manifest.json` | 릴리즈 버전(v1.0/v1.1/v1.2/v1.3 등)별 단원 필터링 및 버전 설명 문서 매핑 매니페스트 |
| `modules/python_runner.py` | 파이썬 실습 실행 |
| `modules/sql_runner.py` | SQL 실습 실행 |
| `modules/diff_viewer.py` | 풀이·답안 비교 |
| `README.md` | 앱 구조, Drive 동기화 및 실행 안내 |

## 데이터 및 교재 배치 안내

- Google Drive `Study_code`의 최신 `관리용` 사본(2026-11-24 추가분 포함 `Study_Python`, `Answer`)을 `app.py`와 같은 위치에 각각 `Study_Python`(121개 파일, 노트북 104개)과 `Study_Python_Answer`(모범 답안 52개)로 배치합니다.
- 머신러닝 실습 데이터는 `Study_Python/[7] Machine_Learning/data/`(`house.price.csv`, `Study.공유.csv`) 경로에 둡니다.
- 모델 평가 실습 데이터는 `Study_Python/[8] Model_Evaluation/data/titanic.csv` 경로에 로컬 캐시로 두며, 파일이 없을 경우 `sns.load_dataset('titanic')` fallback으로 로드합니다.
- 신용 데이터 전처리 실습(`Lv2_Python_1117_Data_Pre_processing_TASK`)과 California Housing 이론 예제의 최초 데이터 로드에는 인터넷 연결이 필요합니다.

## 로컬 실행 및 배포 확인

```sh
python -m pip install -r requirements.txt
streamlit run app.py
```

- GitHub `main` 브랜치 푸시 시 Streamlit Community Cloud 앱이 `app.py` (`v1.3.0`) 기준으로 자동 최신화됩니다. (현재 2026-11-24 로컬 반영 및 Drive 스테이징 완료 상태)
