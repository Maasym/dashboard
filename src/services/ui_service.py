"""
Handles all user interface operations, including displaying data and
capturing user input in the console.
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Import the main data model class
from src.entities.program import DegreeProgram
# CHANGE: Import the new helper function from your utils package
from src.utils.validation import get_validated_input

class DashboardUI:
    """Manages all console output and user interaction."""

    def __init__(self):
        """Initializes the UI with a rich Console object."""
        self.console = Console()

    def display_dashboard(self, program: DegreeProgram | None):
        """
        Displays the main dashboard view with key performance indicators.

        Args:
            program (DegreeProgram | None): The main program object. If None,
                                            shows a welcome message for a new user.
        """
        title = "Studien-Dashboard"
        
        if program is None:
            content = Text("Willkommen! Es sind noch keine Studiendaten vorhanden.\n"
                         "Bitte legen Sie einen neuen Studiengang an.", justify="center")
            panel = Panel(content, title=title, border_style="blue")
        else:
            header = Text(str(program), justify="center")
            panel = Panel(header, title=title, border_style="green")
        
        self.console.print(panel)

    def display_main_menu(self) -> str:
        """
        Displays the main menu and prompts the user for input.

        Returns:
            str: The user's choice.
        """
        self.console.print("\n[bold]Hauptmenü:[/bold]")
        self.console.print("  [1] Neue Prüfungsleistung eintragen")
        self.console.print("  [2] Module anzeigen")
        self.console.print("  [3] Studiengang anlegen/überschreiben")
        self.console.print("  [4] Beenden")
        
        choice = self.console.input("\nBitte wähle eine Option: ")
        return choice
    
    def get_new_program_data(self) -> dict:
        """
        Prompts the user to enter data for a new degree program using validation.

        Returns:
            dict: A dictionary containing the new program's data.
        """
        self.console.print("\n[bold blue]Neuen Studiengang anlegen[/bold blue]")
        
        # String input does not need type validation
        name = self.console.input("Name des Studiengangs (z.B. Computer Science): ")
        
        # CHANGE: Use the helper function for validated integer and float input
        target_semesters = get_validated_input("Geplante Semesteranzahl (z.B. 6): ", int)
        target_grade = get_validated_input("Ziel-Notendurchschnitt (z.B. 2.0): ", float)
        
        return {
            "name": name,
            "target_semesters": target_semesters,
            "target_grade": target_grade
        }
    
    def display_module_table(self, program: DegreeProgram):
        """
        Displays a table of all modules in the degree program.

        Args:
            program (DegreeProgram): The main program object containing the modules.
        """
        table = Table(title="Modulübersicht", border_style="blue", show_header=True, header_style="bold magenta")
        
        # Define the columns for the table
        table.add_column("Modulname", style="cyan", no_wrap=True)
        table.add_column("ECTS", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Beste Note", justify="right", style="green")

        if not program.semesters:
            self.console.print("[yellow]Es sind noch keine Semester oder Module vorhanden.[/yellow]")
            return
            
        # Populate the table with data from the program object
        for semester in program.semesters:
            table.add_section() # Adds a separator line for each semester
            for module in semester.modules:
                grade = module.best_exam_grade()
                # Format the grade nicely, display "-" if no grade is available
                grade_str = f"{grade:.1f}" if grade is not None else "-"
                
                table.add_row(
                    module.name,
                    str(module.credits),
                    module.status.name, # Use the name of the enum member
                    grade_str
                )
                
        self.console.print(table)