"""
The tools manager of CCUI
"""

from cmd import Cmd

from rich import print as rprint

# CCUI Modules
import ccui.utils.util
from ccui.utils.errors import (
    ExitCCUIShutdown,
    SwitchCCUIMode,
    ActivateCCUITool
)
from ccui.utils.constants import Paths
from ccui.tools.chat.chat import launch as tlaunch
from ccui.setup_logging import setup_logging


class ToolsManagerPrompt(Cmd, metaclass=ccui.utils.util.Singleton):
    def __init__(self):
        super().__init__()
        self.logger = setup_logging(__name__)
    
    def no_args(self, command: str) -> None:
        text = f"  Usage: {command} (no arguments)"
        self.logger.debug(text)
        print(text)

    def do_help(self, args: str) -> None:
        """
        help

        Description:
            Provide all commands.
        """
        if args.strip():
            return self.no_args('help')
        ccui.utils.util.output_file_content(Paths.THELP)

    def do_man(self, command: str) -> None:
        """
        Description:
            Provide a manual for given command.

        Parameter List:
            command -- Displays manual for specific given command.
        """
        if not command.strip():
            return self.no_args('man')
        try:
            text = getattr(self, "do_" + command).__doc__
            self.logger.debug(text)
            print(text)
        except AttributeError:
            text = f"[#E74856]ERROR: No such command '{command}'[/#E74856]"
            self.logger.debug(text)
            rprint(text)

    def do_shutdown(self, args: str) -> None:
        """
        shutdown

        Description:
            Shutdown CCUI.
        """
        if args.strip():
            return self.no_args('shutdown')
        raise ExitCCUIShutdown

    def do_clear(self, args: str) -> None:
        """
        clear

        Description:
            Clear the terminal.
        """
        if args.strip():
            return self.no_args('clear')
        ccui.utils.util.clear()

    def do_back(self, args: str) -> None:
        """
        back

        Description:
            Retrieve from Tools Manager back to CCUI.
        """
        if args.strip():
            return self.no_args('back')
        raise SwitchCCUIMode('CCUI')

    def do_tools(self, args: str) -> None:
        """
        tools

        Description:
            Show available tools.
        """
        if args.strip():
            return self.no_args('tools')
        ccui.utils.util.output_file_content(Paths.TOOLS)

    def do_chat(self, args: str) -> None:
        """
        chat

        Description:
            Activates the chat tool.
        """
        if args.strip():
            return self.no_args('chat')
        raise ActivateCCUITool('Chat')

    def do_pac(self, args: str) -> None:
        """
        An upcoming feature which will allow to install
        community made contributions.
        """
        rprint("[#B4009E]An upcoming command!")

    # -Alternative names for commands-
    # do_ is an identifier for commands
    do_commands = do_help
    do_exit = do_quit = do_stop = do_shutdown
    do_cls = do_clear
    do_return = do_back
    do_addon = do_plug = do_tweak = do_pac


def launch(mode: str = 'ToolsMgr'):
    """
    Handles the Tools Manager prompt, Prevents KeyboardInterrupt.
    """
    # The loop will ever be broken only if:
    # 1. Fatal error.
    # 2. Shutdown.

    # Default prompt, CCUI
    prompt = ToolsManagerPrompt()
    mode = f"[{mode}] >> "

    while True:
        try:
            prompt.prompt = mode
            prompt.cmdloop()

        # Handle Prompt Exceptions
        except KeyboardInterrupt:
            print("^C")
        except SwitchCCUIMode as switch_mode:
            mode = f"[{switch_mode.mode}] >> "
            break
        except ActivateCCUITool as activate_tool:
            tlaunch(activate_tool.tool)


if __name__ == '__main__':
    launch()
