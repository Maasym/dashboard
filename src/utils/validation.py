from typing import Type, TypeVar
from rich.console import Console

T = TypeVar('T') # Generic TypeVar for type hinting
console = Console()

def get_validated_input(prompt: str, target_type: Type[T]) -> T:
    """
    Prompts the user for input until a valid value of the target type is entered.

    Args:
        prompt (str): The message to display to the user.
        target_type (Type[T]): The data type to convert the input to (e.g., int, float).

    Returns:
        T: The validated and converted user input.
    """
    while True:
        user_input = console.input(prompt)
        try:
            # Attempt to convert the input to the desired type
            return target_type(user_input)
        except ValueError:
            # If conversion fails, inform the user and loop again
            console.print(f"[bold red]Ungültige Eingabe.[/bold red] Bitte gib einen gültigen Wert vom Typ '{target_type.__name__}' ein.")