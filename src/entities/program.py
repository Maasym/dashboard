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
        self.name = name
        self.target_semesters = target_semesters
        self.target_grade = target_grade
        self.semesters: List[Semester] = []
    
    def add_semester(self, semester: Semester):
        self.semesters.append(semester)
    
    def get_all_modules(self) -> List[CourseModule]:
        all_modules = []
        for semester in self.semesters:
            all_modules.extend(semester.modules)
        return all_modules

    def current_semester(self) -> int:
        all_modules = self.get_all_modules()
        if not all_modules:
            return 1
        open_semester_numbers = {
            module.planned_semester 
            for module in all_modules 
            if not module.is_passed()
        }
        if not open_semester_numbers:
            return self.target_semesters
        return min(open_semester_numbers)
    
    def get_average_grade(self) -> Optional[float]:
        total_weighted_grade = 0.0
        total_credits = 0
        for module in self.get_all_modules():
            if module.is_passed():
                best_grade = module.best_grade()
                if best_grade is not None:
                    total_weighted_grade += best_grade * module.credits
                    total_credits += module.credits
        if total_credits == 0:
            return None
        return round(total_weighted_grade / total_credits, 2)
    
    def to_dict(self):
        return {
            '__class__': 'DegreeProgram',
            'name': self.name,
            'target_semesters': self.target_semesters,
            'target_grade': self.target_grade,
            'semesters': [semester.to_dict() for semester in self.semesters]
        }