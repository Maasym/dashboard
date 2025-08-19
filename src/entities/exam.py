"""
Defines the data model for exams, including their types, statuses,
and an inheritance structure for different examination forms.
"""
from enum import Enum, auto
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List

class StateError(Exception):
    """
    Custom exception raised when attempting invalid state operations.
    
    Primarily used when trying to check the pass status of an exam
    before a grade has been recorded, preventing undefined behavior.
    """
    pass

class ExamStatus(Enum):
    """
    Enumeration representing the lifecycle states of an exam attempt.
    
    - PLANNED: Exam is scheduled but has not been taken yet
    - PASSED: Exam was taken and achieved a passing grade
    - FAILED: Exam was taken but did not achieve a passing grade
    """
    PLANNED = auto()  # Scheduled but not yet taken
    PASSED = auto()   # Successfully completed with passing grade
    FAILED = auto()   # Completed but did not meet passing criteria

class ExamType(Enum):
    """
    Enumeration for the different types of examinations available.
    
    Each type represents a different format of academic assessment,
    each with their own characteristics and evaluation methods.
    """
    WRITTEN = "Written Exam"    # Traditional written examination
    PORTFOLIO = "Portfolio"     # Collection of work samples/projects
    CASE_STUDY = "Case Study"   # Analysis of real-world scenarios
    ORAL = "Oral Exam"         # Verbal examination with examiner

class Exam(ABC):
    """
    Abstract base class for all examination performances.
    
    This class provides the common structure and behavior for all types
    of exams, including grade recording and status management. Concrete
    exam types inherit from this class and implement specific passing criteria.
    """
    
    def __init__(self, exam_type: ExamType, exam_date: date):
        """
        Initialize a new exam with type and date.
        
        Args:
            exam_type: The type of examination (written, oral, etc.)
            exam_date: The scheduled date for this exam
        """
        self.exam_type = exam_type
        self.exam_date = exam_date
        # Grade will be set when exam results are recorded
        self.grade: Optional[float] = None
        # All exams start as planned until results are recorded
        self.status: ExamStatus = ExamStatus.PLANNED
    
    def record_result(self, grade: float):
        """
        Record the grade result for this exam and update its status.
        
        Args:
            grade: The grade achieved (1.0-5.0 in German system, 1.0 being best)
            
        Raises:
            ValueError: If the grade is outside the valid range
        """
        # Validate grade is within German grading system range
        if not (1.0 <= grade <= 5.0):
            raise ValueError("Note muss zwischen 1.0 (beste) und 5.0 (schlechteste) liegen.")
        
        self.grade = grade
        # Update status based on whether this grade meets passing criteria
        self.status = ExamStatus.PASSED if self.is_passed() else ExamStatus.FAILED
    
    @abstractmethod
    def is_passed(self) -> bool:
        """
        Determine if this exam meets the passing criteria.
        
        This abstract method must be implemented by each concrete exam type
        to define their specific passing requirements.
        
        Returns:
            bool: True if the exam grade meets passing criteria, False otherwise
            
        Raises:
            StateError: If called before a grade has been recorded
        """
        pass

    def to_dict(self):
        """
        Serialize the exam to a dictionary for storage or export.
        
        Creates a dictionary representation of the exam including its type,
        date, grade, and status. The '__class__' field enables proper deserialization.
        
        Returns:
            dict: Dictionary representation suitable for JSON serialization
        """
        return {
            '__class__': self.__class__.__name__,  # Enable type identification for deserialization
            'exam_type': self.exam_type.name,
            'exam_date': self.exam_date.isoformat(),
            'grade': self.grade,
            'status': self.status.name
        }

class WrittenExam(Exam):
    """
    Concrete implementation of a written examination.
    
    Written exams are traditional paper-based or computer-based examinations
    with a passing grade threshold of 4.0 or better.
    """
    
    def __init__(self, exam_date: date):
        """
        Initialize a written exam for the specified date.
        
        Args:
            exam_date: The scheduled date for this written exam
        """
        super().__init__(ExamType.WRITTEN, exam_date)
    
    def is_passed(self) -> bool:
        """
        Check if this written exam meets the passing criteria.
        
        Written exams require a grade of 4.0 or better to pass.
        
        Returns:
            bool: True if grade <= 4.0, False otherwise
            
        Raises:
            StateError: If called before a grade has been recorded
        """
        if self.grade is None:
            raise StateError("Cannot check pass status before a grade is recorded.")
        return self.grade <= 4.0

class Portfolio(Exam):
    """
    Concrete implementation of a portfolio examination.
    
    Portfolio exams involve submitting a collection of work samples,
    projects, or assignments with a passing grade threshold of 4.0 or better.
    """
    
    def __init__(self, exam_date: date):
        """
        Initialize a portfolio exam for the specified date.
        
        Args:
            exam_date: The submission deadline for this portfolio
        """
        super().__init__(ExamType.PORTFOLIO, exam_date)
    
    def is_passed(self) -> bool:
        """
        Check if this portfolio meets the passing criteria.
        
        Portfolio exams require a grade of 4.0 or better to pass.
        
        Returns:
            bool: True if grade <= 4.0, False otherwise
            
        Raises:
            StateError: If called before a grade has been recorded
        """
        if self.grade is None:
            raise StateError("Cannot check pass status before a grade is recorded.")
        return self.grade <= 4.0

class CaseStudyExam(Exam):
    """
    Concrete implementation of a case study examination.
    
    Case study exams involve analyzing real-world scenarios and providing
    solutions or recommendations with a passing grade threshold of 4.0 or better.
    """
    
    def __init__(self, exam_date: date):
        """
        Initialize a case study exam for the specified date.
        
        Args:
            exam_date: The scheduled date for this case study exam
        """
        super().__init__(ExamType.CASE_STUDY, exam_date)
    
    def is_passed(self) -> bool:
        """
        Check if this case study meets the passing criteria.
        
        Case study exams require a grade of 4.0 or better to pass.
        
        Returns:
            bool: True if grade <= 4.0, False otherwise
            
        Raises:
            StateError: If called before a grade has been recorded
        """
        if self.grade is None:
            raise StateError("Cannot check pass status before a grade is recorded.")
        return self.grade <= 4.0

class OralExam(Exam):
    """
    Concrete implementation of an oral examination.
    
    Oral exams involve verbal questioning and discussion with an examiner,
    testing knowledge through spoken interaction with a passing grade threshold of 4.0 or better.
    """
    
    def __init__(self, exam_date: date):
        """
        Initialize an oral exam for the specified date.
        
        Args:
            exam_date: The scheduled date for this oral exam
        """
        super().__init__(ExamType.ORAL, exam_date)
    
    def is_passed(self) -> bool:
        """
        Check if this oral exam meets the passing criteria.
        
        Oral exams require a grade of 4.0 or better to pass.
        
        Returns:
            bool: True if grade <= 4.0, False otherwise
            
        Raises:
            StateError: If called before a grade has been recorded
        """
        if self.grade is None:
            raise StateError("Cannot check pass status before a grade is recorded.")
        return self.grade <= 4.0
