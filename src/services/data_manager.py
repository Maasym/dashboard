import json
from datetime import date
from typing import Any

# Import all entity classes
from src.entities.program import DegreeProgram
from src.entities.semester import Semester
from src.entities.module import CourseModule, ModuleStatus
from src.entities.exam import WrittenExam, Portfolio, CaseStudyExam, OralExam, ExamStatus

def from_dict_hook(d: dict) -> Any:
    """
    Object hook for json.load to reconstruct custom objects from dictionaries.
    """
    if "__class__" not in d:
        return d

    class_name = d.pop("__class__")
    obj = None

    # --- Reconstruct Exam objects ---
    if class_name == "WrittenExam":
        obj = WrittenExam(exam_date=date.fromisoformat(d['exam_date']))
        if 'grade' in d and d['grade'] is not None:
            obj.grade = d['grade']
            obj.status = ExamStatus[d['status']]
            
    elif class_name == "Portfolio":
        obj = Portfolio(exam_date=date.fromisoformat(d['exam_date']))
        if 'grade' in d and d['grade'] is not None:
            obj.grade = d['grade']
            obj.status = ExamStatus[d['status']]
            
    elif class_name == "CaseStudyExam":
        obj = CaseStudyExam(exam_date=date.fromisoformat(d['exam_date']))
        if 'grade' in d and d['grade'] is not None:
            obj.grade = d['grade']
            obj.status = ExamStatus[d['status']]
            
    elif class_name == "OralExam":
        obj = OralExam(exam_date=date.fromisoformat(d['exam_date']))
        if 'grade' in d and d['grade'] is not None:
            obj.grade = d['grade']
            obj.status = ExamStatus[d['status']]

    # --- Reconstruct CourseModule ---
    elif class_name == "CourseModule":
        obj = CourseModule(
            name=d['name'], 
            credits=d['credits'], 
            planned_semester=d['planned_semester']
        )
        # Add exams separately to trigger status calculation
        for exam_dict in d['exams']:
            exam = from_dict_hook(exam_dict)
            obj.exams.append(exam)

    # --- Reconstruct Semester ---
    elif class_name == "Semester":
        obj = Semester(number=d['number'])
        obj.modules = [from_dict_hook(mod_dict) for mod_dict in d['modules']]

    # --- Reconstruct DegreeProgram ---
    elif class_name == "DegreeProgram":
        obj = DegreeProgram(
            name=d['name'],
            target_semesters=d['target_semesters'],
            target_grade=d['target_grade']
        )
        obj.semesters = [from_dict_hook(sem_dict) for sem_dict in d['semesters']]

    return obj

class DataManager:
    """Handles saving and loading of the application's data."""

    def save_program(self, program: DegreeProgram, filepath: str):
        """Saves the entire DegreeProgram object to a JSON file."""
        program_dict = program.to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(program_dict, f, indent=4, ensure_ascii=False)

    def load_program(self, filepath: str) -> DegreeProgram | None:
        """Loads a DegreeProgram object from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                program_dict = json.load(f)
                return from_dict_hook(program_dict)
        except FileNotFoundError:
            return None
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Error loading or parsing data: {e}")
            return None