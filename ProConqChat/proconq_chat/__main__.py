import sys

from proconq_chat.setup_logging import setup_logging
from proconq_chat.src.server import launch_server
from proconq_chat.utils.constants import ServerConstants


def main():
    logger = setup_logging(__name__)

    port = ServerConstants.PORT

    try:
        if len(sys.argv) == 2:
            port = int(sys.argv[1])
        elif len(sys.argv) > 2:
            raise ValueError
    except ValueError:
        logger.critical('Invalid Input. Usage: py -m proconq_chat [port]')
        return

    logger.debug('Logging Setup successfully started.')
    logger.debug(f'Initializing Server on port {port}.')
    launch_server(port)
    

if __name__ == '__main__':
    main()
