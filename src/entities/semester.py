"""
Defines the data model for an academic semester, which groups a collection of modules.
"""
from typing import List
from .module import CourseModule, ModuleStatus

class AcademicSemester:
    """
    Represents a single academic semester containing multiple course modules.
    """
    def __init__(self, number: int):
        """
        Initializes a semester.

        Args:
            number (int): The number of the semester (e.g., 1, 2, ...).
        """
        self.number = number
        self.modules: List[CourseModule] = []
    
    def add_module(self, module: CourseModule):
        """
        Adds a course module to this semester's schedule.

        Args:
            module (CourseModule): The module object to add.
        """
        self.modules.append(module)
    
    def earned_credits(self) -> int:
        """
        Calculates the total ECTS credits earned from passed modules in this semester.

        Returns:
            int: The sum of credits from all passed modules.
        """
        # Sums the credits of modules that are in the PASSED state.
        return sum(
            module.credits 
            for module in self.modules 
            if module.status == ModuleStatus.PASSED
        )
    
    def total_possible_credits(self) -> int:
        """
        Calculates the total possible ECTS credits from all modules in this semester.

        Returns:
            int: The sum of credits from all modules.
        """
        return sum(module.credits for module in self.modules)
    
    def progress_percentage(self) -> float:
        """
        Calculates the completion progress of the semester in percent.

        Returns:
            float: The progress from 0.0 to 100.0.
        """
        if not self.modules:
            return 0.0
            
        total = self.total_possible_credits()
        achieved = self.earned_credits()
        # Avoid division by zero if a semester has modules with 0 credits.
        return (achieved / total) * 100 if total > 0 else 0.0
    
    def __str__(self) -> str:
        """Provides a user-friendly string representation of the semester."""
        return f"Semester {self.number}: {self.earned_credits()}/{self.total_possible_credits()} ECTS"