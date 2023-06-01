"""
CCUI's Error Codes
"""

# --Launch related errors--
# Responsible for restarting CCUI
class ExitCCUIRestart(Exception):
    pass


# Responsible for shutting down CCUI
class ExitCCUIShutdown(Exception):
    pass


# Responsible for reloading CCUI
class ExitCCUIReload(Exception):
    pass


# Responsible for switching CCUI mode
class SwitchCCUIMode(Exception):
    def __init__(self, mode):
        self.mode = mode


# Responsible for activating CCUI tool
class ActivateCCUITool(Exception):
    def __init__(self, tool):
        self.tool = tool


# Responsible for breaking out of a try statement
class BreakTry(Exception):
    pass


# Responsible for informing of an illegal username
class InvalidUsername(Exception):
    pass
# ----