"""
Academic progress analysis service providing insights and predictions.

This module analyzes academic performance data to provide valuable insights
including progress tracking, graduation predictions, and risk assessment
for students and academic advisors.
"""
from datetime import date, timedelta
from typing import List, Optional
from src.entities.exam import ExamStatus
from src.entities.program import DegreeProgram
from src.entities.module import CourseModule, ModuleStatus, MAX_ATTEMPTS

class ProgressAnalyzer:
    """
    Service class for analyzing academic progress and generating predictions.
    
    This analyzer provides comprehensive insights into a student's academic
    journey including:
    - ECTS credit accumulation trends
    - Graduation date predictions
    - Risk module identification
    - Progress benchmarking against target timeline
    """
    
    def __init__(self, program: DegreeProgram):
        """
        Initialize the analyzer with a degree program to analyze.
        
        Args:
            program: The DegreeProgram object containing all academic data
        """
        self.program = program
    
    def calculate_ects_trend(self) -> str:
        """
        Analyze ECTS credit accumulation trend compared to target timeline.
        
        This method evaluates whether the student is on track to complete their
        degree within the planned timeframe by comparing actual credit progress
        against expected progress at the current semester.
        
        Returns:
            str: Progress status description:
                - "KRITISCH" if degree cannot be completed
                - "Im Plan" if progress meets or exceeds expectations
                - "Leicht zurückliegend" if slightly behind but recoverable
                - "Deutlich zurückliegend" if significantly behind schedule
        """
        # Critical case: degree cannot be completed due to failed modules
        if not self.program.is_completable():
            return "[red]KRITISCH - Studium nicht abschließbar[/red]"
        
        # Calculate actual vs expected progress metrics
        total_credits = sum(m.credits for m in self.program.get_all_modules())
        earned_credits = sum(m.credits for m in self.program.get_all_modules() 
                             if m.status == ModuleStatus.PASSED)
        
        # Calculate completion ratios
        completion = earned_credits / total_credits if total_credits > 0 else 0
        semesters_used = max(1, self.program.current_semester() - 1)
        expected_completion = semesters_used / self.program.target_semesters
        
        # Categorize progress status with tolerance thresholds
        if completion >= expected_completion:
            return "Im Plan"  # On track or ahead
        elif completion >= expected_completion * 0.75:
            return "Leicht zurückliegend"  # Slightly behind but manageable
        return "Deutlich zurückliegend"  # Significantly behind

    def predict_graduation(self) -> Optional[date]:
        """
        Predict graduation date based on current semester progress.
        
        This method calculates an estimated graduation date by determining
        how many semesters remain and projecting forward from the current date.
        The calculation assumes a standard academic semester length.
        
        Returns:
            Optional[date]: Predicted graduation date, or None if degree
                          cannot be completed due to critical failures
        """
        # Cannot predict graduation if degree is no longer completable
        if not self.program.is_completable():
            return None
        
        # Calculate time projection based on remaining semesters
        today = date.today()
        semesters_left = self.program.target_semesters - self.program.current_semester() + 1
        
        # Standard academic semester duration (6 months = ~180 days)
        days_per_semester = 180
        return today + timedelta(days=days_per_semester * semesters_left)
    
    def identify_risk_modules(self) -> List[CourseModule]:
        """
        Identify modules that pose risks to successful degree completion.
        
        This method analyzes all modules to find those that require immediate
        attention due to various risk factors including:
        - Modules that have exhausted all attempts (critical)
        - Failed modules that can still be retried
        - Overdue planned modules from past semesters
        - Modules with very few attempts remaining
        
        Returns:
            List[CourseModule]: All modules identified as presenting completion risks
        """
        risk_modules = []
        current_semester = self.program.current_semester()
        
        for module in self.program.get_all_modules():
            # Critical risk: Module permanently failed (no more attempts)
            if module.status == ModuleStatus.NO_MORE_ATTEMPTS:
                risk_modules.append(module)
            
            # High risk: Module failed but can still be retried
            elif module.status == ModuleStatus.FAILED:
                risk_modules.append(module)
            
            # Medium risk: Planned modules that should have been started by now
            elif (module.status == ModuleStatus.PLANNED and 
                  module.planned_semester < current_semester):
                risk_modules.append(module)
            
            # Medium risk: Modules in progress with very few attempts remaining
            elif (module.status == ModuleStatus.IN_PROGRESS and
                  module.remaining_attempts() <= 1):  # Last chance
                risk_modules.append(module)
                
        return risk_modules