from proconq.utils.constants import Colors


class Stylesheets:
    toolbar_stylesheet = f'''
        QToolBar {{
            background-color: {Colors.TEAL};
        }}

        QToolButton {{
            color: white;
            font-weight: bold;
            font-size: 18px;
            background-color: transparent;
        }}

        QToolButton:hover {{
            background-color: {Colors.LIGHTSEAGREEN};
        }}

        QToolButton:pressed {{
            background-color: {Colors.DARKSLATEGRAY};
        }}
    '''
    title_label = f'''
        QLabel {{
            background-color: transparent;
            color: {Colors.AQUAMARINE};
            font-size: 50px;
            font-weight: bold;
            padding: 10px;
            border: 4px solid {Colors.AQUAMARINE};
            border-radius: 10px;
        }}
    '''
    text_label = f'''
        QLabel {{
            background-color: transparent;
            color: {Colors.AQUAMARINE};
            font-size: 30px;
            font-weight: bold;
            padding: 10px;
        }}
    '''
    prompt_label = f'''
        QLabel {{
            background-color: transparent;
            color: {Colors.AQUAMARINE};
            font-size: 25px;
            font-weight: bold;
            padding: 10px;
        }}
    '''
    valid_label = f'''
        QLabel {{
            background-color: transparent;
            color: {Colors.LIME};
            font-size: 25px;
            font-weight: bold;
            padding: 10px;
        }}
    '''
    error_label = f'''
        QLabel {{
            background-color: transparent;
            color: {Colors.ROSE};
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
        }}    
    '''
    button = f'''
        QPushButton {{
            background-color: {Colors.TEAL};
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
        }}

        QPushButton:hover {{
            background-color: {Colors.MEDIUMAQUAMARINE};
            color: {Colors.CADETBLUE}
        }}

        QPushButton:pressed {{
            background-color: {Colors.DARKSLATEGRAY};
            color: {Colors.CADETBLUE}
        }}
    '''
    textbox = f'''
        QLineEdit {{
            background-color: white;
            color: black;
            font-size: 20px;
            font-weight: bold;
            padding: 3px;
            border-radius: 5px;
            border: 2px solid {Colors.TEAL};
            min-height: 20px;
        }}
    '''
    long_textbox = f'''
        QLineEdit {{
            background-color: white;
            color: black;
            font-size: 20px;
            font-weight: bold;
            padding: 3px;
            border-radius: 5px;
            border: 2px solid {Colors.TEAL};
            min-height: 20px;
            width: 900px;
        }}
    '''
    name_scroll_area = f'''
        QScrollArea {{
            background-color: {Colors.DARKSLATEGRAY};
            border: 5px solid {Colors.TEAL};
            border-radius: 10px;
        }}
    '''
    scroll_area_button = f'''
        QPushButton {{
            background-color: {Colors.TEAL};
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 5px;
        }}

        QPushButton:hover {{
            background-color: {Colors.MEDIUMAQUAMARINE};
            color: {Colors.CADETBLUE}
        }}

        QPushButton:pressed {{
            background-color: {Colors.DARKSLATEGRAY};
            color: {Colors.CADETBLUE}
        }}
    '''
    multiple_pids_label = f'''
        QLabel {{
            background-color: transparent;
            color: {Colors.VIOLET};
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
        }}
    '''
    small_textbox = f'''
        QLineEdit {{
            background-color: white;
            color: black;
            font-size: 20px;
            font-weight: bold;
            padding: 3px;
            border-radius: 5px;
            border: 2px solid {Colors.TEAL};
            min-height: 20px;
            width: 140px;
        }}
    '''
    small_textbox_locked = f'''
        QLineEdit {{
            background-color: {Colors.DARKSLATEGRAY};
            color: white;
            font-size: 20px;
            font-weight: bold;
            padding: 3px;
            border-radius: 5px;
            border: 2px solid {Colors.TEAL};
            min-height: 20px;
            width: 140px;
        }}
    '''