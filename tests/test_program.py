import unittest
from datetime import date
from src.entities.program import DegreeProgram
from src.entities.semester import Semester
from src.entities.module import CourseModule
from src.entities.exam import WrittenExam

class TestDegreeProgram(unittest.TestCase):

    def setUp(self):
        self.program = DegreeProgram("TestProg", target_semesters=2, target_grade=2.0)
        semester1 = Semester(1)
        mod = CourseModule("Mathe", 5, 1)
        exam = WrittenExam(date(2023,12,15))
        exam.record_result(2.0)
        mod.add_exam(exam)
        semester1.add_module(mod)
        self.program.add_semester(semester1)

    def test_average_grade_calculation(self):
        avg = self.program.get_average_grade()
        self.assertEqual(avg, 2.0)

    def test_current_semester_logic(self):
        current = self.program.current_semester()
        self.assertEqual(current, 2)