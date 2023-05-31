from pathlib import Path
from typing import TypeVar

from PyQt6.QtWidgets import QWidget


class Colors:
    LIGHTSEAGREEN = '#20B2AA'
    TEAL = '#008080'
    MEDIUMAQUAMARINE = '#66CDAA'
    CADETBLUE = '#5F9EA0'
    AQUAMARINE = '#7FFFD4'
    DARKSLATEGRAY = '#2F4F4F'
    ROSE = '#E3242B'
    LIME = '#AEF359'
    VIOLET = '#710193'
    COAL = '#0C0908'


class Paths:
    PROJECT_DIR = Path(__file__).resolve().parent.parent

    LOGGING: Path = PROJECT_DIR / 'logs'

    SYSTEM_CHECKS: Path = PROJECT_DIR / 'bin' / 'system_checks'
    CHECK_ATTACHABILITY: Path = SYSTEM_CHECKS / 'check_ptrace_attachability'
    PIDOF: Path = SYSTEM_CHECKS / 'pidof'
    
    PAGES_PATH: str = 'proconq.src.frontend.pages'

    INTERCEPTOR: str = 'proconq/bin/interceptor/interceptor'


class TypeAliases:
    WidgetSubclass = TypeVar('WidgetSubclass', bound=QWidget)


class Literals:
    WIDTH = 1200
    HEIGHT = 800
    TOOLBAR_HEIGHT = 40
    