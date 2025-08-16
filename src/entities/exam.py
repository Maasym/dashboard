from enum import Enum, auto
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

class ExamStatus(Enum):
    """Represents the lifecycle states of an exam."""
    PLANNED = auto()     # Exam is scheduled but not taken
    PASSED = auto()      # Exam passed successfully
    FAILED = auto()      # Exam failed

class ExamType(Enum):
    """Types of examinations as defined in requirements."""
    WRITTEN = "Written Exam"
    PORTFOLIO = "Portfolio"
    ORAL = "Oral Exam"

class Exam(ABC):
    """Abstract base class for all examination performances."""
    
    def __init__(self, exam_type: ExamType, exam_date: date):
        """
        Initialize an exam instance in planned state.
        
        Args:
            exam_type: Type of examination
            exam_date: Date of the examination
        """
        self.exam_type = exam_type
        self.exam_date = exam_date
        self.grade: Optional[float] = None
        self.status: ExamStatus = ExamStatus.PLANNED
    
    def record_result(self, grade: float):
        """
        Records exam result and updates status.
        
        Args:
            grade: Exam grade between 1.0-5.0
            
        Raises:
            ValueError: If grade is outside valid range
        """
        if not 1.0 <= grade <= 5.0:
            raise ValueError("Grade must be between 1.0 and 5.0")
            
        self.grade = grade
        self.status = ExamStatus.PASSED if self.is_passed() else ExamStatus.FAILED
    
    @abstractmethod
    def is_passed(self) -> bool:
        """
        Abstract method to determine if the exam was passed.
        Should only be called after recording results.
        """
        pass

class WrittenExam(Exam):
    """Represents a written examination."""
    
    def __init__(self, exam_date: date, duration_minutes: int):
        super().__init__(ExamType.WRITTEN, exam_date)
        self.duration_minutes = duration_minutes
    
    def is_passed(self) -> bool:
        """Passed if grade <= 4.0 and result recorded."""
        if self.grade is None:
            raise StateError("Result not recorded yet")
        return self.grade <= 4.0

class Portfolio(Exam):
    """Represents a portfolio assessment."""
    
    def __init__(self, exam_date: date, submission_topics: List[str]):
        super().__init__(ExamType.PORTFOLIO, exam_date)
        self.submission_topics = submission_topics
    
    def is_passed(self) -> bool:
        """Passed if grade <= 4.0 and min. 3 topics submitted."""
        if self.grade is None:
            raise StateError("Result not recorded yet")
        return self.grade <= 4.0 and len(self.submission_topics) >= 3

class StateError(Exception):
    """Custom exception for invalid state transitions."""
    pass