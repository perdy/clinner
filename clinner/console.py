from rich.console import Console

__all__ = ["console", "error_console"]

console = Console()
error_console = Console(stderr=True, style="bold red")
