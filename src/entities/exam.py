"""
Defines the data model for exams, including their types, statuses,
and an inheritance structure for different examination forms.
"""
from enum import Enum, auto
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

class StateError(Exception):
    """Custom exception for invalid state transitions."""
    pass

class ExamStatus(Enum):
    """Enumeration for the lifecycle states of an exam."""
    PLANNED = auto()
    PASSED = auto()
    FAILED = auto()

class ExamType(Enum):
    """Enumeration for the different types of examinations."""
    WRITTEN = "Written Exam"
    PORTFOLIO = "Portfolio"
    CASE_STUDY = "Case Study"
    ORAL = "Oral Exam"

class Exam(ABC):
    """Abstract base class for all examination performances."""
    def __init__(self, exam_type: ExamType, exam_date: date):
        self.exam_type = exam_type
        self.exam_date = exam_date
        self.grade: Optional[float] = None
        self.status: ExamStatus = ExamStatus.PLANNED
    
    def record_result(self, grade: float):
        # Validate grade range (assuming 1.0 is best, 5.0 is worst, adjust as needed)
        if not (1.0 <= grade <= 5.0):
            raise ValueError("Note muss zwischen 1.0 (beste) und 5.0 (schlechteste) liegen.")
        self.grade = grade
        self.status = ExamStatus.PASSED if self.is_passed() else ExamStatus.FAILED
    
    @abstractmethod
    def is_passed(self) -> bool:
        pass

    def to_dict(self):
        return {
            '__class__': self.__class__.__name__,
            'exam_type': self.exam_type.name,
            'exam_date': self.exam_date.isoformat(),
            'grade': self.grade,
            'status': self.status.name
        }

class WrittenExam(Exam):
    def __init__(self, exam_date: date):
        super().__init__(ExamType.WRITTEN, exam_date)
    def is_passed(self) -> bool:
        if self.grade is None:
            raise StateError("Cannot check pass status before a grade is recorded.")
        return self.grade <= 4.0

class Portfolio(Exam):
    def __init__(self, exam_date: date):
        super().__init__(ExamType.PORTFOLIO, exam_date)
    def is_passed(self) -> bool:
        if self.grade is None:
            raise StateError("Cannot check pass status before a grade is recorded.")
        return self.grade <= 4.0

class CaseStudyExam(Exam):
    def __init__(self, exam_date: date):
        super().__init__(ExamType.CASE_STUDY, exam_date)
    def is_passed(self) -> bool:
        if self.grade is None:
            raise StateError("Cannot check pass status before a grade is recorded.")
        return self.grade <= 4.0

class OralExam(Exam):
    def __init__(self, exam_date: date):
        super().__init__(ExamType.ORAL, exam_date)
    def is_passed(self) -> bool:
        if self.grade is None:
            raise StateError("Cannot check pass status before a grade is recorded.")
        return self.grade <= 4.0
