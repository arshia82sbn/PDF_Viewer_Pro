import logging
import threading

class LogManager:
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with LogManager._lock:
                cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance
    def __init__(self):
        if LogManager._initialized:
            return
        with (LogManager._lock):
            if LogManager._initialized:
                return

            # Create logger
            self.logger = logging.getLogger("PDF_Viewer_Pro")
            self.logger.setLevel(logging.DEBUG)

            # Create formatter (ALWAYS defined)
            formatter = logging.Formatter( "%(asctime)s - %(name)s -"
                                           " %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
                                           datefmt='%Y-%m-%d %H:%M:%S' )
            # Console handler
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(formatter)

            # Add handler if not already added
            if not self.logger.handlers:
                self.logger.addHandler(consoleHandler)
            LogManager._initialized = True

    def get_logger(self):
        return self.logger

def get_logger():
    '''Global shortcut logger'''
    return LogManager().get_logger()