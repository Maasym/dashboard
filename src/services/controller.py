"""
Contains the main application controller that orchestrates the different services.
"""
from src.services.data_manager import DataManager
from src.services.ui_service import DashboardUI

class AppController:
    """The main application controller."""

    def __init__(self):
        """Initializes the controller and its components."""
        self.data_manager = DataManager()
        self.ui = DashboardUI()
        self.data_filepath = "data/studienverlauf.json" # Central place for the filepath

    def run(self):
        """Starts the main application flow."""
        # 1. Load data
        program = self.data_manager.load_program(self.data_filepath)
        
        # 2. Display the main dashboard
        self.ui.display_dashboard(program)
    
    def run(self):
        """Starts the main application loop."""
        program = self.data_manager.load_program(self.data_filepath)
        
        while True:
            self.ui.display_dashboard(program)
            choice = self.ui.display_main_menu()
            
            if choice == '1':
                self.ui.console.print("\nFunktion 'Neue Prüfungsleistung' noch nicht implementiert.", style="bold red")
            elif choice == '2':
                self.ui.console.print("\nFunktion 'Module anzeigen' noch nicht implementiert.", style="bold red")
            elif choice == '3':
                self.ui.console.print("\nFunktion 'Studiengang anlegen' noch nicht implementiert.", style="bold red")
            elif choice == '4':
                self.ui.console.print("\nProgramm wird beendet. Auf Wiedersehen!", style="bold blue")
                break
            else:
                self.ui.console.print(f"\n'[bold red]{choice}[/bold red]' ist keine gültige Option.")
            
            self.ui.console.input("\n[cyan]Drücke Enter, um fortzufahren...[/cyan]")
            self.ui.console.clear()
