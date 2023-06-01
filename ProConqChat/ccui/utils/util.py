"""
General utility functions.
"""

import os
from pathlib import Path, PurePath
from random import choice
import importlib.resources

from rich import print as rprint

# CCUI Modules
from ccui.utils.constants import OS


class Singleton(type):
    """
    This metaclass ensures that only one instance of the class
    is created and reused for subsequent calls.
    """
    # Dictionary to store the existing instances
    _instances = {} 

    def __call__(cls, *args, **kwargs):
        """
        Override the __call__ method to control the instance creation process.
        """
        if cls not in cls._instances:
            # If the class doesn't exist in _instances, create a new instance
            cls._instances[cls] = super().__call__(*args, **kwargs)

        # Return the existing or newly created instance
        return cls._instances[cls]


def clear() -> None:
    """Clears the terminal."""
    os.system("cls" if OS.WINDOWS else "clear")


def output_random_quote() -> None:
    """
    Outputs a random quote to the console.
    """
    quotes = [
        "[#61D6D6]I can't really tell if it's a terminal, console, shell or command-line...",
        "[#B4009E]I didn't expect you'd find this hidden feature!",
        "[#E74856]How dare you look at the source code?!?",
        "[#16C60C]I'm not sure what you're trying to do here...",
        "[#0C0C0C]Either your console is broken or you're choosing me."
    ]
    rprint(choice(quotes))


def replace_chars(text: str, chars: str, replace: str) -> str:
    """
    Replace characters in string with others randomly selected.\n
    text    -- string to affect\n
    chars   -- collection of chars to randomly pick from\n
    replace -- substring to replace\n
    """
    list_of_chars = list(text)
    for index, char in enumerate(list_of_chars):
        if char == replace:
            list_of_chars[index] = choice(chars)
    return "".join(list_of_chars)


def output_file_content(path: str, replace: str = None, replacement: str = None) -> None:
    """
    Outputs the text files to the terminal (supports colors).\n
    path        -- path/example.txt\n
    replace     -- replace given substring with replacement\n
    replacement -- random.choice(replacement) will replace given replace string\n
    """
    # Extract path to file
    parent = PurePath(path).parts
    parent = '.'.join(parent[:-1])
    # Extract filename
    filename = Path(path).name

    file_content = ""
    with importlib.resources.open_text(f'ccui.{parent}', filename) as file:
        for line in file:
            file_content += replace_chars(line, replacement, replace) if replace else line

    rprint(file_content)
