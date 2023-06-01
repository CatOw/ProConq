import logging

from ccui.utils.constants import Paths


def setup_logging(logger_name: str) -> logging.Logger:
    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Create file handler
    file_path = Paths.LOGGING / f'{logger_name}.log'
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(logging.DEBUG)

    # Create formatter and apply to file handler
    logging_format = '%(levelname)s %(asctime)s %(name)s %(funcName)s # %(message)s'
    formatter = logging.Formatter(logging_format)
    file_handler.setFormatter(formatter)

    # Apply file handler to logger
    logger.addHandler(file_handler)

    return logger
