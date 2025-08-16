from enum import Enum, auto
from typing import List, Optional
from .exam import Exam, ExamStatus

MAX_ATTEMPTS = 3  # Maximum allowed attempts per module

class StateError(Exception):
    """Custom exception for invalid state transitions."""
    pass

class ModuleStatus(Enum):
    """Status of a course module."""
    PLANNED = auto()
    IN_PROGRESS = auto()
    PASSED = auto()
    FAILED = auto()
    NO_MORE_ATTEMPTS = auto()  # New status for exhausted attempts

class CourseModule:
    """Represents a single course module within a degree program."""
    
    def __init__(self, name: str, credits: int, planned_semester: int):
        self.name = name
        self.credits = credits
        self.planned_semester = planned_semester
        self.exams: List[Exam] = []

    def add_exam(self, exam: Exam):
        """Adds an exam if attempts remain"""
        if self.status == ModuleStatus.NO_MORE_ATTEMPTS:
            raise StateError(f"Maximale Versuche ({MAX_ATTEMPTS}) für Modul '{self.name}' erreicht")
        self.exams.append(exam)
    
    @property
    def status(self) -> ModuleStatus:
        """Calculates the module status dynamically based on its exams."""
        # Check if passed
        if any(exam.status == ExamStatus.PASSED for exam in self.exams):
            return ModuleStatus.PASSED
        
        # Check if attempts exhausted
        if len(self.exams) >= MAX_ATTEMPTS:
            return ModuleStatus.NO_MORE_ATTEMPTS
        
        # Check if failed but can retry
        if self.exams and all(exam.status == ExamStatus.FAILED for exam in self.exams):
            return ModuleStatus.FAILED
        
        # Default statuses
        if self.exams:
            return ModuleStatus.IN_PROGRESS
        return ModuleStatus.PLANNED

    def is_passed(self) -> bool:
        return self.status == ModuleStatus.PASSED
    
    def best_grade(self) -> Optional[float]:
        passed_grades = [exam.grade for exam in self.exams 
                         if exam.status == ExamStatus.PASSED and exam.grade is not None]
        return min(passed_grades) if passed_grades else None
    
    def remaining_attempts(self) -> int:
        """Returns number of remaining exam attempts"""
        return max(0, MAX_ATTEMPTS - len(self.exams))
    
    def to_dict(self):
        """Converts the module object to a dictionary."""
        return {
            '__class__': 'CourseModule',
            'name': self.name,
            'credits': self.credits,
            'planned_semester': self.planned_semester,
            'exams': [exam.to_dict() for exam in self.exams]
        }