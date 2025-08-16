import unittest
from datetime import date

from src.entities.exam import Exam, WrittenExam, Portfolio, ExamStatus, ExamType, StateError

class TestExamLifecycle(unittest.TestCase):
    """Tests core functionality of the Exam base class."""
    
    def test_initial_state(self):
        """Test exam initialization in planned state."""
        exam = WrittenExam(date(2023, 12, 15), 90)
        self.assertEqual(exam.status, ExamStatus.PLANNED)
        self.assertIsNone(exam.grade)
        
    def test_record_result_valid(self):
        """Test recording valid exam results."""
        exam = WrittenExam(date(2023, 12, 15), 90)
        exam.record_result(2.3)
        self.assertEqual(exam.grade, 2.3)
        self.assertEqual(exam.status, ExamStatus.PASSED)
        
    def test_record_result_invalid_grade(self):
        """Test invalid grade handling."""
        exam = WrittenExam(date(2023, 12, 15), 90)
        with self.assertRaises(ValueError):
            exam.record_result(0.9)  # Too low
        with self.assertRaises(ValueError):
            exam.record_result(5.1)  # Too high

class TestWrittenExam(unittest.TestCase):
    """Tests specific functionality of WrittenExam class."""
    
    def test_pass_conditions(self):
        """Test passing conditions for written exams."""
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
        """Test state error when checking result before recording."""
        exam = WrittenExam(date(2023, 12, 15), 90)
        with self.assertRaises(StateError):
            exam.is_passed()

class TestPortfolio(unittest.TestCase):
    """Tests specific functionality of Portfolio class."""
    
    def test_pass_conditions(self):
        """Test passing conditions for portfolios."""
        # Passing case
        portfolio = Portfolio(date(2023, 11, 20), ["Topic1", "Topic2", "Topic3"])
        portfolio.record_result(3.7)
        self.assertTrue(portfolio.is_passed())
        
        # Failing cases
        failing_cases = [
            (["Topic1"], 2.3),        # Too few topics
            (["A", "B", "C", "D"], 4.1), # Grade too high
            (["A", "B"], 1.0)          # Too few topics even with perfect grade
        ]
        
        for topics, grade in failing_cases:
            portfolio = Portfolio(date(2023, 11, 20), topics)
            portfolio.record_result(grade)
            self.assertFalse(portfolio.is_passed())
    
    def test_topic_requirement(self):
        """Test minimum topic requirement."""
        # Exactly 3 topics - should pass
        portfolio = Portfolio(date(2023, 11, 20), ["A", "B", "C"])
        portfolio.record_result(4.0)
        self.assertTrue(portfolio.is_passed())
        
        # 2 topics - should fail
        portfolio = Portfolio(date(2023, 11, 20), ["A", "B"])
        portfolio.record_result(2.0)
        self.assertFalse(portfolio.is_passed())

class TestStateTransitions(unittest.TestCase):
    """Tests state transitions after recording results."""
    
    def test_state_transition_written(self):
        """Test state changes for written exams."""
        exam = WrittenExam(date(2023, 12, 15), 90)
        exam.record_result(1.7)
        self.assertEqual(exam.status, ExamStatus.PASSED)
        
        exam.record_result(4.3)
        self.assertEqual(exam.status, ExamStatus.FAILED)
    
    def test_state_transition_portfolio(self):
        """Test state changes for portfolios."""
        portfolio = Portfolio(date(2023, 11, 20), ["A", "B", "C"])
        portfolio.record_result(3.9)
        self.assertEqual(portfolio.status, ExamStatus.PASSED)
        
        portfolio.record_result(4.1)
        self.assertEqual(portfolio.status, ExamStatus.FAILED)

if __name__ == '__main__':
    unittest.main()