import unittest
from src.entities.program import DegreeProgram
from src.entities.semester import AcademicSemester
from src.entities.module import CourseModule, ModuleStatus
from src.entities.exam import WrittenExam
from datetime import date

class TestDegreeProgram(unittest.TestCase):
    def setUp(self):
        self.program = DegreeProgram("Computer Science", 6, 2.0)
        self.semester1 = AcademicSemester(1)
        
        self.math = CourseModule("Mathematics", 10)
        math_exam = WrittenExam(date(2023,12,15), 90)
        math_exam.record_result(2.3)
        self.math.add_exam(math_exam)
        
        self.physics = CourseModule("Physics", 5)
        physics_exam = WrittenExam(date(2023,11,10), 90)
        physics_exam.record_result(4.7)
        self.physics.add_exam(physics_exam)
        
        self.semester1.add_module(self.math)
        self.semester1.add_module(self.physics)
        self.program.add_semester(self.semester1)
    
    def test_average_grade_calculation(self):
        avg = self.program.calculate_average_grade()
        self.assertEqual(avg, 2.3)
        
        physics_exam = self.physics.exams[0]
        physics_exam.record_result(1.7)
        
        # Die manuelle Aktualisierung wird hier absichtlich weggelassen,
        # um das Problem des veralteten Modul-Status aufzuzeigen.
        # self.physics.update_status() 
        
        avg = self.program.calculate_average_grade()
        expected = (2.3*10 + 1.7*5) / 15
        self.assertEqual(avg, round(expected, 2))
    
    def test_risk_modules(self):
        # Dieser Test benötigt keine Status-Änderung und sollte weiterhin funktionieren
        risk_modules = self.program.identify_risk_modules()
        self.assertEqual(len(risk_modules), 1)
        self.assertEqual(risk_modules[0].name, "Physics")
        self.assertEqual(risk_modules[0].status, ModuleStatus.RETRY)
    
    def test_progress_calculation(self):
        # Dieser Test benötigt keine Status-Änderung und sollte weiterhin funktionieren
        progress = self.program.calculate_progress()
        self.assertAlmostEqual(progress, (10/180)*100, delta=0.01)

if __name__ == '__main__':
    unittest.main()