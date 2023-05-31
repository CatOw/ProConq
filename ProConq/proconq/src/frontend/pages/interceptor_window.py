# Imports that are common for pages modules
from proconq.src.frontend.pages.common_imports import *
from proconq.setup_logging import setup_logging
from proconq.src.backend.tracer.tracer_handler import Syscall


"""
Each page object has a parent and frontend.

The parent is the main window in which the page is contained.
The frontend is the Frontend to interact with.
"""


class InterceptorPage(QWidget):
    def __init__(self, parent: QMainWindow = None, frontend: Frontend = None):
        super().__init__(parent)

        self.logger = setup_logging(__name__)

        self.frontend = frontend
        self.tracer_handler = self.frontend.tracer_handler

        # Used for skipping. Saves the arrival state before changes
        self.syscall_arrival_backup: Syscall = None

        self.tracer_handler.paused.connect(self.handle_tracer_paused)

        PagesUtils.set_standard_configs(self)

        labels: list[tuple] = [
            ('Interceptor', 'title_label', 0, 60, True),
            ('-Syscall Name-', 'text_label', 0, 170, True),
            ('-Args-', 'text_label', 125, 170),
            ('-Arg Type-', 'valid_label', 280, 190),
            ('-Ret Val-', 'text_label', 0, 320, True),
            ('-Manage Filter-', 'text_label', 830, 170),
            ('-Forward Syscall-', 'text_label', 830, 400)
        ]

        # Arguments related widgets
        self.arg_textboxes: list[QLineEdit] = []
        self.type_labels: list[QLabel] = []

        # Create 6 Arg labels, textboxes and types
        for pos in range(6):
            # Label
            labels.append((f'{pos}.', 'text_label', 40, 240 + pos * 70))
            # Textbox
            self.arg_textboxes.append(self.create_arg_textbox(pos))
            # Type
            self.type_labels.append(self.create_arg_type_label(pos))

        PagesUtils.add_labels(self, labels)

        # Create all non arg-related textboxes 
        self.name_textbox = self.create_name_textbox()
        self.ret_textbox = self.create_ret_textbox()
        self.filter_textbox = self.create_filter_textbox()

        # Create all buttons
        self.create_intercept_button()
        self.create_skip_button()
        self.create_autoskip_filter_button()
        self.create_intercept_filter_button()

    def create_arg_textbox(self, pos: int) -> QLineEdit:
        textbox = QLineEdit(self)
        textbox.setReadOnly(True)
        PagesUtils.place_widget(self, textbox,
                                Stylesheets.small_textbox_locked,
                                120, 250 + pos * 70)
        return textbox
    
    def create_arg_type_label(self, pos: int) -> QLabel:
        label = QLabel('unknown', self)
        PagesUtils.place_widget(self, label,
                                Stylesheets.valid_label,
                                280, 240 + pos * 70)
        return label

    def create_name_textbox(self) -> QLineEdit:
        textbox = QLineEdit(self)
        textbox.setReadOnly(True)
        PagesUtils.place_widget(self, textbox,
                                Stylesheets.small_textbox_locked,
                                0, 250, True)
        return textbox
    
    def create_ret_textbox(self) -> QLineEdit:
        textbox = QLineEdit(self)
        textbox.setReadOnly(True)
        PagesUtils.place_widget(self, textbox,
                                Stylesheets.small_textbox_locked,
                                0, 400, True)
        return textbox
    
    def create_filter_textbox(self) -> QLineEdit:
        textbox = QLineEdit(self)
        PagesUtils.place_widget(self, textbox,
                                Stylesheets.textbox,
                                855, 240)
        return textbox
    
    def create_intercept_button(self) -> None:
        button = QPushButton('Intercept', self)
        PagesUtils.place_widget(self, button, Stylesheets.button,
                                850, 490)
        button.clicked.connect(self.intercept)

    def create_skip_button(self) -> None:
        button = QPushButton('Skip', self)
        PagesUtils.place_widget(self, button, Stylesheets.button,
                                1020, 490)
        button.clicked.connect(self.skip)

    def create_autoskip_filter_button(self) -> None:
        button = QPushButton('AutoSkip', self)
        PagesUtils.place_widget(self, button, Stylesheets.button,
                                820, 300)
        button.clicked.connect(self.autoskip_filter)
    
    def create_intercept_filter_button(self) -> None:
        button = QPushButton('Intercept', self)
        PagesUtils.place_widget(self, button, Stylesheets.button,
                                980, 300)
        button.clicked.connect(self.intercept_filter)
    
    def reset_arg(self, pos: int) -> None:
        arg_textbox = self.arg_textboxes[pos]
        type_label = self.type_labels[pos]
        arg_textbox.setReadOnly(True)
        arg_textbox.setStyleSheet(Stylesheets.small_textbox_locked)
        arg_textbox.setText('')
        type_label.setText('unknown')

    def reset_ret(self) -> None:
        self.ret_textbox.setReadOnly(True)
        self.ret_textbox.setStyleSheet(Stylesheets.small_textbox_locked)
        self.ret_textbox.setText('')

    def autoskip_filter(self):
        name = self.filter_textbox.text()
        if not name:
            return
        self.filter_textbox.setText('')
        self.tracer_handler.add_autoskip_filter(name)

    def intercept_filter(self):
        name = self.filter_textbox.text()
        if not name:
            return
        self.filter_textbox.setText('')
        self.tracer_handler.remove_autoskip_filter(name)

    def intercept(self):
        """
        Modifies Syscall object to have the UI values.
        Continues the execution.
        """
        syscall = self.tracer_handler.syscall

        for pos in range(6):
            syscall.args[pos] = self.arg_textboxes[pos].text()

        syscall.ret = self.ret_textbox.text()
        self.tracer_handler.continue_execution()

    def skip(self) -> None:
        """
        Modifies Syscall object to have the values it came with.
        Continues the execution.
        """
        if self.syscall_arrival_backup is None:
            return
        self.tracer_handler.syscall = self.syscall_arrival_backup
        self.tracer_handler.continue_execution()

    def handle_tracer_paused(self, paused: bool):
        if paused:
            self.logger.debug(f'Paused {self.tracer_handler.pid}')

            event_name = self.tracer_handler.input_event.decode().strip()
            
            if event_name.startswith('FINISH'):
                self.logger.debug(f'FINISH: Closing PID {self.tracer_handler.pid}')
                super().close()
                self.frontend.main_window.close()
                return

            if event_name.startswith('SETARG'):
                arg_pos = int(event_name[6])
                arg_val = self.tracer_handler.syscall.args[arg_pos]
                self.tracer_handler.write_input(arg_val)
                self.tracer_handler.continue_execution()
                return
            elif event_name.startswith('SETRET'):
                ret_val = self.tracer_handler.syscall.ret
                self.tracer_handler.write_input(ret_val)
                self.tracer_handler.continue_execution()
                return

            self.update_ui()
        else:
            self.logger.debug(f'Unpaused {self.tracer_handler.pid}')
            self.reset_ui()

    def set_ui_args(self, args_amount: int, args: list[str],
                    args_types: list[str]) -> None:
        for pos, arg in enumerate(args):
            textbox = self.arg_textboxes[pos]
            type_label = self.type_labels[pos]
            if pos < args_amount:
                textbox.setReadOnly(False)
                textbox.setStyleSheet(Stylesheets.small_textbox)
                textbox.setText(arg)
                type_label.setText(args_types[pos])
            else:
                self.reset_arg(pos)

    def reset_ui(self) -> None:
        """
        Fills the UI with default empty fields.
        """
        self.syscall_arrival_backup = None

        for pos in range(6):
            self.reset_arg(pos)
        self.name_textbox.setText('')
        self.reset_ret()

    def update_ui(self) -> None:
        """
        Fills the UI with the updated syscall information.
        """
        syscall = self.tracer_handler.syscall
        self.syscall_arrival_backup = syscall
        
        pid = self.tracer_handler.pid

        # Update name
        self.logger.debug(f'PID {pid} updating name to {syscall.name}')
        self.name_textbox.setText(syscall.name)

        # Update args
        self.logger.debug(f'PID {pid} updating args to {syscall.args}')
        if syscall.is_entry:
            self.set_ui_args(syscall.args_amount,
                             syscall.args, syscall.args_types)
            self.reset_ret()

        # Update ret
        if not syscall.is_entry:
            self.set_ui_args(syscall.args_amount,
                             syscall.args, syscall.args_types)
            self.ret_textbox.setReadOnly(False)
            self.ret_textbox.setStyleSheet(Stylesheets.small_textbox)
            self.ret_textbox.setText(syscall.ret)


class HelpPage(QWidget):
    def __init__(self, parent: QMainWindow = None, frontend: Frontend = None):
        super().__init__(parent)

        self.frontend = frontend
        self.tracer_handler = self.frontend.tracer_handler

        PagesUtils.set_standard_configs(self)