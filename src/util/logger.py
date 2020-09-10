from datetime import datetime

levels = ['TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']

level_stdout = 2
level_file = 0

logfile = None

nowstrfdt = lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
nowstrft = lambda: datetime.now().strftime('%H:%M:%S')
use_file = lambda: not logfile is None

def log_stdout(level, message):
    """
    Logs to stdout

    Args:
        level (int): The severity of the log
        message (str): The message
    """
    if level >= level_stdout:
        print(f'{nowstrft()} [{levels[level]}]: {message}')

def log_file(level, message):
    """
    Logs to a file

    Args:
        level (int): The severity of the log
        message (str): The message
    """
    if level >= level_file:
        logfile.write(f'{nowstrft()} [{levels[level]}]: {message}\n')

def trace(message):
    if use_file():
        log_file(0, message)
    log_stdout(0, message)

def debug(message):
    if use_file():
        log_file(1, message)
    log_stdout(1, message)

def info(message):
    if use_file():
        log_file(2, message)
    log_stdout(2, message)

def warn(message):
    if use_file():
        log_file(3, message)
    log_stdout(3, message)

def error(message):
    if use_file():
        log_file(4, message)
    log_stdout(4, message)

def fatal(message):
    if use_file():
        log_file(5, message)
    log_stdout(5, message)
