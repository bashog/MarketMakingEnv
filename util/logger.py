import logging
import os

def setup_logger(log_filename='test.log'):
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    log_file = os.path.join(log_directory, log_filename)
    logger = logging.getLogger('Debuger')
    logger.setLevel(logging.DEBUG) 

    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(message)s')

    if logger.handlers:
        logger.handlers = []  # clear existing handlers

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger

class DummyLogger:
    def debug(self, msg, *args, **kwargs): pass
    def info(self, msg, *args, **kwargs): pass
    def warning(self, msg, *args, **kwargs): pass
    def error(self, msg, *args, **kwargs): pass
    def critical(self, msg, *args, **kwargs): pass