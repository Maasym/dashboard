"""
Data persistence and serialization service for the academic management system.

This module handles the complex process of serializing and deserializing the
academic program data structure to/from JSON format, including proper
reconstruction of all nested objects with their relationships intact.
"""
import json
from datetime import date
from typing import Any

# Import all entity classes for deserialization
from src.entities.program import DegreeProgram
from src.entities.semester import Semester
from src.entities.module import CourseModule, ModuleStatus
from src.entities.exam import WrittenExam, Portfolio, CaseStudyExam, OralExam, ExamStatus

def from_dict_hook(d: dict) -> Any:
    """
    Custom object hook for JSON deserialization to reconstruct entity objects.
    
    This function is used by json.load() to convert dictionary representations
    back into their original entity objects. It handles the complex object
    hierarchy including nested relationships between programs, semesters,
    modules, and exams while maintaining all state information.
    
    Args:
        d: Dictionary potentially containing serialized object data
        
    Returns:
        Any: Reconstructed object or original dictionary if not serialized
    """
    # Only process dictionaries that have the special __class__ identifier
    if "__class__" not in d:
        return d

    # Extract class name and remove it from data (consumed by reconstruction)
    class_name = d.pop("__class__")
    obj = None

    # === Reconstruct Exam objects ===
    # Each exam type requires special handling for grade and status restoration
    if class_name == "WrittenExam":
        obj = WrittenExam(exam_date=date.fromisoformat(d['exam_date']))
        # Restore grade and status if exam has been completed
        if 'grade' in d and d['grade'] is not None:
            obj.grade = d['grade']
            obj.status = ExamStatus[d['status']]
            
    elif class_name == "Portfolio":
        obj = Portfolio(exam_date=date.fromisoformat(d['exam_date']))
        # Restore grade and status for completed portfolio submissions
        if 'grade' in d and d['grade'] is not None:
            obj.grade = d['grade']
            obj.status = ExamStatus[d['status']]
            
    elif class_name == "CaseStudyExam":
        obj = CaseStudyExam(exam_date=date.fromisoformat(d['exam_date']))
        # Restore grade and status for completed case studies
        if 'grade' in d and d['grade'] is not None:
            obj.grade = d['grade']
            obj.status = ExamStatus[d['status']]
            
    elif class_name == "OralExam":
        obj = OralExam(exam_date=date.fromisoformat(d['exam_date']))
        # Restore grade and status for completed oral examinations
        if 'grade' in d and d['grade'] is not None:
            obj.grade = d['grade']
            obj.status = ExamStatus[d['status']]

    # === Reconstruct CourseModule ===
    elif class_name == "CourseModule":
        # Create module with basic metadata
        obj = CourseModule(
            name=d['name'], 
            credits=d['credits'], 
            planned_semester=d['planned_semester']
        )
        # Reconstruct and add all exams (status will be calculated dynamically)
        # We use append instead of add_exam to avoid attempt validation during deserialization
        for exam_dict in d['exams']:
            exam = from_dict_hook(exam_dict)
            obj.exams.append(exam)

    # === Reconstruct Semester ===
    elif class_name == "Semester":
        # Create semester with semester number
        obj = Semester(number=d['number'])
        # Recursively reconstruct all modules in this semester
        obj.modules = [from_dict_hook(mod_dict) for mod_dict in d['modules']]

    # === Reconstruct DegreeProgram ===
    elif class_name == "DegreeProgram":
        # Create program with metadata and validation
        obj = DegreeProgram(
            name=d['name'],
            target_semesters=d['target_semesters'],
            target_grade=d['target_grade']
        )
        # Recursively reconstruct all semesters (and their nested modules/exams)
        obj.semesters = [from_dict_hook(sem_dict) for sem_dict in d['semesters']]

    # Return the reconstructed object (or None if class_name not recognized)
    return obj

class DataManager:
    """
    Service class responsible for persisting and loading academic program data.
    
    This class provides a clean interface for saving and loading DegreeProgram
    objects to/from JSON files, handling all the complexity of serialization
    and deserialization through the custom object hook system.
    """

    def save_program(self, program: DegreeProgram, filepath: str):
        """
        Save a complete DegreeProgram object hierarchy to a JSON file.
        
        This method converts the entire program structure (including all
        semesters, modules, and exams) into a JSON-serializable format
        and writes it to the specified file with proper encoding.
        
        Args:
            program: The DegreeProgram object to save
            filepath: Path where the JSON file should be saved
            
        Raises:
            IOError: If file cannot be written
            TypeError: If program contains non-serializable data
        """
        # Convert program to dictionary representation using entity's to_dict methods
        program_dict = program.to_dict()
        
        # Write to file with UTF-8 encoding and pretty formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(program_dict, f, indent=4, ensure_ascii=False)

    def load_program(self, filepath: str) -> DegreeProgram | None:
        """
        Load a DegreeProgram object from a JSON file.
        
        This method reads the JSON file and reconstructs the complete object
        hierarchy using the custom from_dict_hook function. All relationships
        between entities are preserved during deserialization.
        
        Args:
            filepath: Path to the JSON file to load
            
        Returns:
            DegreeProgram: The reconstructed program object, or None if file
                         doesn't exist or loading fails
        """
        try:
            # Read and parse JSON file with custom object reconstruction
            with open(filepath, 'r', encoding='utf-8') as f:
                program_dict = json.load(f)
                return from_dict_hook(program_dict)
        except FileNotFoundError:
            # File doesn't exist - this is normal for new installations
            return None
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            # Handle corrupted or invalid JSON data gracefully
            print(f"Error loading or parsing data: {e}")
            return None