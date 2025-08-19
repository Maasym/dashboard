"""
Defines the data model for course modules, including their status tracking,
exam management, and attempt limitations within a degree program.
"""
from enum import Enum, auto
from typing import List, Optional
from .exam import Exam, ExamStatus

# Maximum number of exam attempts allowed per module before permanent failure
MAX_ATTEMPTS = 3

class StateError(Exception):
    """
    Custom exception raised when attempting invalid state transitions.
    
    Used primarily when trying to add exams to modules that have already
    exhausted their maximum allowed attempts.
    """
    pass

class ModuleStatus(Enum):
    """
    Enumeration representing the lifecycle status of a course module.
    
    The status is dynamically calculated based on the module's exam history:
    - PLANNED: No exams have been scheduled or taken yet
    - IN_PROGRESS: Has exams but none are conclusively passed or failed
    - PASSED: At least one exam has been successfully passed
    - FAILED: All exams failed but retries are still possible
    - NO_MORE_ATTEMPTS: Maximum attempts reached without passing (terminal state)
    """
    PLANNED = auto()           # Module scheduled but no exams yet
    IN_PROGRESS = auto()       # Exams exist but outcome uncertain
    PASSED = auto()           # Successfully completed with passing grade
    FAILED = auto()           # Failed but can still retry
    NO_MORE_ATTEMPTS = auto()  # Permanently failed - no more attempts allowed

class CourseModule:
    """
    Represents a single course module within a degree program.
    
    A module encapsulates all information about a specific course, including
    its metadata (name, credits, planned semester) and exam history. The module
    tracks multiple exam attempts and dynamically calculates its status.
    """
    
    def __init__(self, name: str, credits: int, planned_semester: int):
        """
        Initialize a new course module with validation.
        
        Args:
            name: The name/title of the module (cannot be empty)
            credits: ECTS credit points for this module (must be positive)
            planned_semester: The semester this module is planned for (1-indexed)
            
        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate module name is not empty or whitespace-only
        if not name or not name.strip():
            raise ValueError("Modulname darf nicht leer sein.")
        # Ensure credit points are positive (ECTS system requirement)
        if credits <= 0:
            raise ValueError("ECTS-Punkte müssen positiv sein.")
        # Validate semester is a positive number (1-indexed)
        if planned_semester <= 0:
            raise ValueError("Semester muss positiv sein.")
            
        self.name = name
        self.credits = credits
        self.planned_semester = planned_semester
        # Initialize empty list to track all exam attempts for this module
        self.exams: List[Exam] = []

    def add_exam(self, exam: Exam):
        """
        Add an exam attempt to this module if attempts remain.
        
        Args:
            exam: The Exam object representing this attempt
            
        Raises:
            StateError: If the module has already exhausted all allowed attempts
        """
        # Prevent adding exams if maximum attempts already reached
        if self.status == ModuleStatus.NO_MORE_ATTEMPTS:
            raise StateError(f"Maximale Versuche ({MAX_ATTEMPTS}) für Modul '{self.name}' erreicht")
        self.exams.append(exam)
    
    @property
    def status(self) -> ModuleStatus:
        """
        Calculate the module status dynamically based on its exam history.
        
        The status is determined by the current state of all exams associated
        with this module, following a priority order:
        1. PASSED: If any exam is passed
        2. NO_MORE_ATTEMPTS: If max attempts reached without passing
        3. FAILED: If all current exams failed but retries possible
        4. IN_PROGRESS: If exams exist but results are pending/mixed
        5. PLANNED: If no exams have been added yet
        
        Returns:
            ModuleStatus: The current status of this module
        """
        # Priority 1: Check if any exam has been successfully passed
        if any(exam.status == ExamStatus.PASSED for exam in self.exams):
            return ModuleStatus.PASSED
        
        # Priority 2: Check if maximum attempts reached without passing
        if len(self.exams) >= MAX_ATTEMPTS:
            return ModuleStatus.NO_MORE_ATTEMPTS
        
        # Priority 3: Check if all existing exams failed but retries are possible
        if self.exams and all(exam.status == ExamStatus.FAILED for exam in self.exams):
            return ModuleStatus.FAILED
        
        # Priority 4: Exams exist but status is mixed or pending
        if self.exams:
            return ModuleStatus.IN_PROGRESS
            
        # Priority 5: No exams scheduled yet
        return ModuleStatus.PLANNED

    def is_passed(self) -> bool:
        """
        Check if this module has been successfully completed.
        
        Returns:
            bool: True if the module status is PASSED, False otherwise
        """
        return self.status == ModuleStatus.PASSED
    
    def best_grade(self) -> Optional[float]:
        """
        Get the best (lowest) grade from all passed exams for this module.
        
        In the German grading system, lower numbers represent better grades
        (1.0 is the best, 5.0 is the worst). This method returns the minimum
        value among all passed exam grades.
        
        Returns:
            Optional[float]: The best grade achieved, or None if no exams passed
        """
        # Collect all grades from successfully passed exams
        passed_grades = [exam.grade for exam in self.exams 
                         if exam.status == ExamStatus.PASSED and exam.grade is not None]
        # Return the minimum (best) grade, or None if no passed exams exist
        return min(passed_grades) if passed_grades else None
    
    def remaining_attempts(self) -> int:
        """
        Calculate the number of exam attempts remaining for this module.
        
        Each module allows a maximum number of attempts (defined by MAX_ATTEMPTS).
        This method calculates how many attempts are left based on exams already taken.
        
        Returns:
            int: Number of attempts remaining (0 if maximum reached)
        """
        return max(0, MAX_ATTEMPTS - len(self.exams))
    
    def to_dict(self):
        """
        Serialize the module to a dictionary for storage or export.
        
        Creates a dictionary representation of the module including all
        its exams. The '__class__' field enables proper deserialization.
        
        Returns:
            dict: Dictionary representation suitable for JSON serialization
        """
        return {
            '__class__': 'CourseModule',  # Enable type identification for deserialization
            'name': self.name,
            'credits': self.credits,
            'planned_semester': self.planned_semester,
            'exams': [exam.to_dict() for exam in self.exams]
        }