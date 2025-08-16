from datetime import date, timedelta
from typing import List
from src.entities.exam import ExamStatus
from src.entities.program import DegreeProgram
from src.entities.module import CourseModule, ModuleStatus

class ProgressAnalyzer:
    def __init__(self, program: DegreeProgram):
        self.program = program
    
    def calculate_ects_trend(self) -> str:
        """Determines if ECTS accumulation is on track"""
        total_credits = sum(m.credits for m in self.program.get_all_modules())
        earned_credits = sum(m.credits for m in self.program.get_all_modules() 
                             if m.status == ModuleStatus.PASSED)
        
        # Calculate percentage completion
        completion = earned_credits / total_credits if total_credits > 0 else 0
        semesters_used = max(1, self.program.current_semester() - 1)
        expected_completion = semesters_used / self.program.target_semesters
        
        if completion >= expected_completion:
            return "Im Plan"
        elif completion >= expected_completion * 0.75:
            return "Leicht zurück"
        return "Weit zurück"

    def predict_graduation(self) -> date:
        """Estimates graduation date based on current pace"""
        today = date.today()
        semesters_left = self.program.target_semesters - self.program.current_semester() + 1
        
        # Assuming 6 months per semester
        days_per_semester = 180
        return today + timedelta(days=days_per_semester * semesters_left)
    
    def identify_risk_modules(self) -> List[CourseModule]:
        """Finds modules with failed exams or nearing deadlines"""
        risk_modules = []
        current_semester = self.program.current_semester()
        
        for module in self.program.get_all_modules():
            # Failed modules
            if module.status == ModuleStatus.FAILED:
                risk_modules.append(module)
            
            # Planned modules in past semesters
            elif (module.status == ModuleStatus.PLANNED and 
                  module.planned_semester < current_semester):
                risk_modules.append(module)
                
            # Modules with multiple failed attempts
            elif (module.status == ModuleStatus.IN_PROGRESS and
                  sum(1 for e in module.exams if e.status == ExamStatus.FAILED) >= 2):
                risk_modules.append(module)
                
        return risk_modules