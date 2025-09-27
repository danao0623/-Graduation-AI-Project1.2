import os
import json
from core.config import Config
from core.logger import StreamLogger, FileLogger, RotatingFileLogger

class Environment:
    """
    Environment class provides methods to retrieve loggers and the system configuration.
    Automatically initializes required directories, configuration, and loggers.
    """
    log_files = {}
    loggers = {}
    project_root = None
    config = None
    
    @classmethod
    def initialize(cls):
        if cls.project_root is None:
            cls.project_root = os.path.dirname(os.path.dirname(__file__))
            cls.config_folder = os.path.join(cls.project_root, ".configs")
            cls.sqlite_folder = os.path.join(cls.project_root, ".sqlite")
            cls.home_folder = os.path.join(cls.project_root, ".home")
            cls.logs_folder = os.path.join(cls.project_root, ".logs")
            cls.config_file = os.path.join(cls.config_folder, 'sys_config.json')        
        cls._initialize_directories()
        cls._initialize_configuration()
        cls._initialize_loggers()           

    @classmethod
    def _initialize_directories(cls):
        """
        Ensure essential directories exist for the application's runtime environment.
        Creates each directory if it does not already exist, avoiding errors related to missing directories.
        """
        for folder in [cls.config_folder, cls.sqlite_folder, cls.home_folder, cls.logs_folder]:
            os.makedirs(folder, exist_ok=True)

    @classmethod
    def _initialize_configuration(cls):
        if not os.path.exists(cls.config_file):
            default_config = cls._default_configuration()
            with open(cls.config_file, 'w', encoding='utf-8') as file:
                json.dump(default_config, file, indent=4)
                file.flush()
                os.fsync(file.fileno())
        cls.config = Config(cls.config_file, os.path.join(cls.logs_folder, 'config.log'))
        cls.config.load()

    @classmethod
    def _initialize_loggers(cls):
        """
        Configure and instantiate loggers based on settings in the configuration file.
        Supports different types of loggers like StreamLogger, FileLogger, and RotatingFileLogger.
        """  
        entries = cls.retrieve("LOG_FILE") or {}
        for key, args in entries.items():
            if args["TYPE"] == 'StreamLogger':
                cls.loggers[key] = StreamLogger(args["NAME"], args["LEVEL"])
            elif args["TYPE"] == 'FileLogger':            
                cls.log_files[key] = os.path.join(cls.logs_folder, args["FILENAME"])
                cls.loggers[key] = FileLogger(args["NAME"], args["LEVEL"], cls.log_files[key])
            elif args["TYPE"] == 'RotatingFileLogger':  
                cls.log_files[key] = os.path.join(cls.logs_folder, args["FILENAME"]) 
                cls.loggers[key] = RotatingFileLogger(
                    args["NAME"], args["LEVEL"], cls.log_files[key],
                    args["MAX_BYTES"], args["BACKUP_COUNT"]
                )

    @classmethod
    def logger(cls, name):
        """
        Retrieve a logger by name if it exists, allowing for centralized logging throughout the application.
        :param name: The name of the logger to retrieve.
        :return: The logger object or None if not found.
        """
        if cls.config is None:
            cls.initialize()
        return cls.loggers.get(name)

    @classmethod
    def retrieve(cls, *keys):
        """
        Retrieve a nested configuration value by specifying a path through keys, handling complex configurations.
        :param keys: Sequence of keys leading to the desired configuration value.
        :return: The value from the configuration if the keys are valid, or None otherwise.
        """        
        if cls.config is None:
            cls.initialize()
        return cls.config.retrieve(*keys)

    @classmethod
    def set(cls, *keys, value):
        """
        Set or update a configuration value using a specified path of keys.
        :param keys: Sequence of keys leading to the desired configuration location.
        :param value: The new value to set at the specified location.
        """        
        if cls.config is None:
            cls.initialize()
        cls.config.set(*keys, value=value)

    @classmethod
    def remove(cls, *keys):
        """
        Remove a configuration value using a specified path of keys.
        :param keys: Sequence of keys leading to the desired configuration location.
        """            
        if cls.config is None:
            cls.initialize()
        cls.config.remove(*keys)

    @classmethod
    def reload_configuration(cls):
        if cls.config is None:
            cls.initialize()
        cls.config.load()
        logger = cls.loggers.get('SYSTEM')
        if logger:
            logger.warning("Configuration reloaded successfully")

    @classmethod
    def get_all_loggers(cls):
        """ Return a list of all initialized logger keys. """
        return list(cls.loggers.keys())

    @classmethod
    def _default_configuration(cls):
        """
        Provides a default configuration dictionary for initial setup or restoration of default settings.
        """        
        return {
            "LOG_FILE": {
                "SYSTEM": {
                    "TYPE": "FileLogger",
                    "NAME": "System",
                    "LEVEL": "WARNING",
                    "FILENAME": "system.log"   
                },
                "DATABASE": {
                    "TYPE": "FileLogger",
                    "NAME": "Database",
                    "LEVEL": "WARNING",
                    "FILENAME": "database.log"   
                },
                "LOGIN": {
                    "TYPE": "RotatingFileLogger",
                    "NAME": "Login",
                    "LEVEL": "INFO",
                    "FILENAME": "login.log",
                    "MAX_BYTES": 1024*1024*128, 
                    "BACKUP_COUNT": 100   
                },
                "REGISTER": {
                    "TYPE": "FileLogger",
                    "NAME": "Register",
                    "LEVEL": "INFO",
                    "FILENAME": "register.log"  
                },
                "FORGOT_PASSWORD": {
                    "TYPE": "FileLogger",
                    "NAME": "ForgotPassword",
                    "LEVEL": "WARNING",
                    "FILENAME": "forgot_password.log"  
                },
                "ACCESS_CONTROL": {
                    "TYPE": "RotatingFileLogger",
                    "NAME": "AccessControl",
                    "LEVEL": "INFO",
                    "FILENAME": "access_control.log",
                    "MAX_BYTES": 1024*1024*128, 
                    "BACKUP_COUNT": 100                     
                },                
                "FILE_MANAGER": {
                    "TYPE": "FileLogger",
                    "NAME": "FileManager",
                    "LEVEL": "WARNING",
                    "FILENAME": "file_manager.log"
                }
            },
            
            "DATABASE": {
                "SYSTEM": "sqlite+aiosqlite:///.sqlite/system.db",
            },

        }

