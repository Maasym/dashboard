import unittest
import os
import json
from datetime import date

# Import all necessary classes for creating a test object
from src.entities.program import DegreeProgram
from src.entities.semester import AcademicSemester
from src.entities.module import CourseModule
from src.entities.exam import WrittenExam, Portfolio

# Import the class we want to test
from src.services.data_manager import DataManager

class TestDataManager(unittest.TestCase):
    """Tests the DataManager's save and load functionality."""

    def setUp(self):
        """Set up a realistic test scenario and a temporary file path."""
        self.data_manager = DataManager()
        self.test_filepath = "test_data.json"

        # Create a complex, nested DegreeProgram object for testing
        self.program = DegreeProgram("Test B.Sc.", 6, 2.0)
        semester1 = AcademicSemester(1)
        
        # Module 1: Passed
        math = CourseModule("Mathematics", 10)
        math_exam = WrittenExam(date(2024, 7, 20), 90)
        math_exam.record_result(2.3)
        math.add_exam(math_exam)
        
        # Module 2: Open/Planned
        physics = CourseModule("Physics", 5)
        physics_exam = WrittenExam(date(2025, 1, 15), 90)
        physics.add_exam(physics_exam)
        
        semester1.add_module(math)
        semester1.add_module(physics)
        self.program.add_semester(semester1)

    def tearDown(self):
        """Clean up the test file after each test."""
        if os.path.exists(self.test_filepath):
            os.remove(self.test_filepath)

    def test_save_and_load_roundtrip(self):
        """
        Tests the core functionality: saving a program and loading it back.
        The loaded object should be identical in content to the original.
        """
        # --- ACT 1: Save the program ---
        self.data_manager.save_program(self.program, self.test_filepath)
        
        # --- ASSERT 1: Check if the file was created ---
        self.assertTrue(os.path.exists(self.test_filepath))
        
        # --- ACT 2: Load the program back ---
        loaded_program = self.data_manager.load_program(self.test_filepath)
        
        # --- ASSERT 2: Check if the loaded object is valid and identical ---
        self.assertIsNotNone(loaded_program)
        self.assertIsInstance(loaded_program, DegreeProgram)
        
        # The most effective way to check for deep equality of nested objects
        # is to compare their dictionary representations.
        self.assertEqual(self.program.to_dict(), loaded_program.to_dict())

        # You can also add specific checks for deep attributes as a sanity check
        self.assertEqual(loaded_program.semesters[0].modules[0].name, "Mathematics")
        self.assertEqual(loaded_program.semesters[0].modules[0].exams[0].grade, 2.3)

    def test_load_nonexistent_file(self):
        """Tests that loading a non-existent file returns None without crashing."""
        loaded_program = self.data_manager.load_program("nonexistent_file.json")
        self.assertIsNone(loaded_program)

    def test_load_corrupt_file(self):
        """Tests that loading a corrupt/invalid JSON file returns None."""
        # Create a corrupt file
        with open(self.test_filepath, 'w') as f:
            f.write("{'invalid_json': True,}") # Invalid JSON syntax
        
        loaded_program = self.data_manager.load_program(self.test_filepath)
        self.assertIsNone(loaded_program)