"""
notebook_loader.py
Jupyter Notebook (.ipynb) 파싱 및 단원별 이론/실습/정답 로더
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

BASE_DIR = Path(__file__).resolve().parent.parent
STUDY_PY_DIR = BASE_DIR / "Study_Python"
STUDY_ANS_DIR = BASE_DIR / "Study_Python_Answer"
RELEASE_MANIFEST_PATH = BASE_DIR / "운영문서" / "release_manifest.json"

# 전체 커리큘럼 카탈로그
CURRICULUM = {
    "python": {
        "title": "🐍 Python 데이터 분석 실습",
        "categories": [
            {
                "id": "cheatsheet",
                "name": "📌 Python Cheat Sheet (Ref)",
                "units": [
                    {
                        "key": "cheatsheet_guide",
                        "title": "Python 핵심 문법 & 치트시트 가이드",
                        "type": "html_md",
                        "html_path": STUDY_PY_DIR / "Reference_CheatSheet" / "Python_Cheat_Sheets_Complete_Guide.html",
                        "md_path": STUDY_PY_DIR / "Reference_CheatSheet" / "Python_Cheat_Sheets_Complete_Guide.md"
                    }
                ]
            },
            {
                "id": "python_basics",
                "name": "🐍 [0] Python Basics",
                "units": [
                    {
                        "key": "py_basic_1",
                        "title": "1. 기본 문법과 핵심 자료형 (Syntax & DataTypes)",
                        "theory": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_1_Syntax_DataTypes.ipynb",
                        "practice": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_1_Syntax_DataTypes_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Python_Basic_1_Syntax_DataTypes_Answer.ipynb"
                    },
                    {
                        "key": "py_basic_2",
                        "title": "2. 조건문, 반복문과 제어 흐름 (Control Flow)",
                        "theory": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_2_Control_Flow.ipynb",
                        "practice": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_2_Control_Flow_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Python_Basic_2_Control_Flow_Answer.ipynb"
                    },
                    {
                        "key": "py_basic_3",
                        "title": "3. 함수 설계, 람다식과 모듈화 (Functions & Modules)",
                        "theory": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_3_Functions_Modules.ipynb",
                        "practice": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_3_Functions_Modules_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Python_Basic_3_Functions_Modules_Answer.ipynb"
                    },
                    {
                        "key": "py_basic_4",
                        "title": "4. 데이터와 변수 유형 분류 (Data Classification)",
                        "theory": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_4_Data_Classification.ipynb",
                        "practice": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_4_Data_Classification_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Python_Basic_4_Data_Classification_Answer.ipynb"
                    },
                    {
                        "key": "py_basic_5",
                        "title": "5. 필수 표준 라이브러리와 데이터 생태계 (Library Overview)",
                        "theory": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_5_Library_Overview.ipynb",
                        "practice": STUDY_PY_DIR / "[0] Python_Basics" / "Python_Basic_5_Library_Overview_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Python_Basic_5_Library_Overview_Answer.ipynb"
                    }
                ]
            },
            {
                "id": "numpy",
                "name": "🔢 [1] NumPy Matrix",
                "units": [
                    {
                        "key": "numpy_1",
                        "title": "1. N차원 배열 생성과 구조 (Array Creation & Shape)",
                        "theory": STUDY_PY_DIR / "[1] Numpy" / "Numpy_1_Array_Creation_Shape.ipynb",
                        "practice": STUDY_PY_DIR / "[1] Numpy" / "Numpy_1_Array_Creation_Shape_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Numpy_1_Array_Creation_Shape_Answer.ipynb"
                    },
                    {
                        "key": "numpy_2",
                        "title": "2. 벡터화 연산과 브로드캐스팅 (Vectorized Operations)",
                        "theory": STUDY_PY_DIR / "[1] Numpy" / "Numpy_2_Vectorized_Operations.ipynb",
                        "practice": STUDY_PY_DIR / "[1] Numpy" / "Numpy_2_Vectorized_Operations_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Numpy_2_Vectorized_Operations_Answer.ipynb"
                    }
                ]
            },
            {
                "id": "pandas",
                "name": "🐼 [2] Pandas & EDA",
                "units": [
                    {
                        "key": "pandas_1",
                        "title": "1. 데이터 확인 및 탐색 (Data Checked)",
                        "theory": STUDY_PY_DIR / "[2] Pandas" / "Pandas_1_Data_Checked.ipynb",
                        "practice": STUDY_PY_DIR / "[2] Pandas" / "Pandas_1_Data_Checked_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Pandas_1_Data_Checked_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[2] Pandas" / "data"
                    },
                    {
                        "key": "pandas_2",
                        "title": "2. 데이터 병합과 결합 (Merge & Concat)",
                        "theory": STUDY_PY_DIR / "[2] Pandas" / "Pandas_2_merge_concat.ipynb",
                        "practice": STUDY_PY_DIR / "[2] Pandas" / "Pandas_2_merge_concat_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Pandas_2_merge_concat_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[2] Pandas" / "data"
                    },
                    {
                        "key": "pandas_3",
                        "title": "3. 그룹 집계 및 피벗 (Groupby & Pivot Table)",
                        "theory": STUDY_PY_DIR / "[2] Pandas" / "Pandas_3_groupby_pivot_table.ipynb",
                        "practice": STUDY_PY_DIR / "[2] Pandas" / "Pandas_3_groupby_pivot_table_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Pandas_3_groupby_pivot_table_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[2] Pandas" / "data"
                    },
                    {
                        "key": "pandas_4",
                        "title": "4. 데이터 정렬 및 구조 재편 (Arrange Method)",
                        "theory": STUDY_PY_DIR / "[2] Pandas" / "Pandas_4_arrange_method.ipynb",
                        "practice": STUDY_PY_DIR / "[2] Pandas" / "Pandas_4_arrange_method_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Pandas_4_arrange_method_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[2] Pandas" / "data"
                    },
                    {
                        "key": "eda",
                        "title": "5. 실전 탐색적 데이터 분석 (EDA 종합)",
                        "theory": STUDY_PY_DIR / "[2] Pandas" / "EDA.ipynb",
                        "practice": STUDY_PY_DIR / "[2] Pandas" / "EDA_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "EDA_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[2] Pandas" / "data"
                    }
                ]
            },
            {
                "id": "visualization",
                "name": "📊 [3] Data Visualization",
                "units": [
                    {
                        "key": "vis_1",
                        "title": "1. 단일 변수 및 분포 시각화 (Distribution)",
                        "theory": STUDY_PY_DIR / "[3] Visualization" / "Visualization_1_distribution.ipynb",
                        "practice": STUDY_PY_DIR / "[3] Visualization" / "Visualization_1_distribution_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Visualization_1_distribution_Answer.ipynb"
                    },
                    {
                        "key": "vis_2",
                        "title": "2. 두 변수 간 관계 시각화 (Relationship)",
                        "theory": STUDY_PY_DIR / "[3] Visualization" / "Visualization_2_relationship.ipynb",
                        "practice": STUDY_PY_DIR / "[3] Visualization" / "Visualization_2_relationship_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Visualization_2_relationship_Answer.ipynb"
                    },
                    {
                        "key": "vis_3",
                        "title": "3. 범주형 그룹 비교 시각화 (Comparison)",
                        "theory": STUDY_PY_DIR / "[3] Visualization" / "Visualization_3_comparison.ipynb",
                        "practice": STUDY_PY_DIR / "[3] Visualization" / "Visualization_3_comparison_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Visualization_3_comparison_Answer.ipynb"
                    },
                    {
                        "key": "vis_4",
                        "title": "4. 시계열 및 추세 시각화 (Trend)",
                        "theory": STUDY_PY_DIR / "[3] Visualization" / "Visualization_4_trend.ipynb",
                        "practice": STUDY_PY_DIR / "[3] Visualization" / "Visualization_4_trend_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Visualization_4_trend_Answer.ipynb"
                    },
                    {
                        "key": "vis_5",
                        "title": "5. 텍스트 워드클라우드 & Folium 지도 (Wordcloud & Folium)",
                        "theory": STUDY_PY_DIR / "[3] Visualization" / "Visualization_5_wordcloud_folium.ipynb",
                        "practice": STUDY_PY_DIR / "[3] Visualization" / "Visualization_5_wordcloud_folium_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Visualization_5_wordcloud_folium_Answer.ipynb"
                    }
                ]
            },
            {
                "id": "statistics",
                "name": "📐 [4] Statistics",
                "units": [
                    {
                        "key": "stat_1",
                        "title": "1. 기술통계와 데이터 분포 (Descriptive)",
                        "theory": STUDY_PY_DIR / "[4] Statistics" / "Statistics_1_descriptive.ipynb",
                        "practice": STUDY_PY_DIR / "[4] Statistics" / "Statistics_1_descriptive_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Statistics_1_descriptive_Answer.ipynb"
                    },
                    {
                        "key": "stat_2",
                        "title": "2. 정규분포, Z점수, 중심극한정리 (Normal & CLT)",
                        "theory": STUDY_PY_DIR / "[4] Statistics" / "Statistics_2_normal_clt.ipynb",
                        "practice": STUDY_PY_DIR / "[4] Statistics" / "Statistics_2_normal_clt_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Statistics_2_normal_clt_Answer.ipynb"
                    },
                    {
                        "key": "stat_3",
                        "title": "3. 확률과 핵심 확률분포 (Probability)",
                        "theory": STUDY_PY_DIR / "[4] Statistics" / "Statistics_3_probability.ipynb",
                        "practice": STUDY_PY_DIR / "[4] Statistics" / "Statistics_3_probability_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Statistics_3_probability_Answer.ipynb"
                    },
                    {
                        "key": "stat_4",
                        "title": "4. 추론통계, 상관, 회귀분석 (Inference & Regression)",
                        "theory": STUDY_PY_DIR / "[4] Statistics" / "Statistics_4_inference_extension.ipynb",
                        "practice": STUDY_PY_DIR / "[4] Statistics" / "Statistics_4_inference_extension_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Statistics_4_inference_extension_Answer.ipynb"
                    }
                ]
            },
            {
                "id": "eda_advanced",
                "name": "🔍 [5] EDA 심화 프로젝트",
                "units": [
                    {
                        "key": "eda_adv_1",
                        "title": "1. 이커머스 비즈니스 탐색과 이상치 탐지 (E-Commerce EDA)",
                        "theory": STUDY_PY_DIR / "[5] EDA_Advanced" / "EDA_1_Overview_ECommerce.ipynb",
                        "practice": STUDY_PY_DIR / "[5] EDA_Advanced" / "EDA_1_Overview_ECommerce_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "EDA_1_Overview_ECommerce_Answer.ipynb"
                    },
                    {
                        "key": "eda_adv_2",
                        "title": "2. 헬스케어 심장 질환 환자 위험 인자 분석 (Heart Disease)",
                        "theory": STUDY_PY_DIR / "[5] EDA_Advanced" / "EDA_2_Healthcare_Heart_Disease.ipynb",
                        "practice": STUDY_PY_DIR / "[5] EDA_Advanced" / "EDA_2_Healthcare_Heart_Disease_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "EDA_2_Healthcare_Heart_Disease_Answer.ipynb"
                    },
                    {
                        "key": "eda_adv_3",
                        "title": "3. HR 인사 데이터 결측 분석과 이직 요인 탐색 (HR Employee Churn)",
                        "theory": STUDY_PY_DIR / "[5] EDA_Advanced" / "EDA_3_HR_Employee_Churn.ipynb",
                        "practice": STUDY_PY_DIR / "[5] EDA_Advanced" / "EDA_3_HR_Employee_Churn_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "EDA_3_HR_Employee_Churn_Answer.ipynb"
                    },
                    {
                        "key": "eda_adv_4",
                        "title": "4. 다변량 분석, 교차표와 상관계수 히트맵 (Multivariate Analysis)",
                        "theory": STUDY_PY_DIR / "[5] EDA_Advanced" / "EDA_4_Multivariate_Correlation.ipynb",
                        "practice": STUDY_PY_DIR / "[5] EDA_Advanced" / "EDA_4_Multivariate_Correlation_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "EDA_4_Multivariate_Correlation_Answer.ipynb"
                    }
                ]
            },
            {
                "id": "preprocessing",
                "name": "⚙️ [6] 데이터 전처리 & 파이프라인",
                "units": [
                    {
                        "key": "prep_1",
                        "title": "1. 결측치와 이상치 정제 (Missing & Outliers)",
                        "theory": STUDY_PY_DIR / "[6] Preprocessing" / "Preprocessing_1_Missing_Outliers.ipynb",
                        "practice": STUDY_PY_DIR / "[6] Preprocessing" / "Preprocessing_1_Missing_Outliers_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Preprocessing_1_Missing_Outliers_Answer.ipynb"
                    },
                    {
                        "key": "prep_2",
                        "title": "2. 피처 스케일링과 누수 방지 (Feature Scaling)",
                        "theory": STUDY_PY_DIR / "[6] Preprocessing" / "Preprocessing_2_Feature_Scaling.ipynb",
                        "practice": STUDY_PY_DIR / "[6] Preprocessing" / "Preprocessing_2_Feature_Scaling_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Preprocessing_2_Feature_Scaling_Answer.ipynb"
                    },
                    {
                        "key": "prep_3",
                        "title": "3. 범주형 데이터 인코딩 (Categorical Encoding)",
                        "theory": STUDY_PY_DIR / "[6] Preprocessing" / "Preprocessing_3_Categorical_Encoding.ipynb",
                        "practice": STUDY_PY_DIR / "[6] Preprocessing" / "Preprocessing_3_Categorical_Encoding_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Preprocessing_3_Categorical_Encoding_Answer.ipynb"
                    },
                    {
                        "key": "prep_4",
                        "title": "4. ColumnTransformer와 파이프라인 통합 (Pipeline Integration)",
                        "theory": STUDY_PY_DIR / "[6] Preprocessing" / "Preprocessing_4_Pipeline_Integration.ipynb",
                        "practice": STUDY_PY_DIR / "[6] Preprocessing" / "Preprocessing_4_Pipeline_Integration_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Preprocessing_4_Pipeline_Integration_Answer.ipynb"
                    },
                    {
                        "key": "prep_5",
                        "title": "5. 와인 데이터 탐색과 스케일링",
                        "theory": STUDY_PY_DIR / "[6] Preprocessing" / "Lv2_Python_1117_Data_Pre_processing_wine.ipynb",
                        "practice": STUDY_PY_DIR / "[6] Preprocessing" / "Lv2_Python_1117_Data_Pre_processing_wine_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1117_Data_Pre_processing_wine_Answer.ipynb"
                    },
                    {
                        "key": "prep_6",
                        "title": "6. 신용 데이터 전처리 과제",
                        "theory": STUDY_PY_DIR / "[6] Preprocessing" / "Lv2_Python_1117_Data_Pre_processing_TASK.ipynb",
                        "practice": STUDY_PY_DIR / "[6] Preprocessing" / "Lv2_Python_1117_Data_Pre_processing_TASK_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1117_Data_Pre_processing_TASK_Answer.ipynb"
                    }
                ]
            },
            {
                "id": "machine_learning",
                "name": "🤖 [7] 머신러닝",
                "units": [
                    {
                        "key": "ml_1",
                        "title": "1. 분류와 회귀",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_Classification_Regression.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_Classification_Regression_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1118_Classification_Regression_Answer.ipynb"
                    },
                    {
                        "key": "ml_2",
                        "title": "2. K-최근접 이웃 분류",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_KNN.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_KNN_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1118_KNN_Answer.ipynb"
                    },
                    {
                        "key": "ml_3",
                        "title": "3. 엔트로피와 특성 중요도",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_FeatureSelection_Entropy.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_FeatureSelection_Entropy_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1118_FeatureSelection_Entropy_Answer.ipynb"
                    },
                    {
                        "key": "ml_4",
                        "title": "4. 의사결정나무와 랜덤 포레스트 회귀",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_DecisionTree_regression_house.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_DecisionTree_regression_house_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1118_DecisionTree_regression_house_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[7] Machine_Learning" / "data"
                    },
                    {
                        "key": "ml_5",
                        "title": "5. 단순 선형 회귀와 Diabetes 데이터",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_Regression.diabetes.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_Regression.diabetes_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1119_Regression.diabetes_Answer.ipynb"
                    },
                    {
                        "key": "ml_6",
                        "title": "6. 다중 선형 회귀와 Iris 데이터",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_MultipleRegression.iris.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_MultipleRegression.iris_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1119_MultipleRegression.iris_Answer.ipynb"
                    },
                    {
                        "key": "ml_7",
                        "title": "7. 제곱합 분해와 결정계수",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_SST_SSR_SSE__R2.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_SST_SSR_SSE__R2_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1119_SST_SSR_SSE__R2_Answer.ipynb"
                    },
                    {
                        "key": "ml_8",
                        "title": "8. 신경망 주택 가격 회귀",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_Regression_nn_house_price.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_Regression_nn_house_price_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1119_Regression_nn_house_price_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[7] Machine_Learning" / "data"
                    },
                    {
                        "key": "ml_9",
                        "title": "9. 의사결정나무 분류 기초 (Decision Tree)",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_DecisionTree.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1118_DecisionTree_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1118_DecisionTree_Answer.ipynb"
                    },
                    {
                        "key": "ml_10",
                        "title": "10. 의사결정나무 Study 데이터 실습 (Decision Tree Study)",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_DecisionTree_Study.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_DecisionTree_Study_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1119_DecisionTree_Study_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[7] Machine_Learning" / "data"
                    },
                    {
                        "key": "ml_11",
                        "title": "11. 랜덤 포레스트 분류 (Random Forest)",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_RandomForest.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1119_RandomForest_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1119_RandomForest_Answer.ipynb"
                    },
                    {
                        "key": "ml_12",
                        "title": "12. 특성 변환과 선형 분리 (Squared Features)",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1123_Squared_features_test.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1123_Squared_features_test_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1123_Squared_features_test_Answer.ipynb"
                    },
                    {
                        "key": "ml_13",
                        "title": "13. 서포트 벡터 머신 타이타닉 분류 (SVM Titanic)",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_SVM_Titanic.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_SVM_Titanic_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1124_SVM_Titanic_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[8] Model_Evaluation" / "data"
                    },
                    {
                        "key": "ml_14",
                        "title": "14. K-평균 군집화와 Iris 품종 비교 (K-Means Clustering)",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_clustering_iris.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_clustering_iris_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1124_clustering_iris_Answer.ipynb"
                    },
                    {
                        "key": "ml_15",
                        "title": "15. 엘보우 기법으로 최적 군집 수 찾기 (Elbow Method)",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_clustering_elbow.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_clustering_elbow_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1124_clustering_elbow_Answer.ipynb"
                    },
                    {
                        "key": "ml_16",
                        "title": "16. 실루엣 스코어 군집 평가 (Silhouette Score)",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_clustering_silhouette.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_clustering_silhouette_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1124_clustering_silhouette_Answer.ipynb"
                    },
                    {
                        "key": "ml_17",
                        "title": "17. 장바구니 연관 규칙 분석 (Association Rule & Apriori)",
                        "theory": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_AssociationRule.ipynb",
                        "practice": STUDY_PY_DIR / "[7] Machine_Learning" / "Lv2_Python_1124_AssociationRule_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1124_AssociationRule_Answer.ipynb"
                    }
                ]
            },
            {
                "id": "model_evaluation",
                "name": "📏 [8] 모델 평가 & 로지스틱 회귀",
                "units": [
                    {
                        "key": "eval_1",
                        "title": "1. 혼동 행렬 기초와 시각화 (Confusion Matrix 1)",
                        "theory": STUDY_PY_DIR / "[8] Model_Evaluation" / "Lv2_Python_1120_confusion_matrix_1.ipynb",
                        "practice": STUDY_PY_DIR / "[8] Model_Evaluation" / "Lv2_Python_1120_confusion_matrix_1_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1120_confusion_matrix_1_Answer.ipynb"
                    },
                    {
                        "key": "eval_2",
                        "title": "2. 분류 지표와 클래스 불균형 (Confusion Matrix 2 & F1)",
                        "theory": STUDY_PY_DIR / "[8] Model_Evaluation" / "Lv2_Python_1120_confusion_matrix_2.ipynb",
                        "practice": STUDY_PY_DIR / "[8] Model_Evaluation" / "Lv2_Python_1120_confusion_matrix_2_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1120_confusion_matrix_2_Answer.ipynb"
                    },
                    {
                        "key": "eval_3",
                        "title": "3. 로지스틱 회귀 타이타닉 생존 예측 (Logistic Regression Titanic)",
                        "theory": STUDY_PY_DIR / "[8] Model_Evaluation" / "Lv2_Python_1120_logi_titanic.ipynb",
                        "practice": STUDY_PY_DIR / "[8] Model_Evaluation" / "Lv2_Python_1120_logi_titanic_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1120_logi_titanic_Answer.ipynb",
                        "data_dir": STUDY_PY_DIR / "[8] Model_Evaluation" / "data"
                    },
                    {
                        "key": "eval_4",
                        "title": "4. 로지스틱 회귀 유방암 실습 (Logistic Regression Breast Cancer)",
                        "theory": STUDY_PY_DIR / "[8] Model_Evaluation" / "Lv2_Python_1120_logi_bc_P.ipynb",
                        "practice": STUDY_PY_DIR / "[8] Model_Evaluation" / "Lv2_Python_1120_logi_bc_P_Practice.ipynb",
                        "answer": STUDY_ANS_DIR / "Lv2_Python_1120_logi_bc_P_Answer.ipynb"
                    }
                ]
            }
        ]
    }
}

def get_unit_by_key(unit_key: str) -> Optional[Dict[str, Any]]:
    """유닛 키로 단원 정보 조회"""
    for category in CURRICULUM["python"]["categories"]:
        for unit in category.get("units", []):
            if unit["key"] == unit_key:
                return unit
    return None


def _load_raw_manifest() -> Dict[str, Any]:
    """운영문서/release_manifest.json 로드 (미존재 시 전체 커리큘럼 단일 기본 버전 반환)"""
    if RELEASE_MANIFEST_PATH.exists():
        with open(RELEASE_MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    all_keys = [
        unit["key"]
        for cat in CURRICULUM["python"]["categories"]
        for unit in cat.get("units", [])
    ]
    return {
        "default_version": "latest",
        "versions": [
            {
                "id": "latest",
                "label": "최신 전체 커리큘럼",
                "date": "",
                "description_file": "",
                "summary": "전체 등록 커리큘럼",
                "unit_keys": all_keys,
            }
        ],
    }


def _resolve_version_unit_keys(
    version_id: str,
    version_map: Dict[str, Dict[str, Any]],
    visited: Optional[Set[str]] = None,
) -> List[str]:
    """버전 매니페스트의 extends / added_units / removed_units를 재귀적으로 해석"""
    if visited is None:
        visited = set()
    if version_id in visited or version_id not in version_map:
        return []
    visited.add(version_id)

    entry = version_map[version_id]
    keys: List[str] = []
    parent_id = entry.get("extends")
    if parent_id:
        keys.extend(_resolve_version_unit_keys(parent_id, version_map, visited))

    if "unit_keys" in entry:
        keys = list(entry["unit_keys"])

    for added in entry.get("added_units", []):
        if added not in keys:
            keys.append(added)

    removed = set(entry.get("removed_units", []))
    if removed:
        keys = [k for k in keys if k not in removed]

    return keys


def get_release_versions() -> List[Dict[str, Any]]:
    """확장 가능한 릴리즈 매니페스트 기반 버전 목록과 각 버전의 필터링 통계 반환"""
    manifest = _load_raw_manifest()
    raw_versions = manifest.get("versions", [])
    version_map = {v["id"]: v for v in raw_versions if "id" in v}

    resolved_list: List[Dict[str, Any]] = []
    for entry in raw_versions:
        vid = entry.get("id")
        if not vid:
            continue
        unit_keys = _resolve_version_unit_keys(vid, version_map)
        allowed = set(unit_keys)
        filtered_cats = [
            cat
            for cat in CURRICULUM["python"]["categories"]
            if any(u["key"] in allowed for u in cat.get("units", []))
        ]
        unit_count = sum(
            1
            for cat in filtered_cats
            for u in cat.get("units", [])
            if u["key"] in allowed
        )
        resolved_list.append(
            {
                **entry,
                "resolved_unit_keys": unit_keys,
                "category_count": len(filtered_cats),
                "unit_count": unit_count,
            }
        )
    return resolved_list


def get_default_version_id() -> str:
    """기본 선택 릴리즈 버전 ID 반환"""
    manifest = _load_raw_manifest()
    versions = manifest.get("versions", [])
    default_id = manifest.get("default_version")
    if default_id and any(v.get("id") == default_id for v in versions):
        return default_id
    return versions[-1]["id"] if versions else "latest"


def get_curriculum_by_version(version_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """선택된 릴리즈 버전 매니페스트에 해당하는 대단원·소단원 목록만 필터링하여 반환"""
    all_categories = CURRICULUM["python"]["categories"]
    if not version_id:
        return all_categories

    versions = get_release_versions()
    target = next((v for v in versions if v["id"] == version_id), None)
    if not target:
        return all_categories

    allowed_keys = set(target.get("resolved_unit_keys", []))
    filtered_categories: List[Dict[str, Any]] = []
    for category in all_categories:
        filtered_units = [
            unit for unit in category.get("units", []) if unit["key"] in allowed_keys
        ]
        if filtered_units:
            filtered_categories.append({**category, "units": filtered_units})
    return filtered_categories


def load_version_description(version_id: str) -> Dict[str, Any]:
    """선택된 릴리즈 버전 메타데이터와 운영문서/버전_설명_*.md 요약 본문 반환"""
    versions = get_release_versions()
    target = next((v for v in versions if v["id"] == version_id), None)
    if not target:
        return {
            "id": version_id,
            "label": version_id,
            "date": "",
            "summary": "",
            "markdown": "선택한 버전 정보를 찾을 수 없습니다.",
        }

    desc_rel = target.get("description_file", "")
    markdown = ""
    if desc_rel:
        desc_path = BASE_DIR / desc_rel
        if desc_path.exists():
            markdown = desc_path.read_text(encoding="utf-8")
        else:
            markdown = f"버전 설명 문서를 찾을 수 없습니다: `{desc_rel}`"
    else:
        markdown = target.get("summary", "")

    return {
        **target,
        "markdown": markdown,
    }

def sanitize_markdown(text: str) -> str:
    """
    마크다운 문자열에서 불필요한 Jupyter 특화 안내문구를 정리하고,
    취소선 오류를 유발하는 물결표(~) 범위 표기를 안전한 공백 표기(' ~ ')로 정제합니다.
    """
    if not text:
        return ""
    
    # 1. Jupyter 특화 안내문구 ("셀은 실행 단위입니다...")를 웹 실습 안내로 치환/정리
    jupyter_boilerplate = (
        r"셀은 실행 단위입니다\.\s*Shift\+Enter로 한 셀씩 위에서 아래로 실행합니다\..*?"
        r"\*\*완료할 때는 계산 결과 하나와 그 의미 한 문장을 함께 남기세요\.\*\*"
    )
    web_guidance = (
        "💡 **온라인 실습 가이드:** 본 플랫폼에서는 각 문제별로 제공되는 **[✍️ 2. 연습문제 & 코드 실행기]** "
        "탭에서 코드를 작성하고 실시간으로 실행해 볼 수 있습니다. 실행 결과와 그래프를 즉시 확인하고 모범 답안과 비교해 보세요."
    )
    text = re.sub(jupyter_boilerplate, web_guidance, text, flags=re.DOTALL)
    
    # 2. 설명 전용 자료 문구 정리
    text = text.replace(
        "**설명 전용 자료:** 개념·예제·주의점을 Markdown 셀로 제공합니다. 연습문제와 빈 풀이 셀은 같은 이름의 `_Practice.ipynb`에 있습니다.",
        "**학습 안내:** 핵심 개념과 예제를 학습한 후, 상단 탭에서 실습 문제 풀이와 모범 정답 확인을 진행할 수 있습니다."
    )
    
    # 3. 물결표(~) 범위 표기 정제 (취소선 파싱 방지)
    # 3-1. 백틱 코드쌍: `C01`~`C10` -> `C01` ~ `C10`
    text = re.sub(r'(`[^`]+`)\s*~\s*(`[^`]+`)', r'\1 ~ \2', text)
    # 3-2. 따옴표쌍: 'A'~'E' -> 'A' ~ 'E'
    text = re.sub(r"(['\"][^'\"]+['\"])\s*~\s*(['\"][^'\"]+['\"])", r'\1 ~ \2', text)
    # 3-3. 숫자/단위 범위: 100원~2,000원, 1일~5일, 1~3, 159~171, 2024.01.01~02.05
    text = re.sub(r'([\d.,]+[가-힣]*)\s*~\s*([\d.,]+[가-힣]*)', r'\1 ~ \2', text)
    # 3-4. 영문 식별자: Q1~Q3
    text = re.sub(r'([A-Za-z0-9]+)\s*~\s*([A-Za-z0-9]+)', r'\1 ~ \2', text)
    # 3-5. 한글 범위: 1월~3월
    text = re.sub(r'([가-힣]+)\s*~\s*([가-힣]+)', r'\1 ~ \2', text)
    # 3-6. 대략 표기: ~37 -> 약 37
    text = re.sub(r'(^|[^\w\d`])~(\d+)', r'\1약 \2', text)
    
    return text

def load_cheat_sheet_sections(md_path: Optional[Path]) -> Dict[str, str]:
    """치트시트 마크다운 문서를 9대 주제 및 비교 가이드 섹션별로 분할하여 반환"""
    if not md_path or not md_path.exists():
        return {}
    
    text = md_path.read_text(encoding="utf-8")
    
    section_patterns = [
        ("1. 🐍 Core Python", r'(<span id="sec-1"></span>\s*\n## 1\. 🐍 Core Python.*?(?=<span id="sec-2">|\Z))'),
        ("2. 🔢 NumPy", r'(<span id="sec-2"></span>\s*\n## 2\. 🔢 NumPy.*?(?=<span id="sec-3">|\Z))'),
        ("3. 🐼 Pandas", r'(<span id="sec-3"></span>\s*\n## 3\. 🐼 Pandas.*?(?=<span id="sec-4">|\Z))'),
        ("4. ⚡ Polars", r'(<span id="sec-4"></span>\s*\n## 4\. ⚡ Polars.*?(?=<span id="sec-5">|\Z))'),
        ("5. 🤖 Scikit-Learn", r'(<span id="sec-5"></span>\s*\n## 5\. 🤖 Scikit-Learn.*?(?=<span id="sec-6">|\Z))'),
        ("6. 🔥 PyTorch", r'(<span id="sec-6"></span>\s*\n## 6\. 🔥 PyTorch.*?(?=<span id="sec-7">|\Z))'),
        ("7. 🔶 TensorFlow & Keras", r'(<span id="sec-7"></span>\s*\n## 7\. 🔶 TensorFlow.*?(?=<span id="sec-8">|\Z))'),
        ("8. 📊 Matplotlib", r'(<span id="sec-8"></span>\s*\n## 8\. 📊 Matplotlib.*?(?=<span id="sec-9">|\Z))'),
        ("9. 🌊 Seaborn", r'(<span id="sec-9"></span>\s*\n## 9\. 🌊 Seaborn.*?(?=<span id="sec-10">|\Z))'),
        ("💡 Matplotlib vs Seaborn 비교 가이드", r'(<span id="sec-10"></span>\s*\n## 💡 Matplotlib vs Seaborn.*?\Z)'),
    ]
    
    sections = {"📖 전체 가이드북 한눈에 보기": text}
    for title, pat in section_patterns:
        m = re.search(pat, text, re.DOTALL)
        if m:
            sections[title] = m.group(1).strip()
            
    return sections

def load_theory_content(unit_info: Dict[str, Any]) -> str:
    """이론 노트북의 내용을 읽어 Markdown 문자열로 변환"""
    if unit_info.get("type") == "html_md":
        md_path = unit_info.get("md_path")
        if md_path and md_path.exists():
            return sanitize_markdown(md_path.read_text(encoding="utf-8"))
        return "치트시트 문서를 불러올 수 없습니다."
    
    theory_path = unit_info.get("theory")
    if not theory_path or not theory_path.exists():
        return "이론 설명 노트북이 존재하지 않습니다."
    
    with open(theory_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    md_parts = []
    for cell in nb.get("cells", []):
        cell_type = cell.get("cell_type")
        source = cell.get("source", "")
        text = "".join(source) if isinstance(source, list) else source
        
        if cell_type == "markdown":
            cleaned = sanitize_markdown(text)
            if cleaned.strip():
                md_parts.append(cleaned)
        elif cell_type == "code":
            if text.strip():
                md_parts.append(f"```python\n{text}\n```")
                
    return "\n\n".join(md_parts)

def load_practice_and_answers(unit_info: Dict[str, Any]) -> Dict[str, Any]:
    """실습 문제와 정답을 파싱하여 반환"""
    practice_path = unit_info.get("practice")
    answer_path = unit_info.get("answer")
    
    if not practice_path or not practice_path.exists():
        return {"setup_code": "", "questions": []}
    
    with open(practice_path, "r", encoding="utf-8") as f:
        p_nb = json.load(f)
        
    a_nb = {}
    if answer_path and answer_path.exists():
        with open(answer_path, "r", encoding="utf-8") as f:
            a_nb = json.load(f)
            
    p_cells = p_nb.get("cells", [])
    a_cells = a_nb.get("cells", [])
    
    # 1. Setup 코드 추출 (첫 문제 전까지의 코드 셀들)
    setup_lines = []
    first_q_idx = len(p_cells)
    for i, c in enumerate(p_cells):
        src = "".join(c.get("source", ""))
        if c.get("cell_type") == "markdown" and ("## 문제" in src or "### 문제" in src):
            first_q_idx = i
            break
        if c.get("cell_type") == "code":
            code = src.strip()
            if code and not code.startswith("%pip"):
                setup_lines.append(code)
                
    setup_code = "\n\n".join(setup_lines)
    
    # 2. 문제 및 정답 추출
    questions = []
    for i in range(first_q_idx, len(p_cells)):
        c = p_cells[i]
        src = "".join(c.get("source", ""))
        
        if c.get("cell_type") == "markdown" and ("## 문제" in src or "### 문제" in src):
            # 문제 제목 추출
            title_lines = [l.strip().lstrip("#").strip() for l in src.split("\n") if "문제" in l]
            title = title_lines[0] if title_lines else f"문제 {len(questions)+1}"
            
            # 실습 시작 코드 (다음 코드 셀)
            starter_code = ""
            if i + 1 < len(p_cells) and p_cells[i+1].get("cell_type") == "code":
                starter_code = "".join(p_cells[i+1].get("source", ""))
                
            # 정답지에서 매칭되는 코드 및 해석 추출
            solution_code = ""
            interpretation = ""
            if i + 1 < len(a_cells) and a_cells[i+1].get("cell_type") == "code":
                solution_code = "".join(a_cells[i+1].get("source", ""))
            if i + 2 < len(a_cells) and a_cells[i+2].get("cell_type") == "markdown":
                interpretation = "".join(a_cells[i+2].get("source", ""))
                
            questions.append({
                "id": len(questions) + 1,
                "title": title,
                "description": sanitize_markdown(src),
                "starter_code": starter_code,
                "solution_code": solution_code,
                "interpretation": sanitize_markdown(interpretation)
            })
            
    return {
        "setup_code": setup_code,
        "questions": questions,
        "data_dir": str(unit_info.get("data_dir", ""))
    }
