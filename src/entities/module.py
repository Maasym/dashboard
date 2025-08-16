"""
Defines the data model for a course module, which manages a collection of exams.
"""
from enum import Enum, auto
from typing import List, Optional
from .exam import Exam, ExamStatus

class ModuleStatus(Enum):
    """Enumeration for the lifecycle states of a course module."""
    PASSED = auto()
    OPEN = auto()
    RETRY = auto()

class CourseModule:
    """
    Represents a single course module within a degree program.
    
    A module contains one or more exams and its status is derived
    from the statuses of its exams.
    """
    def __init__(self, name: str, credits: int):
        """
        Initializes a course module.

        Args:
            name (str): The name of the module.
            credits (int): The number of ECTS credits for this module.
        """
        self.name = name
        self.credits = credits
        self.exams: List[Exam] = []
    
    def add_exam(self, exam: Exam):
        """
        Adds an exam attempt to this module.

        Args:
            exam (Exam): The exam object to be added.
        """
        self.exams.append(exam)
    
    @property
    def status(self) -> ModuleStatus:
        """
        Calculates the module status dynamically based on its exams.
        The status is a property, so it's always up-to-date.

        Returns:
            ModuleStatus: The current calculated status of the module.
        """
        if any(exam.status == ExamStatus.PASSED for exam in self.exams):
            return ModuleStatus.PASSED
        
        # If there are exams and all of them are graded (not open) but none are passed
        if self.exams and all(exam.status != ExamStatus.OPEN for exam in self.exams):
            return ModuleStatus.RETRY
            
        # If there are any exams (which must be OPEN at this point)
        return ModuleStatus.OPEN

    def is_passed(self) -> bool:
        """
        A convenience method to check if the module's current status is PASSED.

        Returns:
            bool: True if the module is passed, False otherwise.
        """
        return self.status == ModuleStatus.PASSED
    
    def best_exam_grade(self) -> Optional[float]:
        """
        Finds the best grade from all passed exam attempts for this module.

        Returns:
            Optional[float]: The best grade (lowest number) or None if no exam was passed.
        """
        passed_grades = [exam.grade for exam in self.exams 
                         if exam.status == ExamStatus.PASSED and exam.grade is not None]
        return min(passed_grades) if passed_grades else None
    
    def to_dict(self):
        """Converts the module object to a dictionary."""
        return {
            '__class__': 'CourseModule',
            'name': self.name,
            'credits': self.credits,
            'exams': [exam.to_dict() for exam in self.exams]
        }
    
    def __str__(self) -> str:
        """Provides a user-friendly string representation of the module."""
        return f"{self.name} ({self.credits} ECTS) - {self.status.name}"