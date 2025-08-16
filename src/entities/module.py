from enum import Enum, auto
from typing import List, Optional
from .exam import Exam, ExamStatus

class ModuleStatus(Enum):
    """Status of a course module."""
    PLANNED = auto()
    IN_PROGRESS = auto()
    PASSED = auto()
    FAILED = auto()

class CourseModule:
    """Represents a single course module within a degree program."""
    
    def __init__(self, name: str, credits: int, planned_semester: int):
        self.name = name
        self.credits = credits
        self.planned_semester = planned_semester
        self.exams: List[Exam] = []

    def add_exam(self, exam: Exam):
        self.exams.append(exam)
    
    @property
    def status(self) -> ModuleStatus:
        """Calculates the module status dynamically based on its exams."""
        if any(exam.status == ExamStatus.PASSED for exam in self.exams):
            return ModuleStatus.PASSED
        if self.exams and all(exam.status == ExamStatus.FAILED for exam in self.exams):
            return ModuleStatus.FAILED
        if self.exams:
            return ModuleStatus.IN_PROGRESS
        return ModuleStatus.PLANNED

    def is_passed(self) -> bool:
        return self.status == ModuleStatus.PASSED
    
    def best_grade(self) -> Optional[float]:
        passed_grades = [exam.grade for exam in self.exams 
                         if exam.status == ExamStatus.PASSED and exam.grade is not None]
        return min(passed_grades) if passed_grades else None
    
    def to_dict(self):
        """Converts the module object to a dictionary."""
        return {
            '__class__': 'CourseModule',
            'name': self.name,
            'credits': self.credits,
            'planned_semester': self.planned_semester,
            'exams': [exam.to_dict() for exam in self.exams]
        }