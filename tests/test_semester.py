import unittest
from datetime import date
from src.entities.semester import AcademicSemester
from src.entities.module import CourseModule
from src.entities.exam import WrittenExam

class TestAcademicSemester(unittest.TestCase):
    def setUp(self):
        """Prepares a realistic test scenario before each test."""
        self.semester = AcademicSemester(1)
        
        # Setup Math module -> status will be PASSED
        self.math = CourseModule("Mathematics", 5)
        math_exam = WrittenExam(date(2023, 10, 1), 90)
        math_exam.record_result(2.0)
        self.math.add_exam(math_exam)
        
        # Setup Physics module -> status will be OPEN
        self.physics = CourseModule("Physics", 5)
        physics_exam = WrittenExam(date(2023, 11, 1), 90)
        self.physics.add_exam(physics_exam)
        
        # Setup CS module -> status will be RETRY
        self.cs = CourseModule("Computer Science", 10)
        cs_exam = WrittenExam(date(2023, 9, 1), 90)
        cs_exam.record_result(5.0)
        self.cs.add_exam(cs_exam)
    
    def test_initial_state(self):
        """Tests an empty semester right after creation."""
        empty_semester = AcademicSemester(1)
        self.assertEqual(empty_semester.number, 1)
        self.assertEqual(len(empty_semester.modules), 0)
        self.assertEqual(empty_semester.earned_credits(), 0)
        self.assertEqual(empty_semester.progress_percentage(), 0.0)
    
    def test_add_modules_and_total_credits(self):
        """Tests adding modules and calculating total possible credits."""
        self.semester.add_module(self.math)
        self.semester.add_module(self.physics)
        self.semester.add_module(self.cs)
        self.assertEqual(len(self.semester.modules), 3)
        self.assertEqual(self.semester.total_possible_credits(), 20)
    
    def test_credit_calculation_with_state_change(self):
        """Tests calculation of earned credits and its update after an exam retake."""
        self.semester.add_module(self.math)
        self.semester.add_module(self.physics)
        self.semester.add_module(self.cs)
        
        # Initially, only the 'math' module is passed, contributing 5 credits.
        self.assertEqual(self.semester.earned_credits(), 5)
        
        # --- ACT: Simulate a successful retake for the CS module ---
        cs_exam_retake = WrittenExam(date(2024, 2, 1), 90)
        cs_exam_retake.record_result(3.0)
        self.cs.add_exam(cs_exam_retake)
        
        # Now, credits should be 5 (math) + 10 (cs) = 15
        self.assertEqual(self.semester.earned_credits(), 15)
    
    def test_progress_calculation_with_state_change(self):
        """Tests percentage progress and its update after an exam retake."""
        self.semester.add_module(self.math)
        self.semester.add_module(self.physics)
        self.semester.add_module(self.cs)
        
        # 5 of 20 credits are earned -> 25%
        self.assertEqual(self.semester.progress_percentage(), 25.0)
        
        # --- ACT: Simulate a successful retake for the CS module ---
        cs_exam_retake = WrittenExam(date(2024, 2, 1), 90)
        cs_exam_retake.record_result(3.0)
        self.cs.add_exam(cs_exam_retake)
        
        # 15 of 20 credits are earned -> 75%
        self.assertEqual(self.semester.progress_percentage(), 75.0)

if __name__ == '__main__':
    unittest.main()