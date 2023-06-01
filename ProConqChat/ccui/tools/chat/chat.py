from cmd import Cmd
from ipaddress import ip_address

from rich import print as rprint

import ccui.utils.util
from ccui.utils.errors import (
    ExitCCUIShutdown,
    SwitchCCUIMode,
    BreakTry,
    InvalidUsername
)
from ccui.utils.constants import Paths
from ccui.tools.chat.chat_client import ChatClient
from ccui.setup_logging import setup_logging


class ChatPrompt(Cmd, metaclass=ccui.utils.util.Singleton):
    def __init__(self):
        super().__init__()
        self.chat_client = ChatClient()
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
        ccui.utils.util.output_file_content(Paths.CHELP)

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
        raise SwitchCCUIMode('ToolsMgr')
    
    def do_connect(self, addr: str) -> None:
        """
        connect [ip] [port]

        Description:
            Connect to the Chat Server.
            Entering 'def' as a parameter will
                connect to ('127.0.0.1', 50000)

        Parameter List:
            IP -- ip of the desired server.
            PORT -- port of the desired server.
        """
        addr = addr.strip()

        if not addr:
            return print('  Usage: connect [ip] [port]')
        try:
            ip = addr.split()[0]
            if ip == 'def':
                raise BreakTry

            port = addr.split()[1]

            ip = ip_address(ip)
            port = int(port)
            if not (0 <= port <= 65535):
                raise ValueError
        except ValueError:
            return rprint(f"[#E74856]ERROR: Invalid IP or Port ('{ip}', {port})[/#E74856]")
        except IndexError:
            return print('  Usage: connect [ip] [port]')
        except BreakTry:
            ip = '127.0.0.1'
            port = 50000
        rprint(f"[#16C60C]Connection Addr ('{ip}', {port}) valid. Attempting connection...[/#16C60C]")
        self.chat_client.connect(ip, port)

    def do_disconnect(self, args: str) -> None:
        """
        disconnect

        Description:
            Disconnects from the Chat Server.
        """
        if args.strip():
            return print("  Usage: disconnect (no arguments)")
        rprint("[#16C60C]Attempting disconnection...[/#16C60C]")
        self.chat_client.disconnect()

    def do_users(self, args: str) -> None:
        """
        users

        Description:
            Get the list of online users.
        """
        if args.strip():
            return self.no_args('users')
        rprint("[#16C60C]Getting active users list...[/#16C60C]")
        self.chat_client.get_users()

    def do_login(self, args: str) -> None:
        """
        login [name] [password]

        Description:
            Login to the chat server.

        Parameter List:
            NAME -- Your name.
            PASSWORD -- Your password.
        """
        args = args.split()

        if not args:
            return print('  Usage: login [name] [password]')
        try:
            name = args[0]
            password = args[1]

            if not name.isalpha():
                raise InvalidUsername

            rprint(f"[#16C60C]Logging in NAME: {name} PASSWORD: {password}[/#16C60C]")
            self.chat_client.login(name, password)
        except IndexError:
            print('  Usage: login [name] [password]')
        except InvalidUsername:
            rprint(f"[#E74856]ERROR: Username {name} must contain only alphabets.[/#E74856]")

    def do_register(self, args: str) -> None:
        """
        register [name] [password]

        Description:
            Register as a user.

        Parameter List:
            NAME -- Your name.
            PASSWORD -- Your password.
        """
        args = args.split()

        if not args:
            return print('  Usage: register [name] [password]')
        try:
            name = args[0]
            password = args[1]

            if not name.isalpha():
                raise InvalidUsername

            rprint(f"[#16C60C]Registering NAME: {name} PASSWORD: {password}[/#16C60C]")
            self.chat_client.register(name, password)
        except IndexError:
            print('  Usage: register [name] [password]')
        except InvalidUsername:
            rprint(f"[#E74856]ERROR: Username {name} must contain only alphabets.[/#E74856]")

    def do_getid(self, args: str) -> None:
        """
        getid

        Description:
            Get your user's ID.
        """
        if args.strip():
            return self.no_args('getid')
        rprint(f"[#16C060C]Getting ids...")
        self.chat_client.get_id()

    def do_message(self, args: str) -> None:
        """
        message [id] [message]

        Description:
            Send a message to a user.

        Parameter List:
            ID -- id of the desired user.
            MESSAGE -- message to send.
        """
        if not args.split():
            return print('  Usage: connect [id] [message]')
        try:
            receiver_id = args.split()[0]
            message = args[len(receiver_id) + 1:]

            receiver_id = int(receiver_id)
            if not (1000 <= receiver_id <= 9999):
                raise ValueError
            rprint(f"[#16C60C]Sending message...[/#16C60C]")
            self.chat_client.send_message(receiver_id, message)
        except ValueError:
            return rprint(f"[#E74856]ERROR: Invalid ID: {receiver_id}[/#E74856]")
        except IndexError:
            return print('  Usage: message [id] [message]')
    
    def do_mail(self, args: str) -> None:
        """
        mail

        Description:
            Get the list of received messages.
        """
        if args.strip():
            return self.no_args('mail')
        self.chat_client.output_mail()

    def do_buffer(self, args: str) -> None:
        """
        buffer

        Description:
            See messages that (probably) failed to send.
        """
        args = args.strip()
        if args:
            return self.no_args('buffer')
        return self.chat_client.buffer()
    
    def do_database(self, args: str) -> None:
        """
        database

        Description:
            Get the database (admins only).
        """
        if args.strip():
            return self.no_args('database')
        rprint(f"[#16C060C]Getting database...")
        self.chat_client.database()

    def do_deluser(self, name: str) -> None:
        """
        deluser [name]

        Description:
            Delete a registered user from the database (admins only).
        """
        name = name.strip()
        if not name:
            return print('  Usage: deluser [name]')
        
        try:
            if not name.isalpha():
                raise InvalidUsername
            
            rprint(f"[#16C060C]Attempting to delete user...")
            self.chat_client.deluser(name)
        except InvalidUsername:
            rprint(f"[#E74856]ERROR: Username {name} must contain only alphabets.[/#E74856]")

        
    # -Alternative names for commands-
    # do_ is an identifier for commands
    do_commands = do_help
    do_exit = do_quit = do_stop = do_shutdown
    do_cls = do_clear
    do_return = do_back
    do_id = do_getid
    do_msg = do_message


def launch(mode: str = 'Chat'):
    """
    Handles the Chat prompt, Prevents KeyboardInterrupt.
    """
    # The loop will ever be broken only if:
    # 1. Fatal error.
    # 2. Shutdown.

    # Default prompt, CCUI
    prompt = ChatPrompt()
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


if __name__ == '__main__':
    launch()
    