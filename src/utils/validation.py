"""
Input validation utilities for the academic management dashboard.

This module provides type-safe input validation functions that ensure
user input meets expected data types and constraints. It uses generic
typing to maintain type safety while providing flexible validation
for different data types (int, float, etc.).
"""
from typing import Type, TypeVar
from rich.console import Console

# Generic type variable for maintaining type safety across different input types
T = TypeVar('T')  # Represents any type that can be validated (int, float, str, etc.)

# Rich console instance for formatted user interaction and error messages
console = Console()

def get_validated_input(prompt: str, target_type: Type[T]) -> T:
    """
    Prompt user for input with automatic type validation and conversion.
    
    This function implements a robust input validation pattern that:
    1. Displays a prompt to the user
    2. Attempts to convert the input to the specified type
    3. Re-prompts if conversion fails with a helpful error message
    4. Returns only when valid input of the correct type is provided
    
    The function uses generic typing to maintain compile-time type safety
    while supporting runtime validation for any type that can be constructed
    from a string (int, float, etc.).
    
    Common use cases:
        - age = get_validated_input("Enter your age: ", int)
        - grade = get_validated_input("Enter grade: ", float)
        - semester = get_validated_input("Semester number: ", int)
    
    Args:
        prompt: The message displayed to prompt user input
        target_type: The expected data type (e.g., int, float)
                    Must be a type that can convert from string
    
    Returns:
        T: User input converted to the specified type, guaranteed to be valid
        
    Raises:
        KeyboardInterrupt: If user presses Ctrl+C during input
        EOFError: If input stream is closed unexpectedly
        
    Note:
        This function will loop indefinitely until valid input is provided.
        The target_type must support construction from string (e.g., int("5")).
    """
    while True:
        # Get user input as string
        user_input = console.input(prompt)
        
        try:
            # Attempt type conversion using the target type's constructor
            # This works for int(), float(), and other types that accept strings
            validated_value = target_type(user_input)
            return validated_value
        except ValueError:
            # Handle conversion errors with user-friendly feedback
            # Show specific type name for clearer error messages
            console.print(
                f"[bold red]Ungültige Eingabe.[/bold red] "
                f"Bitte gib einen gültigen Wert vom Typ '{target_type.__name__}' ein."
            )