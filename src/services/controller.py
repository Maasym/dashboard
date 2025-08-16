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