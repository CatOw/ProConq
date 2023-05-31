from __future__ import annotations
import sys
import importlib
import inspect

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar
)
from PyQt6.QtGui import (
    QAction,
    QGuiApplication
)

from PyQt6.QtCore import (
    QRect,
    Qt
)

from proconq.utils.constants import (
    Colors,
    Paths,
    TypeAliases,
    Literals
)
from proconq.utils.gui.stylesheets import Stylesheets
from proconq.src.backend.tracer.tracer_handler import TracerHandler


class FrontendUtils:
    @staticmethod
    def calculate_geometry() -> tuple[int, int, int, int]:
        """
        Calculates the position in which to place the Frontend window.
        The calculated position will be in the center of the primary screen.
        Supports scenarios with multiple screens available.
        """
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        x_offset = screen_geometry.x()
        x_offset += (screen_geometry.width() - Literals.WIDTH) // 2
        
        y_offset = screen_geometry.y()
        y_offset += (screen_geometry.height() - Literals.HEIGHT) // 2
        
        return x_offset, y_offset, Literals.WIDTH, Literals.HEIGHT
    
    @staticmethod
    def set_window_design(main_window: QMainWindow) -> QToolBar:
        """
        Sets the main window's design.
        Applies default design configurations.
        Sets background color and toolbar design.
        """
        main_window.setStyleSheet(f'background-color: {Colors.LIGHTSEAGREEN}')

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet(Stylesheets.toolbar_stylesheet)
        toolbar.setFixedHeight(Literals.TOOLBAR_HEIGHT)
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        main_window.addToolBar(toolbar)

        return toolbar
    
    @staticmethod
    def create_toolbar_pages(
        module_name: str,
        main_window: QMainWindow,
        toolbar_pages_order: list[str],
        frontend: Frontend
    ) -> dict[str, TypeAliases.WidgetSubclass]:
        """
        This function instantiates all the page objects
            in the purpose of adding to the toolbar buttons that show them.

        The toolbar only has buttons with the purpose
            of switching between pages.

        Pages exist inside pages modules.
        module_name is the name of the desired pages module.

        toolbar_pages_order is the order in which to sort
            the buttons that are added to the toolbar.
        """
        # Create a dictionary to contain pages in the format of
        # PageName: PageInstance
        pages: dict[str, TypeAliases.WidgetSubclass] = {}
        for pos, page_name in enumerate(toolbar_pages_order):
            pages[f'{page_name}Page'] = None

        # Import the module which contains all the Page classes
        module_path = f'{Paths.PAGES_PATH}.{module_name}'
        module = importlib.import_module(module_path)

        # Extract all the classes from the module
        classes = inspect.getmembers(module, inspect.isclass)

        for cls_name, cls in classes:
            # Confirm that the class originates in the module
            if cls.__module__ == module_path:
                # Instantiate the page instance
                page_instance: TypeAliases.WidgetSubclass
                page_instance = cls(parent=main_window, frontend=frontend)
                # Add the page to the dictionary
                pages[cls_name] = page_instance

        return pages


class Frontend:
    """
    Creates a main window.

    Whenever an instance of this class is created,
        a GUI window will automatically launch.

    The window will have a toolbar.
    Handles switching between pages.
    """

    def __init__(self, title: str = 'ProConq',
                 pages_module_name: str = 'base_window',
                 default_page_name: str = 'Home',
                 toolbar_pages_order: list[str] = ['Home', 'Tracer', 'About'],
                 tracer_handler: TracerHandler = None):
        self.tracer_handler = tracer_handler

        self.title = title

        # Create the window
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle(title)

        # Apply geometric configurations
        geometry = FrontendUtils.calculate_geometry()
        self.main_window.setGeometry(*geometry)
        self.main_window.setFixedSize(Literals.WIDTH, Literals.HEIGHT)
        
        # Set the design and obtain the toolbar object
        self.toolbar = FrontendUtils.set_window_design(self.main_window)

        # Instantiate all the pages
        self.pages: dict[str, TypeAliases.WidgetSubclass]
        self.pages = FrontendUtils.create_toolbar_pages(
            module_name=pages_module_name,
            main_window=self.main_window,
            toolbar_pages_order=toolbar_pages_order,
            frontend=self)
        
        # Load the pages buttons into the toolbar
        self.load_toolbar_buttons()

        # Show the main window and load its default page
        self.main_window.show()
        self.show_page(default_page_name)

    def show_page(self, page_name: str):
        """
        Activates a page's visibility.
        """
        # Modify the name to match the class recognition name
        page_name += 'Page'
        self.pages[page_name].setVisible(True)

        # Remove the visiblity of all other pages.
        for page, page_instance in self.pages.items():
            if page != page_name:
                page_instance.setVisible(False)

    def load_toolbar_buttons(self):
        """
        Load buttons into the toolbar.
        Creates the buttons as actions
            and applies a show_page click action to them.
        """
        # Iterate all pages
        for action_name, page_instance in self.pages.items():
            # Set visual button's name
            action_name = action_name.replace('Page', '')
            qaction = QAction(action_name, self.main_window)
            # Apply show_page click action
            qaction.triggered.connect(lambda checked,
                                      name=action_name: self.show_page(name))
            # Add button to toolbar
            self.toolbar.addAction(qaction)


def launch_default_ui():
    """
    Instantiates the PyQt Application, including the default frontend.
    Enters the PyQt Application execution loop.
    """
    app = QApplication(sys.argv)
    def_ui = Frontend()
    sys.exit(app.exec())
