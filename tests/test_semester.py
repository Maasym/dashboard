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

    def test_empty_semester_has_zero_credits(self):
        empty_semester = Semester(2)
        self.assertEqual(empty_semester.total_credits(), 0)

    def test_add_module_increases_count(self):
        new_mod = CourseModule("Physik", 4, 1)
        self.semester.add_module(new_mod)
        self.assertEqual(len(self.semester.modules), 3)

    def test_semester_with_no_passed_modules(self):
        semester = Semester(2)
        mod = CourseModule("Bio", 5, 2)
        exam = WrittenExam(date(2023,11,1))
        exam.record_result(5.0)  # failed
        mod.add_exam(exam)
        semester.add_module(mod)
        passed = [m for m in semester.modules if m.is_passed()]
        self.assertEqual(len(passed), 0)

    def test_semester_with_all_modules_failed(self):
        semester = Semester(3)
        mod1 = CourseModule("Chemie", 5, 3)
        mod2 = CourseModule("Physik", 3, 3)
        exam1 = WrittenExam(date(2023,12,1))
        exam1.record_result(5.0)
        exam2 = WrittenExam(date(2023,12,2))
        exam2.record_result(5.0)
        mod1.add_exam(exam1)
        mod2.add_exam(exam2)
        semester.add_module(mod1)
        semester.add_module(mod2)
        failed = [m for m in semester.modules if not m.is_passed()]
        self.assertEqual(len(failed), 2)

    def test_add_same_module_twice(self):
        mod = CourseModule("Mathe", 5, 1)
        self.semester.add_module(mod)
        self.assertEqual(len(self.semester.modules), 3)