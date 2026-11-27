"""
modules/quiz_bank/__init__.py
10개 챕터별 퀴즈 모듈(총 750문항)을 통합하여 QUIZ_BANK를 제공합니다.
"""

from typing import Any, Dict, List

from .eda_advanced import QUESTIONS as EDA_ADVANCED_QUESTIONS
from .machine_learning import QUESTIONS as MACHINE_LEARNING_QUESTIONS
from .model_evaluation import QUESTIONS as MODEL_EVALUATION_QUESTIONS
from .numpy import QUESTIONS as NUMPY_QUESTIONS
from .pandas import QUESTIONS as PANDAS_QUESTIONS
from .preprocessing import QUESTIONS as PREPROCESSING_QUESTIONS
from .python_basics import QUESTIONS as PYTHON_BASICS_QUESTIONS
from .sql import QUESTIONS as SQL_QUESTIONS
from .statistics import QUESTIONS as STATISTICS_QUESTIONS
from .visualization import QUESTIONS as VISUALIZATION_QUESTIONS

QUIZ_BANK: List[Dict[str, Any]] = [
    *PYTHON_BASICS_QUESTIONS,
    *NUMPY_QUESTIONS,
    *PANDAS_QUESTIONS,
    *VISUALIZATION_QUESTIONS,
    *STATISTICS_QUESTIONS,
    *EDA_ADVANCED_QUESTIONS,
    *PREPROCESSING_QUESTIONS,
    *MACHINE_LEARNING_QUESTIONS,
    *MODEL_EVALUATION_QUESTIONS,
    *SQL_QUESTIONS,
]

__all__ = ["QUIZ_BANK"]
