import threading
import subprocess
import fcntl
import os
import logging

from PyQt6.QtCore import (
    QObject,
    pyqtSignal
)

from proconq.utils.constants import Paths
from proconq.utils.exceptions import TracerError
from proconq.setup_logging import setup_logging


class Syscall:
    """
    Contains information about the currently
        intercepted system call.
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger

        self.is_entry: bool = False
        
        self.name: str = 'None'
        self.args_amount: int = 0
        self.ret: str = ''
        
        self.args: list[str] = [''] * 6
        self.args_types: list[str] = ['unknown'] * 6

    def reset_syscall(self) -> None:
        self.is_entry = False
        self.name = 'None'
        self.args_amount = 0
        self.ret = ''
        self.args = [''] * 6
        self.args_types = ['unknown'] * 6

    def extract_syscall(self, lines: list[bytes]):
        """
        First item contains type, args amount and name.
        Second item is either ret if type Exit
        """
        self.reset_syscall()
        first_item = lines[0].decode().strip()

        # Syscall name
        self.name = first_item[2:]
        self.logger.debug(f'Set name {self.name}')
        
        # Check if Entry (E) or Exit (R)
        if first_item[0] == 'E':
            self.is_entry = True
            self.extract_entry(first_item, lines[1:])
        else:
            self.is_entry = False
            self.extract_exit(lines[1].decode().strip())

    def extract_entry(self, first_item: str, args: list[bytes]) -> None:
        self.logger.debug(f'Set Entry')
        # Args amount
        self.args_amount = int(first_item[1])
        self.logger.debug(f'Set args amount: {self.args_amount}')
        # Ret value
        self.ret = ''
        self.logger.debug('Reset ret')

        for arg in args:
            arg = arg.decode()
            self.logger.debug(f'Handling {arg}')
            # Get arg position
            pos = int(arg[3])
            self.logger.debug(f'Arg Pos: {pos}')

            # Get arg type
            match arg[4]:
                case '0':
                    arg_type = 'long'
                case '1':
                    arg_type = 'string'
                case _:
                    arg_type = 'unknown'

            self.logger.debug(f'Setting arg {pos} type: {arg_type}')
            self.args_types[pos] = arg_type

            # Get arg
            self.arg_size = arg[5:9]
            self.logger.debug(f'Arg {pos} size: {self.arg_size}')
            self.args[pos] = arg[9:]
            self.logger.debug(f'Set arg {pos}: {arg[9:]}')

    def extract_exit(self, second_item: str) -> None:
        self.logger.debug(f'Set Exit')
        # Args amount
        self.args_amount = 0
        self.logger.debug(f'Set args amount: 0')
        # Ret value
        self.ret = second_item[3:]
        self.logger.debug(f'Set ret: {self.ret}')
    

class TracerHandler(QObject):
    """
    Creates and handles an interceptor tracer subprocess.
    """
    paused = pyqtSignal(bool)

    def __init__(self, is_pid: bool, command: str):
        super().__init__()

        self.logger = setup_logging(__name__)

        if is_pid:
            self.logger.debug(f'Setting PID to {command}')
            self.pid = command
            option = '-p'
        else:
            option = '-e'

        interceptor_command = \
        f'./{Paths.INTERCEPTOR} {option} {command}\n'
        self.logger.debug(f'Running subprocess: {interceptor_command}')
        self.proc = subprocess.Popen(['/bin/bash'],
                                     stdout=subprocess.PIPE,
                                     stdin=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        
        stderr_fd = self.proc.stderr.fileno()
        flags = fcntl.fcntl(stderr_fd, fcntl.F_GETFL)
        fcntl.fcntl(stderr_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        self.write_input(interceptor_command)
        
        self.syscalls_to_skip: set[str] = set()
        self.syscall = Syscall(self.logger)

        self.input_event: bytes = b''

        self.pause_event = threading.Event()
        self.is_paused = False
        self.interact_thread = \
            threading.Thread(target=self.interact)
        self.interact_thread.start()

    def write_input(self, data: str) -> None:
        if not data.endswith('\n'):
            data += '\n'
        self.logger.debug(f'Writing input {data.encode()}')
        self.proc.stdin.write(data.encode())
        self.proc.stdin.flush()

    def interact(self):
        while True:
            try:
                # Read until input
                self.logger.debug(f'{self.pid} Reading until input')
                lines = self.read_until_input()
                self.logger.debug(f'{self.pid} {lines}')

                self.input_event = lines[-1]
                self.logger.debug(f'{self.pid} input event {self.input_event}')

                if self.input_event == b'SKIP\n':
                    self.syscall.extract_syscall(lines[:-1])

                    # Continue if syscall is to be skipped
                    if self.syscall.name in self.syscalls_to_skip:
                        self.logger.debug(f'{self.pid} Syscall {self.syscall.name} is filtered. Skipping')
                        self.write_input('1\n')
                        continue
                    
                    self.logger.debug(f'{self.pid} Intercepting {self.syscall.name}')
                    self.write_input('0\n')
                
                self.logger.debug(f'{self.pid} wait signal')
                self.is_paused = True
                self.paused.emit(True)
                self.pause_event.wait()
                self.is_paused = False
                self.paused.emit(False)
                self.logger.debug(f'{self.pid} continue signal')
                self.pause_event.clear()
            except TracerError:
                self.input_event = b'FINISH'
                self.is_paused = True
                self.paused.emit(True)

    def continue_execution(self):
        """
        Signal the TracerHandler to continue execution.
        """
        self.pause_event.set()

    def read_until_input(self) -> list[bytes]:
        """
        Reads stdout of subprocess until detected input event.
        Returns the entire stdout that was read.
        If an error in stderr is detected raise TracerError
        """
        input_events = [
            b'SKIP',
            b'SETARG',
            b'SETRET'
        ]
        lines: list[bytes] = []

        while True:
            try:
                errors = self.proc.stderr.read(1)
            except IOError:
                pass
            if errors:
                self.logger.warning(f'TracerError {self.pid} {errors}')
                raise TracerError
            
            self.logger.debug(f'{self.pid} Reading line')
            line = self.proc.stdout.readline()
            lines.append(line)
            self.logger.debug(f'{self.pid} Readline {line}')

            if any(line.startswith(event) \
                   for event in input_events):
                self.logger.debug(f'{self.pid} Input found')
                break
        
        return lines
    
    def add_autoskip_filter(self, name: str) -> None:
        """
        Adds a syscall name to the syscalls to skip filter
        """
        self.syscalls_to_skip.add(name)
        self.logger.debug(f'{self.pid} added AutoSkip {name}')

    def remove_autoskip_filter(self, name: str) -> None:
        """
        Removes a syscall name from the syscalls to skip filter
        """
        self.syscalls_to_skip.remove(name)
        self.logger.debug(f'{self.pid} removed AutoSkip {name}')
