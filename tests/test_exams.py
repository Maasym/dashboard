import unittest
from datetime import date
from src.entities.exam import WrittenExam, Portfolio, CaseStudyExam, OralExam, ExamStatus, StateError

class TestExamLifecycle(unittest.TestCase):

    def setUp(self):
        self.written_exam = WrittenExam(date(2023, 12, 15))
        self.portfolio = Portfolio(date(2023, 11, 20))
        self.case_study = CaseStudyExam(date(2023, 10, 10))
        self.oral_exam = OralExam(date(2023, 9, 5))

    def test_initial_state(self):
        for exam in [self.written_exam, self.portfolio, self.case_study, self.oral_exam]:
            self.assertIsNone(exam.grade)
            self.assertEqual(exam.status, ExamStatus.PLANNED)

    def test_record_result_valid(self):
        self.written_exam.record_result(2.0)
        self.assertEqual(self.written_exam.grade, 2.0)
        self.assertEqual(self.written_exam.status, ExamStatus.PASSED)

    def test_pass_conditions(self):
        self.portfolio.record_result(3.5)
        self.assertEqual(self.portfolio.status, ExamStatus.PASSED)
        self.case_study.record_result(4.0)
        self.assertEqual(self.case_study.status, ExamStatus.PASSED)
        self.oral_exam.record_result(5.0)
        self.assertEqual(self.oral_exam.status, ExamStatus.FAILED)

    def test_is_passed_without_result(self):
        with self.assertRaises(StateError):
            _ = self.written_exam.is_passed()