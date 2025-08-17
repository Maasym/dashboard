"""
Defines the data model for an academic semester, which groups a collection of modules.
"""
from typing import List
from .module import CourseModule, ModuleStatus

class Semester:
    """Represents a single academic semester containing multiple course modules."""
    def __init__(self, number: int):
        if number <= 0:
            raise ValueError("Semester-Nummer muss positiv sein.")
        self.number = number
        self.modules: List[CourseModule] = []
    
    def add_module(self, module: CourseModule):
        self.modules.append(module)

    def total_credits(self) -> int:
        """Calculates the total credits of all modules in this semester."""
        return sum(module.credits for module in self.modules)
    
    def get_achieved_credits(self) -> int:
        return sum(
            module.credits 
            for module in self.modules 
            if module.is_passed()
        )
    
    def to_dict(self):
        return {
            '__class__': 'Semester',
            'number': self.number,
            'modules': [module.to_dict() for module in self.modules]
        }