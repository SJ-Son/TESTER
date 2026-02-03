import logging


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance with the given name.

    Args:
        name (str): Logger name, typically __name__ of the calling module.

    Returns:
        logging.Logger: A configured logger instance.
    """
    return logging.getLogger(name)
