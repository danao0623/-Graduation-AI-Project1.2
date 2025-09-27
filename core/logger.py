import os
import logging
import logging.handlers
from abc import ABC, abstractmethod

# AbstractLogger serves as a base class for implementing various types of loggers
# Subclasses must implement the `_add_handler` method to add specific logging handlers
class AbstractLogger(ABC):
    def __init__(self):
        """
        Initialize the AbstractLogger base class.
        """
        self.logger: logging.Logger = None

    def debug(self, message: str) -> None:
        """
        Log a debug message.

        :param message: The message to log.
        """
        if self.logger:
            self.logger.debug(f"DEBUG | {message}")        

    def info(self, message):
        """
        Log an informational message.

        :param message: The message to log.
        """
        if self.logger:
            self.logger.info(f"INFO | {message}")

    def warning(self, message):
        """
        Log a warning message.

        :param message: The message to log.
        """
        if self.logger:        
            self.logger.warning(f"WARNING | {message}")

    def error(self, message):
        """
        Log an error message.

        :param message: The message to log.
        """
        if self.logger:        
            self.logger.error(f"ERROR | {message}")
    
    def critical(self, message):
        """
        Log a critical message.

        :param message: The message to log.
        """
        if self.logger:        
            self.logger.critical(f"CRITICAL | {message}")

    def set_level(self, level):
        """
        Set the logging level.

        :param level: Logging level as a string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        """
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level in levels and self.logger:
            self.logger.setLevel(level)

    def flush(self):
        if self.logger:
            for handler in self.logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()

    @abstractmethod
    def _add_handler(self):
        """
        Abstract method to add specific logging handlers.
        Must be implemented by subclasses.
        """
        pass

# StreamLogger outputs logs to the console
class StreamLogger(AbstractLogger):
    def __init__(self, name: str, level: str):
        """
        Initialize a StreamLogger instance.

        :param name: Logger name.
        :param level: Logging level.
        """
        self.logger = logging.getLogger(name)
        self.logger.propagate = False        
        self.set_level(level)
        self._add_handler()

    def _add_handler(self):
        """
        Add a StreamHandler for console output.
        """
        if not self.logger.handlers:
            sh = logging.StreamHandler()
            sh.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(message)s'))
            self.logger.addHandler(sh)

# FileLogger writes logs to a specified file
class FileLogger(AbstractLogger):
    def __init__(self, name: str, level: str, filename: str):
        """
        Initialize a FileLogger instance.

        :param name: Logger name.
        :param level: Logging level.
        :param filename: Path to the log file.
        """
        self.logger = logging.getLogger(name)
        self.logger.propagate = False        
        self.set_level(level)
        self.filename = filename        
        self._add_handler()

    def _add_handler(self):
        """
        Add a FileHandler for file-based logging.
        """
        if not self.logger.handlers:
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            if not os.path.exists(self.filename):
                with open(self.filename, 'w') as file:
                    file.write('')
            fh = logging.FileHandler(filename=self.filename, encoding='utf-8')
            fh.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(message)s'))
            fh.setLevel(self.logger.level)
            self.logger.addHandler(fh)

    def get_log_path(self):
        return self.filename

# RotatingFileLogger rotates log files when they exceed a specified size
class RotatingFileLogger(AbstractLogger):
    def __init__(self, 
                 name: str, 
                 level: str, 
                 filename: str, 
                 maxBytes: int = 1024*1024*10, 
                 backupCount: int = 100):
        """
        Initialize a RotatingFileLogger instance.

        :param name: Logger name.
        :param level: Logging level.
        :param filename: Path to the log file.
        :param maxBytes: Maximum file size in bytes before rotation.
        :param backupCount: Number of backup files to keep.
        """
        self.logger = logging.getLogger(name)
        self.logger.propagate = False        
        self.set_level(level)
        self.filename = filename
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self._add_handler()

    def _add_handler(self):
        """
        Add a RotatingFileHandler for log rotation.
        """
        if not self.logger.handlers:
            os.makedirs(os.path.dirname(self.filename), exist_ok=True) 
            if not os.path.exists(self.filename):
                with open(self.filename, 'w') as file:
                    file.write('')               
            fh = logging.handlers.RotatingFileHandler(
                filename=self.filename,
                maxBytes=self.maxBytes,
                backupCount=self.backupCount,
                encoding='utf-8'
            )       
            fh.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(message)s'))
            fh.setLevel(self.logger.level)
            self.logger.addHandler(fh)

    def get_log_path(self):
        return self.filename            