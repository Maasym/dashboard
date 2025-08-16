"""
Main entry point for the Dashboard application.
"""
from src.services.controller import AppController

if __name__ == "__main__":
    app = AppController()
    app.run()