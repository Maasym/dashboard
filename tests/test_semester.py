import unittest
from datetime import date

from src.entities.semester import Semester
from src.entities.module import CourseModule
from src.entities.exam import WrittenExam

class TestSemester(unittest.TestCase):

    def setUp(self):
        self.semester = Semester(1)
        mod1 = CourseModule("Mathe", 5, 1)
        mod2 = CourseModule("Englisch", 3, 1)
        exam1 = WrittenExam(date(2023,10,1))
        exam1.record_result(2.0)
        exam2 = WrittenExam(date(2023,10,2))
        exam2.record_result(3.0)
        mod1.add_exam(exam1)
        mod2.add_exam(exam2)
        self.semester.add_module(mod1)
        self.semester.add_module(mod2)

    def test_credit_calculation(self):
        self.assertEqual(self.semester.total_credits(), 8)