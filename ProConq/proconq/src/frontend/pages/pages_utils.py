from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QLineEdit,
    QPushButton
)
from PyQt6.QtCore import (
    QRect,
    QTimer
)

from proconq.utils.constants import (
    TypeAliases,
    Literals
)
from proconq.utils.gui.stylesheets import Stylesheets


class PagesUtils:
    """
    Useful functions that many Page objects can make use of.
    """

    @staticmethod
    def set_standard_configs(page_object: TypeAliases.WidgetSubclass) -> None:
        """
        Applies standard configurations to a page object.
        """
        page_object.move(0, Literals.TOOLBAR_HEIGHT)
        page_object.resize(Literals.WIDTH,
                    Literals.HEIGHT - Literals.TOOLBAR_HEIGHT)

        page_object.setVisible(False)

    @staticmethod
    def cal_widget_centered_x(parent: QWidget,
                              widget: QLabel | QLineEdit | QPushButton) -> int:
        """
        Calculates the X position for the center of the window.
        """
        screen_width = Literals.WIDTH
        parent_x_offset = parent.pos().x()
        label_width = widget.width()
        return (screen_width - parent_x_offset - label_width) // 2


    @staticmethod
    def cal_widget_centered_y(parent: QWidget,
                              widget: QLabel | QLineEdit | QPushButton) -> int:
        """
        Calculates the Y position for the center of the window.
        """
        screen_height = Literals.HEIGHT
        parent_y_offset = parent.pos().y()
        label_height = widget.height()
        return (screen_height - parent_y_offset - label_height) // 2

    @staticmethod
    def place_widget(page: TypeAliases.WidgetSubclass,
                     widget: QLabel | QLineEdit | QPushButton,
                     stylesheet: str, x: int, y: int,
                     center_x: bool = False, center_y: bool = False
    ) -> None:
        """
        Places a widget on a page object.
        Compatible with Labels, Textboxes and Buttons.
        """
        widget.setStyleSheet(stylesheet)
        widget.setFixedSize(widget.sizeHint())

        x -= page.pos().x()
        y -= page.pos().y()

        if center_x:
            x = PagesUtils.cal_widget_centered_x(page, widget)
        if center_y:
            y = PagesUtils.cal_widget_centered_y(page, widget)

        widget.setGeometry(QRect(x, y, page.width(),
                                        widget.height()))

    @staticmethod
    def timer_timeout(label: QLabel, timer: QTimer) -> None:
        """
        Timeout a timer before it finishes.
        """
        label.hide()
        timer.stop()

    @staticmethod
    def show_label_for_seconds(label: QLabel, seconds: int) -> QTimer:
        """
        Instantiates a timer to show a label for a period of time.
        Can be timed out before timer finishes.
        """
        label.show()
        timer = QTimer()
        timer.timeout.connect(lambda: PagesUtils.timer_timeout(label, timer))
        timer.start(seconds * 1000)
        return timer

    @staticmethod
    def add_label(page_object: TypeAliases.WidgetSubclass,
                  label_text: str, stylesheet_name: str,
                  x: int, y: int, center_x: bool = False,
                  center_y: bool = False) -> None:
        """
        Adds a label to a page object.
        Takes its necessary configurations.
        """
        stylesheet = getattr(Stylesheets, stylesheet_name)

        label = QLabel(label_text, page_object)
        PagesUtils.place_widget(page_object, label, stylesheet,
                                x, y, center_x, center_y)

    @staticmethod
    def add_labels(page_object: TypeAliases.WidgetSubclass,
                   labels: list[tuple]) -> None:
        """
        Given a page object and a list of labels to add,
        this function will extract the label tuple data
        and add all labels in the list to the page object.
        """
        for label in labels:
            PagesUtils.add_label(page_object, *label)
