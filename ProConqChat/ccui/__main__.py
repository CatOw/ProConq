import importlib
import ccui.main
from ccui.main import launch
from ccui.utils.errors import (
    ExitCCUIRestart,
    ExitCCUIShutdown,
    ExitCCUIReload,
)
from ccui.setup_logging import setup_logging


def main():
    logger = setup_logging(__name__)

    while True:
        try:
            launch()
        except ExitCCUIShutdown:
            logger.debug('Shutting down.')
            break
        except ExitCCUIRestart:
            logger.debug('Restarted.')
            importlib.reload(ccui.main)
        except ExitCCUIReload:
            logger.debug('Reloaded')


if __name__ == '__main__':
    main()
