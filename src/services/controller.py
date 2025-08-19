"""
Contains the main application controller that orchestrates the different services.
"""
from src.services.progress_analyzer import ProgressAnalyzer
from src.services.data_manager import DataManager
from src.services.ui_service import DashboardUI
from src.entities.program import DegreeProgram
from src.entities.semester import Semester
from src.entities.module import CourseModule, ModuleStatus, MAX_ATTEMPTS
from src.entities.exam import WrittenExam, Portfolio, CaseStudyExam, OralExam
from src.utils.validation import get_validated_input
from datetime import date

class AppController:
    """
    Main application controller that orchestrates all services and user interactions.
    
    This class serves as the central coordinator for the academic dashboard application,
    managing the flow between user interface, data persistence, and business logic.
    It implements the main application loop and handles all user menu selections.
    """

    def __init__(self):
        """
        Initialize the controller and its dependent services.
        
        Sets up the data manager for persistence, UI service for user interaction,
        and defines the default data storage location.
        """
        # Service dependencies for separation of concerns
        self.data_manager = DataManager()  # Handles data persistence
        self.ui = DashboardUI()           # Manages user interface
        
        # Application configuration
        self.data_filepath = "data/studienverlauf.json"  # Default data storage location
        
        # Current program state (loaded from file or created new)
        self.program: DegreeProgram | None = None

    def run(self):
        """
        Start the main application loop and handle user interactions.
        
        This method implements the core application workflow:
        1. Load existing program data from storage
        2. Display the dashboard with current program status
        3. Present menu options and process user selections
        4. Continue until user chooses to exit
        
        The loop ensures proper state management and user experience flow.
        """
        # Load existing program data or start with None if no data exists
        self.program = self.data_manager.load_program(self.data_filepath)
    
        # Main application loop - continues until user exits
        while True:
            # Display current program status and statistics
            self.ui.display_dashboard(self.program)
            
            # Show menu options and get user selection
            choice = self.ui.display_main_menu()
            
            # Process user choice and delegate to appropriate handler
            if choice == '1':
                self._add_new_module()
            elif choice == '2':
                self._add_new_exam()
            elif choice == '3':
                # Module overview requires existing program data
                if self.program:
                    self.ui.display_module_table(self.program)
                else:
                    self.ui.console.print("\n[bold red]Fehler:[/bold red] Bitte zuerst einen Studiengang anlegen.")
            elif choice == '4':
                self._show_analysis()
            elif choice == '5':
                # Create new program and reload from storage
                self._create_new_program()
                self.program = self.data_manager.load_program(self.data_filepath)
            elif choice == '6':
                # Graceful application exit
                self.ui.console.print("\nProgramm wird beendet. Auf Wiedersehen!", style="bold blue")
                break
            else:
                # Handle invalid menu selections
                self.ui.console.print(f"\n'[bold red]{choice}[/bold red]' ist keine gültige Option.")
            
            # Pause for user acknowledgment before continuing to next iteration
            self.ui.console.input("\n[cyan]Drücke Enter, um fortzufahren...[/cyan]")
            self.ui.console.clear()  # Clear screen for clean next iteration

    def _create_new_program(self):
        """
        Handle the complete workflow for creating and saving a new degree program.
        
        This method orchestrates the process of:
        1. Collecting program information from the user via UI
        2. Creating a new DegreeProgram entity with validation
        3. Persisting the program to storage
        4. Providing user feedback on successful creation
        
        Note: This will overwrite any existing program data.
        """
        # Collect program details from user through UI service
        program_data = self.ui.get_new_program_data()
        
        # Create new program entity with validation (constructor validates inputs)
        self.program = DegreeProgram(
            name=program_data["name"],
            target_semesters=program_data["target_semesters"],
            target_grade=program_data["target_grade"]
        )
        
        # Persist the new program to storage
        self.data_manager.save_program(self.program, self.data_filepath)
        
        # Provide success feedback to user
        self.ui.console.print("\n[bold green]✔ Studiengang wurde erfolgreich angelegt und gespeichert.[/bold green]")
        
    def _add_new_module(self):
        """
        Handle the complete workflow for adding a new module to a semester.
        
        This method manages the process of:
        1. Validating that a program exists
        2. Collecting module information from the user
        3. Finding or creating the target semester
        4. Creating and adding the new module
        5. Persisting changes and providing feedback
        
        The method automatically creates semesters if they don't exist and
        maintains semester ordering within the program.
        """
        # Ensure a program exists before allowing module creation
        if not self.program:
            self.ui.console.print("\n[bold red]Fehler:[/bold red] Bitte zuerst einen Studiengang anlegen.")
            return

        # Collect module details from user through UI service
        module_data = self.ui.get_new_module_data()
        semester_num = module_data["semester_num"]

        # Find existing semester or prepare to create a new one
        target_semester = next((s for s in self.program.semesters if s.number == semester_num), None)
        
        # Create semester if it doesn't exist
        if not target_semester:
            target_semester = Semester(number=semester_num)
            self.program.add_semester(target_semester)
            # Maintain chronological order of semesters
            self.program.semesters.sort(key=lambda s: s.number)

        # Create new module entity with validation
        new_module = CourseModule(
            name=module_data["name"], 
            credits=module_data["credits"], 
            planned_semester=semester_num
        )
        
        # Add module to the target semester
        target_semester.add_module(new_module)
        
        # Persist changes to storage
        self.data_manager.save_program(self.program, self.data_filepath)
        
        # Provide success feedback to user
        self.ui.console.print(f"\n[bold green]✔ Modul '{new_module.name}' wurde zu Semester {semester_num} hinzugefügt.[/bold green]")

    def _add_new_exam(self):
        """
        Handle the complete workflow for adding a new exam to an existing module.
        
        This method manages a complex process involving:
        1. Validating prerequisites (program and modules exist)
        2. Filtering modules that are eligible for new exams
        3. Presenting module selection to the user
        4. Collecting exam type and details
        5. Recording the exam result and updating module status
        6. Persisting changes and providing feedback
        
        Only modules that haven't been passed and still have attempts remaining
        are eligible for new exams.
        """
        # Validate that program exists and has modules before proceeding
        if not self.program or not self.program.get_all_modules():
            self.ui.console.print("\n[bold red]Fehler:[/bold red] Bitte zuerst einen Studiengang mit Modulen anlegen.")
            return

        # Filter modules that are eligible for new exam attempts
        # Exclude: already passed modules and modules with no attempts left
        eligible_modules = [
            m for m in self.program.get_all_modules()
            if m.status != ModuleStatus.PASSED and m.status != ModuleStatus.NO_MORE_ATTEMPTS
        ]
        
        # Check if any modules are eligible for new exams
        if not eligible_modules:
            self.ui.console.print("\n[bold yellow]Keine Module verfügbar:[/bold yellow]")
            self.ui.console.print("- Alle Module sind bestanden oder haben keine Versuche mehr")
            self.ui.console.print("- Fügen Sie zuerst neue Module hinzu")
            return

        # Present eligible modules to user with status indicators
        self.ui.console.print("\n[bold]Modulauswahl für Prüfungsleistung[/bold]")
        for idx, module in enumerate(eligible_modules, start=1):
            # Add warning icon for failed modules to draw attention
            status_icon = ""
            if module.status == ModuleStatus.FAILED:
                status_icon = "[yellow]⚠[/yellow] "
            self.ui.console.print(f"[{idx}] {status_icon}{module.name} (Status: {module.status.name}, Verbleibende Versuche: {module.remaining_attempts()})")

        # Get user's module selection with validation
        choice = get_validated_input("Zu welchem Modul soll die Prüfungsleistung hinzugefügt werden? ", int)
        if choice < 1 or choice > len(eligible_modules):
            self.ui.console.print("\n[bold red]Ungültige Auswahl.[/bold red]")
            return

        # Get the selected module for exam addition
        selected_module = eligible_modules[choice - 1]
        
        # Present exam type options to the user
        self.ui.console.print("\nPrüfungsart auswählen:")
        self.ui.console.print("[1] Schriftliche Prüfung")
        self.ui.console.print("[2] Portfolio")
        self.ui.console.print("[3] Fallstudie")
        self.ui.console.print("[4] Mündliche Prüfung")
        exam_type_choice = get_validated_input("Deine Wahl: ", int)

        # Create appropriate exam object based on user selection
        # All exams use today's date as the exam date
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

        # Collect and record the exam grade with validation
        grade = get_validated_input("Note der Prüfungsleistung: ", float)
        try:
            # Record the result, which automatically updates exam status
            exam.record_result(grade)
        except Exception as e:
            # Handle validation errors from grade recording
            self.ui.console.print(f"[bold red]Fehler:[/bold red] {e}")
            return

        # Add the completed exam to the selected module
        selected_module.add_exam(exam)
        
        # Persist all changes to storage
        self.data_manager.save_program(self.program, self.data_filepath)
        
        # Provide success feedback and show remaining attempts
        self.ui.console.print(f"\n[bold green]✔ Prüfungsleistung für Modul '{selected_module.name}' hinzugefügt.[/bold green]")
        self.ui.console.print(f"[yellow]Verbleibende Versuche: {selected_module.remaining_attempts()}/{MAX_ATTEMPTS}[/yellow]")
    
    def _show_analysis(self):
        """
        Generate and display comprehensive academic progress analysis.
        
        This method orchestrates the analysis workflow by:
        1. Validating that program data exists
        2. Creating a ProgressAnalyzer instance
        3. Calculating various progress metrics and predictions
        4. Identifying at-risk modules and critical failures
        5. Delegating display to the UI service
        
        The analysis includes ECTS trends, graduation predictions, and risk assessment.
        """
        # Ensure program exists before attempting analysis
        if not self.program:
            self.ui.console.print("\n[bold red]Fehler:[/bold red] Bitte zuerst einen Studiengang mit Modulen anlegen.")
            return
        
        # Create analyzer instance for the current program
        analyzer = ProgressAnalyzer(self.program)
        
        # Calculate ECTS accumulation trend (on track, behind, etc.)
        trend = analyzer.calculate_ects_trend()
        
        # Predict graduation date based on current progress
        grad_date = analyzer.predict_graduation()
        
        # Identify modules that require attention (failed, overdue, low attempts)
        risk_modules = analyzer.identify_risk_modules()
        
        # Get modules that permanently prevent degree completion
        critical_failures = self.program.get_critical_failures()
        
        # Delegate display formatting to the UI service
        self.ui.display_analysis(self.program, trend, grad_date, risk_modules, critical_failures)