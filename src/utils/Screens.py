import os
from tabulate import tabulate

def clear_terminal():
    """
    Clears the terminal screen based on the operating system.
    """
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For Mac and Linux (posix-based systems)
    else:
        _ = os.system('clear')

def new_line():
    print("\n")

def print_table(headers, content):
    print(tabulate(content, headers, tablefmt="grid"))