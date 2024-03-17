import logging


LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

LOG_FORMATTER = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S"
)
CONSOLE_FORMATTER = logging.Formatter("%(levelname)s - %(name)s - %(message)s")


def setup_logger(name, log_level="INFO", log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))

    # Remove all handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CONSOLE_FORMATTER)
    logger.addHandler(console_handler)

    # Add file handler if log file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(LOG_FORMATTER)
        logger.addHandler(file_handler)

    return logger
