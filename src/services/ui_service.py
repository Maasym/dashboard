"""
Handles all user interface operations, including displaying data and
capturing user input in the console.
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Import entity classes and validation helpers
from src.entities.program import DegreeProgram
from src.utils.validation import get_validated_input
from src.entities.module import ModuleStatus

class DashboardUI:
    """Manages all console output and user interaction."""

    def __init__(self):
        """Initializes the UI with a rich Console object."""
        self.console = Console()

    def display_dashboard(self, program: DegreeProgram | None):
        """
        Displays a compact main dashboard view with key performance indicators.
        Shows only high-level stats and a credit progress bar.
        """
        from rich.progress import Progress, BarColumn, TextColumn

        title = "Studien-Dashboard"

        if program is None:
            content = Text(
                "Willkommen! Es sind noch keine Studiendaten vorhanden.\n"
                "Bitte legen Sie einen neuen Studiengang an.",
                justify="center"
            )
            panel = Panel(content, title=title, border_style="blue", expand=False)
        else:
            # Gather program statistics
            current_sem = program.current_semester()
            avg_grade = program.get_average_grade()
            all_modules = program.get_all_modules()
            total_credits = sum(module.credits for module in all_modules)
            achieved_credits = sum(module.credits for module in all_modules if module.is_passed())
            credit_ratio = achieved_credits / total_credits if total_credits > 0 else 0

            # Build text with KPI info
            content = Text(justify="left")
            content.append("Studiengang: ", style="bold")
            content.append(f"{program.name}\n", style="green")
            content.append("Aktuelles Semester: ")
            content.append(f"{current_sem}\n", style="cyan")
            content.append("Ziel-Notendurchschnitt: ")
            content.append(f"{program.target_grade}\n", style="magenta")
            content.append("Aktueller Durchschnitt: ")
            content.append(f"{avg_grade if avg_grade is not None else '-'}\n", style="yellow")
            content.append("Erreichte Credits: ")
            content.append(f"{achieved_credits} / {total_credits}\n", style="green")

            # Add a simple horizontal progress bar for credits
            progress_bar = Progress(
                "{task.description}",
                BarColumn(bar_width=30),
                TextColumn("{task.percentage:>3.0f}%"),
                expand=False,
                console=self.console
            )
            task_id = progress_bar.add_task("Fortschritt:", total=total_credits, completed=achieved_credits)
            with progress_bar:
                progress_bar.refresh()  # render bar once

            # Wrap the text and bar in a panel
            panel = Panel(
                content,
                title=title,
                border_style="green",
                width=60,
                expand=False
            )

        self.console.print(panel)

    def display_main_menu(self) -> str:
        """
        Displays the main menu and prompts the user for input.
        """
        self.console.print("\n[bold]Hauptmenü:[/bold]")
        self.console.print("  [1] Neues Modul hinzufügen")
        self.console.print("  [2] Neue Prüfungsleistung eintragen")
        self.console.print("  [3] Modulübersicht anzeigen")
        self.console.print("  [4] Studiengang anlegen/überschreiben")
        self.console.print("  [5] Beenden")
        
        choice = self.console.input("\nBitte wähle eine Option: ")
        return choice
    
    def get_new_program_data(self) -> dict:
        """
        Prompts the user to enter data for a new degree program using validation.
        """
        self.console.print("\n[bold blue]Neuen Studiengang anlegen[/bold blue]")
        name = self.console.input("Name des Studiengangs (z.B. Computer Science): ")
        target_semesters = get_validated_input("Geplante Semesteranzahl (z.B. 6): ", int)
        target_grade = get_validated_input("Ziel-Notendurchschnitt (z.B. 2.0): ", float)
        
        return {
            "name": name,
            "target_semesters": target_semesters,
            "target_grade": target_grade
        }

    def get_new_module_data(self) -> dict:
        """Prompts for and validates data for a new module."""
        self.console.print("\n[bold blue]Neues Modul hinzufügen[/bold blue]")
        name = self.console.input("Name des Moduls: ")
        credits = get_validated_input("Anzahl ECTS-Punkte: ", int)
        semester_num = get_validated_input("Zu welchem Semester hinzufügen (z.B. 1): ", int)
        return {"name": name, "credits": credits, "semester_num": semester_num}

    def display_module_table(self, program: DegreeProgram):
        """
        Displays a table of all modules in the degree program.
        """
        table = Table(title="Modulübersicht", border_style="blue", show_header=True, header_style="bold magenta")
        
        table.add_column("Semester", justify="center")
        table.add_column("Modulname", style="cyan", no_wrap=True)
        table.add_column("ECTS", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Beste Note", justify="right", style="green")

        if not program.semesters:
            self.console.print("[yellow]Es sind noch keine Semester oder Module vorhanden.[/yellow]")
            return
            
        for semester in program.semesters:
            table.add_section()
            for module in semester.modules:
                grade = module.best_grade()
                grade_str = f"{grade:.1f}" if grade is not None else "-"
                
                table.add_row(
                    str(semester.number),
                    module.name,
                    str(module.credits),
                    module.status.name,
                    grade_str
                )
                
        self.console.print(table)