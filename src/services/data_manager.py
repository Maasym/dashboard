import json
from datetime import date
from typing import Any

# Import all entity classes to be able to reconstruct them from the JSON data
from src.entities.program import DegreeProgram
from src.entities.semester import AcademicSemester
from src.entities.module import CourseModule
from src.entities.exam import WrittenExam, Portfolio, ExamStatus, ExamType

def from_dict_hook(d: dict) -> Any:
    """
    Object hook for json.load to reconstruct custom objects from dictionaries.
    This function is the core of the deserialization process.
    """
    if "__class__" not in d:
        return d

    class_name = d.pop("__class__")
    
    # Reconstruct the entity based on its class name
    obj = None

    # --- Reconstruction of Exam hierarchy ---
    if class_name == "WrittenExam":
        obj = WrittenExam(exam_date=date.fromisoformat(d['exam_date']), 
                          duration_minutes=d['duration_minutes'])
    elif class_name == "Portfolio":
        obj = Portfolio(exam_date=date.fromisoformat(d['exam_date']), 
                        submission_topics=d['submission_topics'])
    
    # --- Reconstruction of other entities ---
    elif class_name == "CourseModule":
        obj = CourseModule(name=d['name'], credits=d['credits'])
        # Recursively reconstruct the contained exams
        obj.exams = [from_dict_hook(exam_dict) for exam_dict in d['exams']]
    
    elif class_name == "AcademicSemester":
        obj = AcademicSemester(number=d['number'])
        obj.modules = [from_dict_hook(mod_dict) for mod_dict in d['modules']]
        
    elif class_name == "DegreeProgram":
        obj = DegreeProgram(name=d['name'], 
                            target_semesters=d['target_semesters'], 
                            target_grade=d['target_grade'])
        obj.semesters = [from_dict_hook(sem_dict) for sem_dict in d['semesters']]

    # Manually set the remaining attributes that are not in the constructor (e.g., grade, status)
    if hasattr(obj, 'grade') and 'grade' in d:
        obj.grade = d['grade']
    if hasattr(obj, 'status') and 'status' in d:
        # Convert the string back into an Enum member
        obj.status = ExamStatus[d['status']]

    return obj if obj else d


class DataManager:
    """Handles saving and loading of the application's data."""

    def save_program(self, program: DegreeProgram, filepath: str):
        """
        Saves the entire DegreeProgram object to a JSON file.
        
        Args:
            program (DegreeProgram): The main program object to save.
            filepath (str): The path to the JSON file.
        """
        program_dict = program.to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(program_dict, f, indent=4, ensure_ascii=False)

    def load_program(self, filepath: str) -> DegreeProgram | None:
        """
        Loads a DegreeProgram object from a JSON file.
        
        Args:
            filepath (str): The path to the JSON file.

        Returns:
            DegreeProgram | None: The reconstructed program object, or None if the file doesn't exist.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                program_dict = json.load(f)
                return from_dict_hook(program_dict)
        except FileNotFoundError:
            return None # It's normal for the file not to exist on first run
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Error loading or parsing data: {e}")
            return None # Data is corrupt or structure is wrong