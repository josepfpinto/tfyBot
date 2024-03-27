import sys
import logging


def configure_logging(name):
    """Function to configure logging"""
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent logger from propagating messages to ancestor loggers
    logger.propagate = False

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Add handler to the logger
    logger.addHandler(handler)
    return logger
