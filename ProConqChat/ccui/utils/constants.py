"""
CCUI's Constants
"""

from sys import platform
from pathlib import Path

# CCUI
VERSION = '0.4.0'


# OS
class OS:
    LINUX: bool = platform.startswith('linux')
    WINDOWS: bool = platform.startswith('win32')


# Paths
class Paths:
    PROJECT_DIR = Path(__file__).resolve().parent.parent
    LOGGING: Path = PROJECT_DIR / 'logs'

    HELP: str = 'utils/text/ccui_prompt_help.txt'
    THELP: str = 'utils/text/ccui_prompt_thelp.txt'
    CHELP: str = 'utils/text/ccui_prompt_chelp.txt'
    LOGO: str = 'utils/text/ccui_logo.txt'
    TOOLS: str = 'utils/text/ccui_tools.txt'
    