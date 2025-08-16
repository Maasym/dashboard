import unittest
from datetime import date
from src.entities.module import CourseModule, ModuleStatus
from src.entities.exam import WrittenExam, ExamStatus

class TestCourseModule(unittest.TestCase):

    def setUp(self):
        self.module = CourseModule("Mathe", 5, 1)

    def test_initial_status(self):
        self.assertEqual(self.module.status, ModuleStatus.PLANNED)

    def test_status_in_progress(self):
        exam = WrittenExam(date(2023,12,15))
        exam.record_result(5.0)
        self.module.add_exam(exam)
        self.assertEqual(self.module.status, ModuleStatus.FAILED)

    def test_status_passed(self):
        exam = WrittenExam(date(2023,12,15))
        exam.record_result(2.0)
        self.module.add_exam(exam)
        self.assertEqual(self.module.status, ModuleStatus.PASSED)

    def test_best_grade(self):
        exam1 = WrittenExam(date(2023,12,15))
        exam1.record_result(3.0)
        exam2 = WrittenExam(date(2023,12,16))
        exam2.record_result(2.0)
        self.module.add_exam(exam1)
        self.module.add_exam(exam2)
        self.assertEqual(self.module.best_grade(), 2.0)