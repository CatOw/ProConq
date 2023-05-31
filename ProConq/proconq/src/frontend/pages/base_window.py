# Imports that are common for pages modules
from proconq.src.frontend.pages.common_imports import *


"""
Each page object has a parent and frontend.

The parent is the main window in which the page is contained.
The frontend is the Frontend to interact with.
"""


class HomePage(QWidget):
    def __init__(self, parent: QMainWindow = None, frontend: Frontend = None):
        super().__init__(parent)

        self.frontend = frontend

        PagesUtils.set_standard_configs(self)

        labels: list[tuple] = [
            ('Welcome to ProConq', 'title_label', 0, 60, True),
            (LargeTexts.home_information, 'text_label', 0, 160, True),
            ('> By Yuval .O.', 'text_label', 0, 600, True)
        ]

        PagesUtils.add_labels(self, labels)


class TracerPage(QWidget):
    def __init__(self, parent: QMainWindow = None, frontend: Frontend = None):
        super().__init__(parent)

        self.frontend = frontend

        PagesUtils.set_standard_configs(self)

        labels: list[tuple] = [
            ('Tracer', 'title_label', 0, 60, True),
            (LargeTexts.tracer_information, 'text_label', 0, 160, True),
            (LargeTexts.tracer_field_prompts, 'prompt_label', 0, 300, True)
        ]

        PagesUtils.add_labels(self, labels)

        pid_button = self.add_pid_selection_button()
        name_button = self.add_name_selection_button()

        self.textboxes: dict[str, QLineEdit] = {}
        self.textboxes['pid'] = self.add_pid_selection_textbox(pid_button)
        self.textboxes['name'] = self.add_name_selection_textbox(name_button)

        self._selected_pid = 'None'
        self.selected_pid_label: QLabel = None
        self.add_selected_pid_prompt_label()

        self.invalid_pid_label = self.create_invalid_pid_label()
        self.invalid_pid_timer = QTimer()

        self.invalid_name_label = self.create_invalid_name_label()
        self.invalid_name_timer = QTimer()

        self.multiple_pids_label = self.create_multiple_pids_label()
        self.multiple_pids_timer = QTimer()

        self.add_start_tracing_button()
        self.attachment_fail_label = self.create_no_pid_selected_label()
        self.attachment_fail_timer = QTimer()

        self.add_file_execution_label()
        file_execution_button = self.add_file_execution_button()
        self.textboxes['file_execution'] = self.add_file_execution_textbox(
            file_execution_button)
        
        self.name_scroll_area = self.create_name_scroll_area()

    @property
    def selected_pid(self):
        return self._selected_pid
    
    @selected_pid.setter
    def selected_pid(self, pid: str) -> None:
        self._selected_pid = pid
        text = f'Selected PID:\n{pid}'
        self.selected_pid_label.setText(text)
        
    def add_pid_selection_button(self) -> QPushButton:
        button = QPushButton('Select by PID', self)
        PagesUtils.place_widget(self, button, Stylesheets.button,
                                207, 440)
        button.clicked.connect(self.select_by_pid)
        return button

    def add_name_selection_button(self) -> QPushButton:
        button = QPushButton('Select by Name', self)
        PagesUtils.place_widget(self, button, Stylesheets.button,
                                792, 440)
        button.clicked.connect(self.select_by_name)
        return button

    def add_pid_selection_textbox(self, button: QPushButton) -> QLineEdit:
        textbox = QLineEdit(self)
        PagesUtils.place_widget(self, textbox, Stylesheets.textbox,
                                 185, 380)
        textbox.returnPressed.connect(button.click)
        return textbox

    def add_name_selection_textbox(self, button: QPushButton) -> QLineEdit:
        textbox = QLineEdit(self)
        PagesUtils.place_widget(self, textbox, Stylesheets.textbox,
                                 780, 380)
        textbox.returnPressed.connect(button.click)
        return textbox
    
    def add_selected_pid_prompt_label(self) -> None:
        text = f'Selected PID:\n{self.selected_pid}'
        self.selected_pid_label = QLabel(text, self)
        PagesUtils.place_widget(self, self.selected_pid_label,
                                Stylesheets.valid_label,
                                0, 450, True)

    def create_invalid_pid_label(self) -> QLabel:
        label = QLabel('Unattachable PID', self)
        PagesUtils.place_widget(self, label, Stylesheets.error_label,
                                187, 490)
        label.hide()
        return label
    
    def create_invalid_name_label(self) -> QLabel:
        label = QLabel('Invalid Name\'s PIDs', self)
        PagesUtils.place_widget(self, label, Stylesheets.error_label,
                                775, 490)
        label.hide()
        return label
    
    def add_start_tracing_button(self) -> None:
        button = QPushButton('Start Tracing PID', self)
        PagesUtils.place_widget(self, button, Stylesheets.button,
                                0, 540, True)
        button.clicked.connect(self.start_tracing)

    def create_no_pid_selected_label(self) -> QLabel:
        label = QLabel('Attachment Failed', self)
        PagesUtils.place_widget(self, label, Stylesheets.error_label,
                                0, 580, True)
        label.hide()
        return label
    
    def add_file_execution_label(self) -> None:
        label = QLabel('OR\nEnter commandline execution:', self)
        PagesUtils.place_widget(self, label, Stylesheets.prompt_label,
                         50, 600)
        
    def add_file_execution_button(self) -> QPushButton:
        button = QPushButton('> Trace File', self)
        PagesUtils.place_widget(self, button, Stylesheets.button,
                                970, 695)
        button.clicked.connect(self.execute_file)
        return button

    def add_file_execution_textbox(self, button: QPushButton) -> QLineEdit:
        textbox = QLineEdit(self)
        PagesUtils.place_widget(self, textbox, Stylesheets.long_textbox,
                                 50, 700)
        textbox.returnPressed.connect(button.click)
        return textbox

    def create_name_scroll_area(self) -> QScrollArea:
        scroll_area = QScrollArea(self)
        scroll_area.setStyleSheet(Stylesheets.name_scroll_area)

        scroll_area.setWidgetResizable(True)

        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        scroll_area.setMaximumSize(150, 200)

        scroll_area.setGeometry(QRect(1020, 340,
                                      self.width(),
                                      self.height()))

        widget = QWidget(scroll_area)
        widget.setMinimumSize(50, 10)
        widget.setStyleSheet('background-color: transparent;')

        scroll_area.setWidget(widget)

        return scroll_area
    
    def add_button_to_scroll_area(self, button_text: str) -> None:
        buttons_widget = self.name_scroll_area.widget()
        button = QPushButton(button_text, buttons_widget)
        button.setStyleSheet(Stylesheets.scroll_area_button)
        
        buttons_amount = buttons_widget.minimumHeight() // 40
        button_y = 10 + 40 * buttons_amount

        button.setGeometry(10, button_y, 107, 35)
        button.show()

        button.clicked.connect(lambda: \
                               self.scroll_button_select_pid(button_text))

        new_height = 10 + (buttons_amount + 1) * 40
        buttons_widget.setMinimumHeight(new_height)

    def create_multiple_pids_label(self) -> QLabel:
        label = QLabel('Multiple PIDs Detected ►', self)
        PagesUtils.place_widget(self, label, Stylesheets.multiple_pids_label,
                                750, 490)
        label.hide()
        return label

    def scroll_button_select_pid(self, pid: str):
        self.reset_inputs()
        self.textboxes['pid'].setText(pid)
        self.select_by_pid()

    def clear_scroll_area(self) -> None:
        buttons = self.name_scroll_area.findChildren(QPushButton)
        buttons_widget = self.name_scroll_area.widget()

        for button in buttons:
            button.deleteLater()
            
            new_height = max(0, buttons_widget.minimumHeight() - 40)
            buttons_widget.setMinimumHeight(new_height)
            
    def select_by_pid(self) -> None:
        pid = self.textboxes['pid'].text()
        self.reset_inputs()
        if TracerUtils.is_pid_valid(pid):
            self.selected_pid = pid
        else:
            self.selected_pid = 'None'
            self.invalid_pid_timer = PagesUtils.show_label_for_seconds(
                self.invalid_pid_label, 5)

    def select_by_name(self) -> None:
        name = self.textboxes['name'].text()
        self.reset_inputs()
        pids = TracerUtils.get_valid_pids_by_name(name)

        if not pids:
            self.invalid_name_timer = PagesUtils.show_label_for_seconds(
                self.invalid_name_label, 5)
        elif len(pids) == 1:
            pid = pids[0]
            self.textboxes['pid'].setText(pid)
            self.select_by_pid()
        else:
            self.selected_pid = 'None'
            self.textboxes['pid'].setText('')

            self.multiple_pids_timer = PagesUtils.show_label_for_seconds(
                self.multiple_pids_label, 5)

            for pid in pids:
                self.add_button_to_scroll_area(pid)

    def reset_inputs(self) -> None:
        self.selected_pid = 'None'
        self.textboxes['pid'].setText('')
        self.textboxes['name'].setText('')
        self.clear_scroll_area()
        self.clear_timeouts()

    def clear_timeouts(self) -> None:
        PagesUtils.timer_timeout(self.invalid_pid_label,
                                 self.invalid_pid_timer)
        PagesUtils.timer_timeout(self.invalid_name_label,
                                 self.invalid_name_timer)
        PagesUtils.timer_timeout(self.attachment_fail_label,
                                 self.attachment_fail_timer)
        PagesUtils.timer_timeout(self.multiple_pids_label,
                                 self.multiple_pids_timer)
        
    def start_tracing(self):
        try:
            if not TracerUtils.is_pid_valid(self.selected_pid):
                raise TracerError
            TracerUtils.launch_tracer(True, self.selected_pid)
        except TracerError:
            self.attachment_fail_timer = PagesUtils.show_label_for_seconds(
                self.attachment_fail_label, 5
            )

    def execute_file(self):
        pass


class AboutPage(QWidget):
    def __init__(self, parent: QMainWindow = None, frontend: Frontend = None):
        super().__init__(parent)

        self.frontend = frontend

        PagesUtils.set_standard_configs(self)
        
        labels: list[tuple] = [
            ('About ProConq', 'title_label', 0, 60, True),
            (LargeTexts.about_content, 'text_label', 0, 160)
        ]

        PagesUtils.add_labels(self, labels)
