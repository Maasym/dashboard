"""
Handles all user interface operations, including displaying data and
capturing user input in the console.
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Import the main data model class
from src.entities.program import DegreeProgram

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
            # Use the __str__ method of the program for a quick summary
            header = Text(str(program), justify="center")
            
            panel = Panel(header, title=title, border_style="green")
        
        self.console.print(panel)