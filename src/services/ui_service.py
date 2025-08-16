"""
Handles all user interface operations, including displaying data and
capturing user input in the console.
"""
from datetime import date
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Import entity classes and validation helpers
from src.entities.exam import ExamStatus
from src.entities.program import DegreeProgram
from src.utils.validation import get_validated_input
from src.entities.module import CourseModule, ModuleStatus

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
        self.console.print("  [5] Analyse")
        self.console.print("  [6] Beenden")
        
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
    
    def display_analysis(self, program: DegreeProgram, trend: str, grad_date: date, risk_modules: List[CourseModule]):
        # Main analysis panel
        self.console.print(Panel("[bold]ANALYSE DES STUDIENVERLAUFS[/bold]", style="blue"))
        
        # Progress Summary section
        summary_table = Table(show_header=False, box=None, padding=(0, 2))
        summary_table.add_column(style="bold", justify="right")
        summary_table.add_column(style="")
        
        # Get progress data for visualization
        all_modules = program.get_all_modules()
        total_credits = sum(m.credits for m in all_modules)
        earned_credits = sum(m.credits for m in all_modules if m.status == ModuleStatus.PASSED)
        completion = earned_credits / total_credits if total_credits > 0 else 0
        
        semesters_used = max(1, program.current_semester() - 1)
        expected_completion = semesters_used / program.target_semesters
        
        # Create visual progress bar
        bar_length = 30
        actual_pos = min(int(completion * bar_length), bar_length)
        expected_pos = min(int(expected_completion * bar_length), bar_length)
        
        progress_bar = ""
        for i in range(bar_length):
            if i < actual_pos:
                progress_bar += "█"  # Completed portion
            elif i == actual_pos and actual_pos < expected_pos:
                progress_bar += "▌"  # Current position marker
            elif i == expected_pos:
                progress_bar += "│"  # Expected position marker
            else:
                progress_bar += " "  # Not yet completed
        
        # Add labels to the progress bar
        progress_bar += "\n"
        progress_bar += " " * actual_pos + "▲" + " " * max(0, expected_pos - actual_pos - 1)
        progress_bar += "\n"
        progress_bar += " " * actual_pos + f"Aktuell ({earned_credits}/{total_credits} ECTS)"
        progress_bar += " " * max(0, expected_pos - actual_pos - 15) + f"│ Erwartet (Semester {semesters_used}/{program.target_semesters})"
        
        # Add to summary
        summary_table.add_row("ECTS-Verlauf:", progress_bar)
        summary_table.add_row("Vorauss. Abschluss:", grad_date.strftime('%d.%m.%Y'))
        summary_table.add_row("Status:", f"{trend}")
        
        self.console.print(summary_table)
        
        # Risk Modules section
        self.console.print("\n[bold]RISIKOMODULE[/bold]")
        if risk_modules:
            risk_table = Table(show_header=True, header_style="bold")
            risk_table.add_column("Modul", style="cyan")
            risk_table.add_column("Status", style="bold")
            risk_table.add_column("Semester", justify="center")
            risk_table.add_column("Problem", style="red")
            
            for module in risk_modules:
                # Determine problem description
                if module.status == ModuleStatus.FAILED:
                    problem = "Nicht bestanden"
                elif module.status == ModuleStatus.PLANNED and module.planned_semester < program.current_semester():
                    problem = "Nicht begonnen (überfällig)"
                else:  # IN_PROGRESS with multiple fails
                    problem = f"{sum(1 for e in module.exams if e.status == ExamStatus.FAILED)}x nicht bestanden"
                
                risk_table.add_row(
                    module.name,
                    module.status.name,
                    str(module.planned_semester),
                    problem
                )
            self.console.print(risk_table)
        else:
            self.console.print("[green]Keine Risikomodule identifiziert[/green]")