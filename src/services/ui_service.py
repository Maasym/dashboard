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
from rich.progress import Progress, BarColumn, TextColumn

# Import entity classes and validation helpers
from src.entities.exam import ExamStatus
from src.entities.program import DegreeProgram
from src.utils.validation import get_validated_input
from src.entities.module import CourseModule, ModuleStatus, MAX_ATTEMPTS

class DashboardUI:
    """
    User interface service managing all console interactions and display formatting.
    
    This class handles the presentation layer of the academic dashboard application,
    using the Rich library to create colorful, formatted console output. It provides
    methods for displaying complex data structures, collecting user input, and
    presenting analysis results in a user-friendly format.
    """

    def __init__(self):
        """
        Initialize the UI service with a Rich Console for enhanced formatting.
        
        The Rich Console enables colored text, tables, progress bars, and other
        visual enhancements that improve the user experience.
        """
        self.console = Console()

    def display_dashboard(self, program: DegreeProgram | None):
        """
        Display the main dashboard with key performance indicators and progress.
        
        This method creates the primary interface view that users see, showing:
        - Program name and basic information
        - Current semester and target grade
        - Credit progress with visual progress bar
        - Critical warnings for failed modules
        - Overall degree completion status
        
        The display adapts based on whether program data exists and includes
        appropriate warnings for critical situations.
        
        Args:
            program: The current degree program, or None if no data exists
        """
        title = "Studien-Dashboard"

        # Handle case where no program data exists yet
        if program is None:
            content = Text(
                "Willkommen! Es sind noch keine Studiendaten vorhanden.\n"
                "Bitte legen Sie einen neuen Studiengang an.",
                justify="center"
            )
            panel = Panel(content, title=title, border_style="blue", expand=False)
        else:
            # Collect key metrics and statistics for display
            current_sem = program.current_semester()
            avg_grade = program.get_average_grade()
            all_modules = program.get_all_modules()
            total_credits = sum(module.credits for module in all_modules)
            achieved_credits = sum(module.credits for module in all_modules if module.is_passed())
            critical_failures = program.get_critical_failures()
            is_completable = program.is_completable()
            
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
            
            # Critical failures warning
            if critical_failures:
                warning_text = Text.from_markup(
                "[bold red]KRITISCHER FEHLER:[/bold red] "
                "Studium kann nicht abgeschlossen werden!\n"
            )
                content.append("\n")    
                content.append(warning_text)

                for module in critical_failures:
                    content.append(f" - {module.name} (3x nicht bestanden)\n", style="red")
            
            # Degree completion status
            status_style = "red" if not is_completable else "green"
            status_text = "NICHT ABSCHLIESSBAR" if not is_completable else "ABSCHLIESSBAR"
            content.append("\nStudienabschluss: ")
            content.append(status_text + "\n", style=f"bold {status_style}")

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
            panel_border_style = "red" if critical_failures else "green"
            panel = Panel(
                content,
                title=title,
                border_style=panel_border_style,
                width=60,
                expand=False
            )

        self.console.print(panel)

    def display_main_menu(self) -> str:
        """
        Display the main menu options and collect user selection.
        
        This method presents the primary navigation menu with all available
        application functions and waits for user input.
        
        Returns:
            str: The user's menu choice as a string
        """
        self.console.print("\n[bold]Hauptmenü:[/bold]")
        self.console.print("  [1] Neues Modul hinzufügen")
        self.console.print("  [2] Neue Prüfungsleistung eintragen")
        self.console.print("  [3] Modulübersicht anzeigen")
        self.console.print("  [4] Analyse")
        self.console.print("  [5] Studiengang anlegen/überschreiben")
        self.console.print("  [6] Beenden")
        
        choice = self.console.input("\nBitte wähle eine Option: ")
        return choice
    
    def get_new_program_data(self) -> dict:
        """
        Collect degree program information from the user with validation.
        
        This method guides the user through entering all required information
        for creating a new degree program, including input validation to ensure
        data integrity.
        
        Returns:
            dict: Dictionary containing program name, target semesters, and target grade
        """
        self.console.print("\n[bold blue]Neuen Studiengang anlegen[/bold blue]")
        
        # Collect basic program information with examples
        name = self.console.input("Name des Studiengangs (z.B. Computer Science): ")
        target_semesters = get_validated_input("Geplante Semesteranzahl (z.B. 6): ", int)
        target_grade = get_validated_input("Ziel-Notendurchschnitt (z.B. 2.0): ", float)
        
        return {
            "name": name,
            "target_semesters": target_semesters,
            "target_grade": target_grade
        }

    def get_new_module_data(self) -> dict:
        """
        Collect module information from the user with validation.
        
        This method guides the user through entering all required information
        for adding a new module to the degree program.
        
        Returns:
            dict: Dictionary containing module name, credits, and semester assignment
        """
        self.console.print("\n[bold blue]Neues Modul hinzufügen[/bold blue]")
        
        # Collect module details with validation
        name = self.console.input("Name des Moduls: ")
        credits = get_validated_input("Anzahl ECTS-Punkte: ", int)
        semester_num = get_validated_input("Zu welchem Semester hinzufügen (z.B. 1): ", int)
        
        return {"name": name, "credits": credits, "semester_num": semester_num}

    def display_module_table(self, program: DegreeProgram):
        """
        Display a comprehensive table showing all modules in the degree program.
        
        This method creates a formatted table with columns for semester, module name,
        ECTS credits, status, attempt counts, and best grades. The table provides
        a complete overview of academic progress across all semesters.
        
        Args:
            program: The degree program containing modules to display
        """
        # Create table with appropriate columns and styling
        table = Table(title="Modulübersicht", border_style="blue", show_header=True, header_style="bold magenta")
        
        table.add_column("Semester", justify="center")
        table.add_column("Modulname", style="cyan", no_wrap=True)
        table.add_column("ECTS", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Versuche", justify="center")
        table.add_column("Beste Note", justify="right", style="green")

        # Handle empty program case
        if not program.semesters:
            self.console.print("[yellow]Es sind noch keine Semester oder Module vorhanden.[/yellow]")
            return
        
        # Populate table with module data from all semesters
        for semester in program.semesters:
            for module in semester.modules:
                # Format grade display
                grade = module.best_grade()
                grade_str = f"{grade:.1f}" if grade is not None else "-"
                
                # Format attempt status with color coding for risk levels
                if module.status == ModuleStatus.NO_MORE_ATTEMPTS:
                    attempts = f"[red]{len(module.exams)}/{MAX_ATTEMPTS}[/red]"  # Critical
                elif module.remaining_attempts() < MAX_ATTEMPTS:
                    attempts = f"[yellow]{len(module.exams)}/{MAX_ATTEMPTS}[/yellow]"  # Warning
                else:
                    attempts = f"{len(module.exams)}/{MAX_ATTEMPTS}"  # Normal
                
                # Add row with all module information
                table.add_row(
                    str(semester.number),
                    module.name,
                    str(module.credits),
                    module.status.name,
                    attempts,
                    grade_str
                )
                
        self.console.print(table)
    
    def display_analysis(self, program: DegreeProgram, trend: str, grad_date: date, 
                        risk_modules: List[CourseModule], critical_failures: List[CourseModule]):
        """
        Display comprehensive academic progress analysis with visualizations.
        
        This method presents a detailed analysis including:
        - Critical failure warnings and impact assessment
        - Progress summary with visual progress bars
        - ECTS trends and graduation predictions
        - Risk module identification and recommendations
        
        The display uses color coding and visual elements to highlight
        important information and guide user attention to critical issues.
        
        Args:
            program: The degree program being analyzed
            trend: ECTS accumulation trend description
            grad_date: Predicted graduation date (or None if impossible)
            risk_modules: List of modules requiring attention
            critical_failures: List of permanently failed modules
        """
        # Use red borders for critical situations, blue for normal analysis
        border_style = "red" if critical_failures else "blue"
        self.console.print(Panel("[bold]ANALYSE DES STUDIENVERLAUFS[/bold]", style=border_style))
        
        # === Critical Failures Section ===
        # Show permanent failures that prevent degree completion
        if critical_failures:
            self.console.print("\n[bold red on white] KRITISCHE FEHLER [/bold red on white]")
            self.console.print("Ihr Studium kann nicht abgeschlossen werden, da folgende Module\n"
                            "definitiv nicht bestanden wurden (3 Versuche gescheitert):", style="bold red")
            
            crit_table = Table(show_header=True, header_style="bold red")
            crit_table.add_column("Modul", style="red")
            crit_table.add_column("ECTS", justify="center")
            crit_table.add_column("Semester", justify="center")
            
            for module in critical_failures:
                crit_table.add_row(
                    module.name,
                    str(module.credits),
                    str(module.planned_semester)
                )
            
            self.console.print(crit_table)
            self.console.print("\n[bold]Mögliche Lösungen:[/bold]")
            self.console.print("- Studiengang wechseln")
            self.console.print("- Studienabbruch erwägen")
            self.console.print("- Mit Studienberatung sprechen")
        
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
        summary_table.add_row("Status:", f"{trend}")
        if grad_date:
            summary_table.add_row("Vorauss. Abschluss:", grad_date.strftime('%d.%m.%Y'))
        else:
            summary_table.add_row("Vorauss. Abschluss:", "[red]Nicht möglich[/red]")
        
        self.console.print(summary_table)
        
        # Risk Modules section (only if there are any non-critical risk modules)
        non_critical_risk = [m for m in risk_modules if m not in critical_failures]
        if non_critical_risk:
            self.console.print("\n[bold]RISIKOMODULE[/bold]")
            risk_table = Table(show_header=True, header_style="bold")
            risk_table.add_column("Modul", style="cyan")
            risk_table.add_column("Status", style="bold")
            risk_table.add_column("Sem", justify="center")
            risk_table.add_column("Versuche", justify="center")
            risk_table.add_column("Problem", style="red")
            
            for module in non_critical_risk:
                # Format attempts
                attempts = f"{len(module.exams)}/{MAX_ATTEMPTS}"
                
                # Determine problem
                if module.status == ModuleStatus.FAILED:
                    problem = f"Nicht bestanden ({module.remaining_attempts()} Versuch(e) übrig)"
                elif module.status == ModuleStatus.PLANNED and module.planned_semester < program.current_semester():
                    problem = "Nicht begonnen (überfällig)"
                else:
                    problem = f"Nur noch {module.remaining_attempts()} Versuch(e)"
                
                risk_table.add_row(
                    module.name,
                    module.status.name,
                    str(module.planned_semester),
                    attempts,
                    problem
                )
            self.console.print(risk_table)
        elif risk_modules:  # only critical failures were shown
            pass
        else:
            self.console.print("\n[green]Keine weiteren Risikomodule identifiziert[/green]")