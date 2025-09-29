import logging
import os
import sys
from datetime import datetime



DEFAULT_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

TRACE_LEVEL_NUM = 10

# LOG_COLORS = {
#     'TRAC': 'white',
#     'SAVE': 'blue',
#     'NOTI': 'bold_cyan',
#     'DEBUG': 'cyan',
#     'INFO': 'green',
#     'WARN': 'yellow',
#     'ERROR': 'red',
#     'CRITICAL': 'bold_red',
# }

def _get_formatter():
    return logging.Formatter(DEFAULT_FORMAT, datefmt=DATE_FORMAT)

def _add_console_handler(logger, level):
    handler = (logging.StreamHandler(sys.stdout))
    handler.setFormatter(_get_formatter())
    handler.setLevel(level)
    logger.addHandler(handler)


def setup_logger(name="app_logger",log_dir="logs",log_level=logging.DEBUG,to_console=True,to_file=True):
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(log_level)
    logger.propagate = False

    if to_file:
        # timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        file_path = os.path.join(log_dir, f"{name}.log")
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setFormatter(_get_formatter())
        file_handler.setLevel(TRACE_LEVEL_NUM)
        logger.addHandler(file_handler)

    if to_console:
        _add_console_handler(logger, log_level)

    return logger


# --- Global registry with short names ---
_active_logger = None

def set_global_logger(logger):
    global _active_logger
    _active_logger = logger

def get_global_logger():
    return _active_logger or logging.getLogger("default_logger")
