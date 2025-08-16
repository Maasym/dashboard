"""
Contains the main application controller that orchestrates the different services.
"""
from src.services.progress_analyzer import ProgressAnalyzer
from src.services.data_manager import DataManager
from src.services.ui_service import DashboardUI
from src.entities.program import DegreeProgram
from src.entities.semester import Semester
from src.entities.module import CourseModule
from src.entities.exam import WrittenExam, Portfolio, CaseStudyExam, OralExam
from src.utils.validation import get_validated_input
from datetime import date

class AppController:
    """The main application controller."""

    def __init__(self):
        """Initializes the controller and its components."""
        self.data_manager = DataManager()
        self.ui = DashboardUI()
        self.data_filepath = "data/studienverlauf.json"
        self.program: DegreeProgram | None = None

    def run(self):
        """Starts the main application loop."""
        self.program = self.data_manager.load_program(self.data_filepath)
    
        while True:
            self.ui.display_dashboard(self.program)
            choice = self.ui.display_main_menu()
            
            if choice == '1':
                self._add_new_module()
            elif choice == '2':
                self._add_new_exam()
            elif choice == '3':
                if self.program:
                    self.ui.display_module_table(self.program)
                else:
                    self.ui.console.print("\n[bold red]Fehler:[/bold red] Bitte zuerst einen Studiengang anlegen.")
            elif choice == '4':
                self._create_new_program()
                self.program = self.data_manager.load_program(self.data_filepath)
            elif choice == '5':
                self._show_analysis()
            elif choice == '6':
                self.ui.console.print("\nProgramm wird beendet. Auf Wiedersehen!", style="bold blue")
                break
            else:
                self.ui.console.print(f"\n'[bold red]{choice}[/bold red]' ist keine gültige Option.")
            
            self.ui.console.input("\n[cyan]Drücke Enter, um fortzufahren...[/cyan]")
            self.ui.console.clear()

    def _create_new_program(self):
        """Handles the workflow for creating and saving a new degree program."""
        program_data = self.ui.get_new_program_data()
        
        self.program = DegreeProgram(
            name=program_data["name"],
            target_semesters=program_data["target_semesters"],
            target_grade=program_data["target_grade"]
        )
        
        self.data_manager.save_program(self.program, self.data_filepath)
        self.ui.console.print("\n[bold green]✔ Studiengang wurde erfolgreich angelegt und gespeichert.[/bold green]")
        
    def _add_new_module(self):
        """Handles the workflow for adding a new module to a semester."""
        if not self.program:
            self.ui.console.print("\n[bold red]Fehler:[/bold red] Bitte zuerst einen Studiengang anlegen.")
            return

        module_data = self.ui.get_new_module_data()
        semester_num = module_data["semester_num"]

        target_semester = next((s for s in self.program.semesters if s.number == semester_num), None)
        
        if not target_semester:
            target_semester = Semester(number=semester_num)
            self.program.add_semester(target_semester)
            self.program.semesters.sort(key=lambda s: s.number)

        new_module = CourseModule(
            name=module_data["name"], 
            credits=module_data["credits"], 
            planned_semester=semester_num
        )
        target_semester.add_module(new_module)
        
        self.data_manager.save_program(self.program, self.data_filepath)
        self.ui.console.print(f"\n[bold green]✔ Modul '{new_module.name}' wurde zu Semester {semester_num} hinzugefügt.[/bold green]")

    def _add_new_exam(self):
        """Handles adding a new exam (any type) to an existing module."""
        if not self.program or not self.program.get_all_modules():
            self.ui.console.print("\n[bold red]Fehler:[/bold red] Bitte zuerst einen Studiengang mit Modulen anlegen.")
            return

        # Show modules
        self.ui.console.print("\nModulauswahl für Prüfungsleistung")
        modules = self.program.get_all_modules()
        for idx, module in enumerate(modules, start=1):
            self.ui.console.print(f"[{idx}] {module.name} ({module.status.name})")

        choice = get_validated_input("Zu welchem Modul soll die Prüfungsleistung hinzugefügt werden? ", int)
        if choice < 1 or choice > len(modules):
            self.ui.console.print("\n[bold red]Ungültige Auswahl.[/bold red]")
            return

        selected_module = modules[choice - 1]

        # Choose exam type
        self.ui.console.print("\nPrüfungsart auswählen:")
        self.ui.console.print("[1] Schriftliche Prüfung")
        self.ui.console.print("[2] Portfolio")
        self.ui.console.print("[3] Fallstudie")
        self.ui.console.print("[4] Mündliche Prüfung")
        exam_type_choice = get_validated_input("Deine Wahl: ", int)

        # Create exam objects without extra metadata
        if exam_type_choice == 1:
            exam = WrittenExam(date.today())
        elif exam_type_choice == 2:
            exam = Portfolio(date.today())
        elif exam_type_choice == 3:
            exam = CaseStudyExam(date.today())
        elif exam_type_choice == 4:
            exam = OralExam(date.today())
        else:
            self.ui.console.print("\n[bold red]Ungültige Prüfungsart.[/bold red]")
            return

        # Record grade
        grade = get_validated_input("Note der Prüfungsleistung: ", float)
        try:
            exam.record_result(grade)
        except Exception as e:
            self.ui.console.print(f"[bold red]Fehler:[/bold red] {e}")
            return

        selected_module.add_exam(exam)
        self.data_manager.save_program(self.program, self.data_filepath)
        self.ui.console.print(f"\n[bold green] Prüfungsleistung für Modul '{selected_module.name}' hinzugefügt.[/bold green]")
    
    def _show_analysis(self):
        if not self.program:
            self.ui.console.print("\n[bold red]Error:[/bold red] Bitte zuerst Studiengang erstellen")
            return
        
        analyzer = ProgressAnalyzer(self.program)
        
        # ECTS Trend
        trend = analyzer.calculate_ects_trend()
        
        # Graduation Prediction
        grad_date = analyzer.predict_graduation()
        
        # Risk Modules
        risk_modules = analyzer.identify_risk_modules()
        
        # Display results
        self.ui.display_analysis(self.program, trend, grad_date, risk_modules)