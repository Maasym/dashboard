"""
Defines the data model for exams, including their types, statuses,
and an inheritance structure for different examination forms.
"""
from enum import Enum, auto
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

class ExamStatus(Enum):
    """Enumeration for the lifecycle states of an exam."""
    PASSED = auto()
    OPEN = auto()
    RETRY = auto()

class ExamType(Enum):
    """Enumeration for the different types of examinations."""
    WRITTEN = "Written Exam"
    PORTFOLIO = "Portfolio"
    ORAL = "Oral Exam"

class Exam(ABC):
    """
    Abstract base class for all examination performances.
    
    This class defines the common interface and attributes for all concrete exam types.
    It manages the state of an exam from its creation (OPEN) to its completion.
    """
    def __init__(self, exam_type: ExamType, exam_date: date):
        """
        Initializes an exam instance in an OPEN state.

        Args:
            exam_type (ExamType): The type of the examination.
            exam_date (date): The date of the examination.
        """
        self.exam_type = exam_type
        self.exam_date = exam_date
        self.grade: Optional[float] = None
        self.status: ExamStatus = ExamStatus.OPEN
    
    def record_result(self, grade: float):
        """
        Records the result of the exam and updates its status.

        Args:
            grade (float): The grade received, typically between 1.0 and 5.0.
        
        Raises:
            ValueError: If the provided grade is outside the valid range.
        """
        if not 1.0 <= grade <= 5.0:
            raise ValueError("Grade must be between 1.0 and 5.0")
            
        self.grade = grade
        self.status = ExamStatus.PASSED if self.is_passed() else ExamStatus.RETRY
    
    @abstractmethod
    def is_passed(self) -> bool:
        """
        Abstract method to determine if the exam was passed.
        
        This method must be implemented by all concrete subclasses.

        Returns:
            bool: True if the exam was passed, False otherwise.
        """
        pass

class WrittenExam(Exam):
    """Represents a concrete written examination."""
    def __init__(self, exam_date: date, duration_minutes: int):
        """
        Initializes a written exam.

        Args:
            exam_date (date): The date of the exam.
            duration_minutes (int): The duration of the exam in minutes.
        """
        super().__init__(ExamType.WRITTEN, exam_date)
        self.duration_minutes = duration_minutes
    
    def is_passed(self) -> bool:
        """
        Checks if the written exam is passed (grade <= 4.0).

        Raises:
            RuntimeError: If the grade has not been recorded yet.
        
        Returns:
            bool: True if passed, False otherwise.
        """
        if self.grade is None:
            raise RuntimeError("Cannot check pass status before a result is recorded.")
        return self.grade <= 4.0

class Portfolio(Exam):
    """Represents a concrete portfolio assessment."""
    def __init__(self, exam_date: date, submission_topics: List[str]):
        """
        Initializes a portfolio.

        Args:
            exam_date (date): The date of the final submission.
            submission_topics (List[str]): A list of submitted topics.
        """
        super().__init__(ExamType.PORTFOLIO, exam_date)
        self.submission_topics = submission_topics
    
    def is_passed(self) -> bool:
        """
        Checks if the portfolio is passed (grade <= 4.0 and at least 3 topics).

        Raises:
            RuntimeError: If the grade has not been recorded yet.

        Returns:
            bool: True if passed, False otherwise.
        """
        if self.grade is None:
            raise RuntimeError("Cannot check pass status before a result is recorded.")
        return self.grade <= 4.0 and len(self.submission_topics) >= 3