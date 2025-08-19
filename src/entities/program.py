"""
Defines the main data model for the degree program, which acts as the root
container for all academic data.
"""
from typing import List, Optional
from .semester import Semester
from .module import CourseModule, ModuleStatus

class DegreeProgram:
    """Represents the entire degree program, holding all semesters and modules."""
    
    def __init__(self, name: str, target_semesters: int, target_grade: float):
        """
        Initialize a new degree program with validation.
        
        Args:
            name: The name of the degree program (cannot be empty)
            target_semesters: Number of planned semesters to complete (must be positive)
            target_grade: Target average grade to achieve (1.0-5.0, where 1.0 is best)
        
        Raises:
            ValueError: If any parameter is invalid
        """
        # Validate program name is not empty or whitespace only
        if not name or not name.strip():
            raise ValueError("Studiengangsname darf nicht leer sein.")
        # Ensure target semester count is realistic
        if target_semesters <= 0:
            raise ValueError("Anzahl der Zielsemester muss positiv sein.")
        # Validate grade is within German grading system range
        if not (1.0 <= target_grade <= 5.0):
            raise ValueError("Ziel-Notendurchschnitt muss zwischen 1.0 und 5.0 liegen.")
        
        self.name = name
        self.target_semesters = target_semesters
        self.target_grade = target_grade
        # Initialize empty list to store all semesters in chronological order
        self.semesters: List[Semester] = []
    
    def add_semester(self, semester: Semester):
        """
        Add a semester to the degree program.
        
        Args:
            semester: The Semester object to add to this program
        """
        self.semesters.append(semester)
    
    def get_all_modules(self) -> List[CourseModule]:
        """
        Return a flat list of all modules in all semesters.
        
        This method aggregates modules from all semesters into a single list,
        useful for program-wide calculations and analysis.
        
        Returns:
            List[CourseModule]: All modules from all semesters combined
        """
        all_modules = []
        # Iterate through each semester and collect all its modules
        for semester in self.semesters:
            all_modules.extend(semester.modules)
        return all_modules

    def current_semester(self) -> int:
        """
        Determine the current semester based on unpassed modules.
        
        The current semester is determined by finding the earliest semester
        that still contains modules that haven't been passed yet.
        
        Returns:
            int: The current semester number (1-indexed)
                 - Returns 1 if no modules exist yet
                 - Returns target_semesters if all modules are passed
                 - Otherwise returns the lowest semester with unpassed modules
        """
        all_modules = self.get_all_modules()
        # If no modules exist yet, student is in first semester
        if not all_modules:
            return 1
        
        # Find all semesters that have modules not yet passed
        open_semester_numbers = {
            module.planned_semester 
            for module in all_modules 
            if not module.is_passed()
        }
        
        # If all modules are passed, student is in final semester
        if not open_semester_numbers:
            return self.target_semesters
        
        # Return the earliest semester with unpassed modules
        return min(open_semester_numbers)
    
    def get_average_grade(self) -> Optional[float]:
        """
        Calculate the weighted average grade across all passed modules.
        
        The average is weighted by credit points (ECTS), so modules with more
        credits have a proportionally larger impact on the overall grade.
        Only considers the best grade for each module if multiple attempts exist.
        
        Returns:
            Optional[float]: Weighted average grade rounded to 2 decimal places,
                           or None if no modules have been passed yet
        """
        total_weighted_grade = 0.0
        total_credits = 0
        
        # Sum up weighted grades for all passed modules
        for module in self.get_all_modules():
            if module.is_passed():
                best_grade = module.best_grade()
                if best_grade is not None:
                    # Weight the grade by the module's credit points
                    total_weighted_grade += best_grade * module.credits
                    total_credits += module.credits
        
        # Return None if no modules have been completed yet
        if total_credits == 0:
            return None
        
        # Calculate and round the weighted average
        return round(total_weighted_grade / total_credits, 2)
    
    def is_completable(self) -> bool:
        """
        Check if the degree can still be completed (no critical failures).
        
        A degree becomes incompletable when any required module has exhausted
        all allowed attempts without passing (NO_MORE_ATTEMPTS status).
        
        Returns:
            bool: True if the degree can still be completed, False if any
                  module has reached the maximum failure limit
        """
        return not any(
            module.status == ModuleStatus.NO_MORE_ATTEMPTS
            for module in self.get_all_modules()
        )
    
    def get_critical_failures(self) -> List[CourseModule]:
        """
        Get all modules that prevent degree completion due to failed attempts.
        
        These are modules that have reached the maximum number of allowed
        attempts without successfully passing, making degree completion impossible.
        
        Returns:
            List[CourseModule]: All modules with NO_MORE_ATTEMPTS status
        """
        return [
            module for module in self.get_all_modules()
            if module.status == ModuleStatus.NO_MORE_ATTEMPTS
        ]
    
    def to_dict(self):
        """
        Serialize the degree program to a dictionary for storage or export.
        
        Creates a dictionary representation of the entire degree program,
        including all nested semesters and their modules. The '__class__'
        field enables proper deserialization.
        
        Returns:
            dict: Dictionary representation suitable for JSON serialization
        """
        return {
            '__class__': 'DegreeProgram',  # Enable type identification for deserialization
            'name': self.name,
            'target_semesters': self.target_semesters,
            'target_grade': self.target_grade,
            'semesters': [semester.to_dict() for semester in self.semesters]
        }