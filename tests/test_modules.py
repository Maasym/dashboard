import unittest
from datetime import date
from src.entities.module import CourseModule, ModuleStatus
from src.entities.exam import WrittenExam, Portfolio, ExamStatus

class TestCourseModule(unittest.TestCase):
    def setUp(self):
        self.module = CourseModule("Mathematics", 5)
        self.written_exam = WrittenExam(date(2023,12,15), 90)
        self.portfolio = Portfolio(date(2023,11,20), ["Topic1", "Topic2", "Topic3"])
    
    def test_initial_state(self):
        self.assertEqual(self.module.status, ModuleStatus.OPEN)
        self.assertEqual(len(self.module.exams), 0)
    
    def test_add_open_exam(self):
        self.module.add_exam(self.written_exam)
        self.assertEqual(self.module.status, ModuleStatus.OPEN)
        self.assertEqual(len(self.module.exams), 1)
    
    def test_passed_module(self):
        self.written_exam.record_result(2.3)
        self.module.add_exam(self.written_exam)
        self.assertEqual(self.module.status, ModuleStatus.PASSED)
        self.assertEqual(self.module.best_exam_grade(), 2.3)
    
    def test_retry_module(self):
        self.written_exam.record_result(4.3)
        self.module.add_exam(self.written_exam)
        self.assertEqual(self.module.status, ModuleStatus.RETRY)
        self.assertIsNone(self.module.best_exam_grade())
    
    def test_multiple_attempts(self):
        failed_exam = WrittenExam(date(2023,6,10), 90)
        failed_exam.record_result(4.7)
        self.module.add_exam(failed_exam)
        self.assertEqual(self.module.status, ModuleStatus.RETRY)
        
        passed_exam = WrittenExam(date(2023,9,15), 90)
        passed_exam.record_result(2.0)
        self.module.add_exam(passed_exam)
        self.assertEqual(self.module.status, ModuleStatus.PASSED)
        self.assertEqual(self.module.best_exam_grade(), 2.0)

if __name__ == '__main__':
    unittest.main()