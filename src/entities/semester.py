"""
Defines the data model for an academic semester, which groups a collection of modules.
"""
from typing import List
from .module import CourseModule, ModuleStatus

class Semester:
    """
    Represents a single academic semester containing multiple course modules.
    
    A semester serves as an organizational container for grouping modules
    by their planned completion period. It provides aggregation methods
    for calculating total credits and tracking completion progress.
    """
    
    def __init__(self, number: int):
        """
        Initialize a new semester with validation.
        
        Args:
            number: The semester number (1-indexed, must be positive)
            
        Raises:
            ValueError: If the semester number is not positive
        """
        # Validate semester number is positive (1-indexed system)
        if number <= 0:
            raise ValueError("Semester-Nummer muss positiv sein.")
        self.number = number
        # Initialize empty list to hold all modules for this semester
        self.modules: List[CourseModule] = []
    
    def add_module(self, module: CourseModule):
        """
        Add a course module to this semester.
        
        Args:
            module: The CourseModule to add to this semester
        """
        self.modules.append(module)

    def total_credits(self) -> int:
        """
        Calculate the total ECTS credits of all modules in this semester.
        
        Sums up the credit points from all modules planned for this semester,
        regardless of their completion status.
        
        Returns:
            int: Total ECTS credit points for this semester
        """
        return sum(module.credits for module in self.modules)
    
    def get_achieved_credits(self) -> int:
        """
        Calculate the ECTS credits achieved from successfully passed modules.
        
        Only counts credits from modules that have been successfully completed
        (passed status). This represents the actual credit progress made.
        
        Returns:
            int: Total ECTS credits from passed modules in this semester
        """
        return sum(
            module.credits 
            for module in self.modules 
            if module.is_passed()
        )
    
    def to_dict(self):
        """
        Serialize the semester to a dictionary for storage or export.
        
        Creates a dictionary representation of the semester including all
        its modules. The '__class__' field enables proper deserialization.
        
        Returns:
            dict: Dictionary representation suitable for JSON serialization
        """
        return {
            '__class__': 'Semester',  # Enable type identification for deserialization
            'number': self.number,
            'modules': [module.to_dict() for module in self.modules]
        }