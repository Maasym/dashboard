"""
Contains the main application controller that orchestrates the different services.
"""
from src.services.data_manager import DataManager
from src.services.ui_service import DashboardUI
from src.entities.program import DegreeProgram

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
            # CHANGE 3: Use self.program everywhere now
            self.ui.display_dashboard(self.program)
            choice = self.ui.display_main_menu()
            
            if choice == '1':
                self.ui.console.print("\nFunktion 'Neue Prüfungsleistung' noch nicht implementiert.", style="bold red")
            elif choice == '2':
                if self.program:
                    self.ui.display_module_table(self.program)
                else:
                    self.ui.console.print("\n[bold red]Fehler:[/bold red] Bitte zuerst einen Studiengang anlegen.",)
            elif choice == '3':
                self._create_new_program()
                self.program = self.data_manager.load_program(self.data_filepath)
            elif choice == '4':
                self.ui.console.print("\nProgramm wird beendet. Auf Wiedersehen!", style="bold blue")
                break
            else:
                self.ui.console.print(f"\n'[bold red]{choice}[/bold red]' ist keine gültige Option.")
            
            self.ui.console.input("\n[cyan]Drücke Enter, um fortzufahren...[/cyan]")
            self.ui.console.clear()

    def _create_new_program(self):
        """Handles the workflow for creating and saving a new degree program."""
        program_data = self.ui.get_new_program_data()
        
        # Create the new DegreeProgram instance
        self.program = DegreeProgram(
            name=program_data["name"],
            target_semesters=program_data["target_semesters"],
            target_grade=program_data["target_grade"]
        )
        
        # Save the new, empty program
        self.data_manager.save_program(self.program, self.data_filepath)
        self.ui.console.print("\n[bold green]✔ Studiengang wurde erfolgreich angelegt und gespeichert.[/bold green]")