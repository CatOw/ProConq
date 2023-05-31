from proconq.setup_logging import setup_logging
from proconq.src.frontend.frontend import launch_default_ui

def main():
    logger = setup_logging(__name__)
    logger.debug('Launching default UI')

    launch_default_ui()


if __name__ == '__main__':
    main()
