"""
Defines the main data model for the degree program, which acts as the root
container for all academic data.
"""
from typing import List, Optional
from .semester import AcademicSemester
from .module import CourseModule, ModuleStatus

class DegreeProgram:
    """
    Represents the entire degree program, holding all semesters and modules.
    
    This class serves as the main data object that will be managed by the
    application controller and persisted by the data manager.
    """
    def __init__(self, name: str, target_semesters: int, target_grade: float):
        """
        Initializes the degree program.

        Args:
            name (str): The official name of the degree program.
            target_semesters (int): The planned number of semesters.
            target_grade (float): The target average grade for graduation.
        """
        self.name = name
        self.target_semesters = target_semesters
        self.target_grade = target_grade
        self.semesters: List[AcademicSemester] = []
    
    def add_semester(self, semester: AcademicSemester):
        """
        Adds a semester to the program.

        Args:
            semester (AcademicSemester): The semester object to add.
        """
        self.semesters.append(semester)
    
    def current_semester(self) -> int:
        """
        Determines the current semester number based on the number of semesters added.

        Returns:
            int: The number of the latest semester.
        """
        return len(self.semesters)
    
    def total_earned_credits(self) -> int:
        """
        Calculates the total earned credits across all semesters.

        Returns:
            int: The sum of all earned credits.
        """
        return sum(semester.earned_credits() for semester in self.semesters)
    
    def calculate_progress(self) -> float:
        """
        Calculates the overall progress towards graduation based on a 180 ECTS total.
        
        Returns:
            float: The progress percentage.
        """
        
        total_target_credits = 180
        return (self.total_earned_credits() / total_target_credits) * 100 if total_target_credits > 0 else 0.0
    
    def calculate_average_grade(self) -> Optional[float]:
        """
        Calculates the weighted average grade of all passed modules.
        The grade of each module is weighted by its ECTS credits.
        
        Returns:
            Optional[float]: The weighted average grade, rounded to 2 decimal places,
                             or None if no modules have been passed yet.
        """
        total_weighted_grade = 0.0
        total_credits = 0
        
        for semester in self.semesters:
            for module in semester.modules:
                if module.is_passed() and module.best_exam_grade() is not None:
                    module_credits = module.credits
                    total_weighted_grade += module.best_exam_grade() * module_credits
                    total_credits += module_credits
        
        if total_credits == 0:
            return None
            
        return round(total_weighted_grade / total_credits, 2)

    def identify_risk_modules(self) -> List[CourseModule]:
        """
        Finds all modules that are currently not in a PASSED state.
        
        Returns:
            List[CourseModule]: A list of module objects that are at risk.
        """
        risk_modules = []
        for semester in self.semesters:
            for module in semester.modules:
                if module.status in (ModuleStatus.RETRY, ModuleStatus.OPEN):
                    risk_modules.append(module)
        return risk_modules
    
    def __str__(self) -> str:
        """Provides a comprehensive one-line status summary for the degree program."""
        avg_grade = self.calculate_average_grade()
        progress = self.calculate_progress()
        
        # Conditionally format the average grade string
        grade_str = f"{avg_grade:.2f}" if avg_grade is not None else "-"
        
        return (f"{self.name} | Semester: {self.current_semester()}/{self.target_semesters} "
                f"| ECTS: {self.total_earned_credits()}/180 "
                f"| Progress: {progress:.1f}% "
                f"| Average: {grade_str}")