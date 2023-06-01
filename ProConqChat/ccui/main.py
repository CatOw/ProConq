"""
The main interaction console of CCUI
"""

from cmd import Cmd

from rich import print as rprint

# CCUI Modules
import ccui.utils.util
from ccui.utils.errors import (
    ExitCCUIRestart,
    ExitCCUIShutdown,
    ExitCCUIReload,
    SwitchCCUIMode
)
from ccui.utils.constants import Paths
from ccui.tools.tools_manager import launch as tlaunch
from ccui.setup_logging import setup_logging


class CCUIPrompt(Cmd):
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
        ccui.utils.util.output_file_content(Paths.HELP)

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

    def do_restart(self, args: str) -> None:
        """
        restart

        Description:
            A partial restart of CCUI to update main code changes.
        """
        if args.strip():
            return self.no_args('restart')
        raise ExitCCUIRestart
    
    def do_shutdown(self, args: str) -> None:
        """
        shutdown

        Description:
            Shutdown CCUI.
        """
        if args.strip():
            return self.no_args('shutdown')
        raise ExitCCUIShutdown

    def do_reload(self, args: str):
        """
        reload

        Description:
            Reload CCUI.
        """
        if args.strip():
            return self.no_args('reload')
        raise ExitCCUIReload

    def do_clear(self, args: str) -> None:
        """
        clear

        Description:
            Clear the terminal.
        """
        if args.strip():
            return self.no_args('clear')
        ccui.utils.util.clear()

    def do_tools(self, args: str) -> None:
        """
        tools

        Description:
            Show available tools.
        """
        if args.strip():
            return self.no_args('tools')
        ccui.utils.util.output_file_content(Paths.TOOLS)

    def do_tool(self, args: str) -> None:
        """
        tool (no arguments)

        Description:
            Activate the tools manager.
        """
        if args.strip():
            return self.no_args('tool')
        raise SwitchCCUIMode('ToolsMgr')

    def do_quote(self, args: str) -> None:
        """
        quote

        Description:
            Nice quotes :)
        """
        if args.strip():
            return print("But I don't have any arguments >:(")
        ccui.utils.util.output_random_quote()

    # -Alternative names for commands-
    # do_ is an identifier for commands
    do_commands = do_help
    do_reboot = do_restart
    do_exit = do_quit = do_stop = do_shutdown
    do_refresh = do_reload
    do_cls = do_clear


def launch(fresh_launch: bool = True) -> None:
    """
    Handles the CCUI initial prompt, Prevents KeyboardInterrupt.

    Keyword arguments:
    fresh_launch -- set default prompt (default True)
    """
    # The loop will ever be broken only if:
    # 1. Fatal error.
    # 2. Restart.
    # 3. Shutdown.
    # 4. Reload.

    # Default prompt, CCUI
    prompt = CCUIPrompt()
    mode = "[CCUI] >> "

    while True:
        try:
            prompt.prompt = mode

            if fresh_launch:
                # This runs ONLY if launched by __main__.py
                ccui.utils.util.clear()
                prompt.cmdloop(ccui.utils.util.output_file_content(Paths.LOGO, "*", "CCUI"))
            else:
                prompt.cmdloop()

        # Handle Prompt Exceptions
        except KeyboardInterrupt:
            print("^C")
        except SwitchCCUIMode as switch_mode:
            tlaunch(switch_mode.mode)
            
        finally:
            fresh_launch = False


if __name__ == '__main__':
    launch()
