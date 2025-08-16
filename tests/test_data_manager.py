import unittest
import os
from datetime import date
from src.services.data_manager import DataManager
from src.entities.program import DegreeProgram
from src.entities.semester import Semester
from src.entities.module import CourseModule
from src.entities.exam import WrittenExam

class TestDataManager(unittest.TestCase):

    def setUp(self):
        self.manager = DataManager()
        self.filepath = "test_program.json"
        self.program = DegreeProgram("TestProg", 1, 2.0)
        semester = Semester(1)
        module = CourseModule("Mathe", 5, 1)
        exam = WrittenExam(date(2024,7,20))
        exam.record_result(2.0)
        module.add_exam(exam)
        semester.add_module(module)
        self.program.add_semester(semester)

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def test_save_and_load_roundtrip(self):
        self.manager.save_program(self.program, self.filepath)
        loaded = self.manager.load_program(self.filepath)
        self.assertEqual(loaded.name, self.program.name)
        self.assertEqual(loaded.get_average_grade(), self.program.get_average_grade())

    def test_load_nonexistent_file(self):
        loaded = self.manager.load_program("nonexistent_file.json")
        self.assertIsNone(loaded)

    def test_load_corrupt_file(self):
        with open(self.filepath, "w") as f:
            f.write("{ invalid json")
        loaded = self.manager.load_program(self.filepath)
        self.assertIsNone(loaded)