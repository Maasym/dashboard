import unittest
from datetime import date
from src.entities.exam import Exam, WrittenExam, Portfolio, ExamStatus, ExamType

class TestExamLifecycle(unittest.TestCase):
    def test_initial_state(self):
        exam = WrittenExam(date(2023, 12, 15), 90)
        self.assertEqual(exam.status, ExamStatus.OPEN)
        self.assertIsNone(exam.grade)
        
    def test_record_result_valid(self):
        exam = WrittenExam(date(2023, 12, 15), 90)
        exam.record_result(2.3)
        self.assertEqual(exam.grade, 2.3)
        self.assertEqual(exam.status, ExamStatus.PASSED)

class TestWrittenExam(unittest.TestCase):
    def test_pass_conditions(self):
        exam = WrittenExam(date(2023, 12, 15), 90)
        
        # Passing grades
        for grade in [1.0, 2.3, 4.0]:
            exam.record_result(grade)
            self.assertTrue(exam.is_passed())
        
        # Failing grades
        for grade in [4.1, 4.3, 5.0]:
            exam.record_result(grade)
            self.assertFalse(exam.is_passed())
    
    def test_is_passed_without_result(self):
        exam = WrittenExam(date(2023, 12, 15), 90)
        with self.assertRaises(RuntimeError):
            exam.is_passed()

class TestPortfolio(unittest.TestCase):
    def test_pass_conditions(self):
        portfolio = Portfolio(date(2023, 11, 20), ["Topic1", "Topic2", "Topic3"])
        portfolio.record_result(3.7)
        self.assertTrue(portfolio.is_passed())
        
        # Failing cases
        failing_cases = [
            (["Topic1"], 2.3),
            (["A", "B", "C", "D"], 4.1),
            (["A", "B"], 1.0)
        ]
        
        for topics, grade in failing_cases:
            portfolio = Portfolio(date(2023, 11, 20), topics)
            portfolio.record_result(grade)
            self.assertFalse(portfolio.is_passed())

class TestStateTransitions(unittest.TestCase):
    def test_state_transition_written(self):
        exam = WrittenExam(date(2023, 12, 15), 90)
        exam.record_result(1.7)
        self.assertEqual(exam.status, ExamStatus.PASSED)
        
        exam.record_result(4.3)
        self.assertEqual(exam.status, ExamStatus.RETRY)
    
    def test_state_transition_portfolio(self):
        portfolio = Portfolio(date(2023, 11, 20), ["A", "B", "C"])
        portfolio.record_result(3.9)
        self.assertEqual(portfolio.status, ExamStatus.PASSED)
        
        portfolio.record_result(4.1)
        self.assertEqual(portfolio.status, ExamStatus.RETRY)

if __name__ == '__main__':
    unittest.main()