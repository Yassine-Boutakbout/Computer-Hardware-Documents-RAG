import os
import sys
import json
import logging as std_logger
from loguru import logger as loguru_logger


# loading config file
config = json.load(open("config/config.json"))


class Logger:
    """
    Singleton to access a configured logger.
    * For local prototyping / development the Loguru logger is used.
    """
    __loguru_instance = None # For prod / dev – Loguru

    @classmethod
    def get_instance(cls):
        """
        Return the singleton logger.
        """
        # ---------- PROTOTYPE / DEV ----------
        if cls.__loguru_instance is None:
            cls.__loguru_instance = cls.__init_loguru_logger()
        return cls.__loguru_instance

    # --------------------------------------------------------------------
    #  Loguru logger (used for local prototyping / dev)
    # --------------------------------------------------------------------
    @staticmethod
    def __init_loguru_logger():
        """
        Configure Loguru with:

        * Colored console output
        * Optional file handler (via environment var LOG_FILE)
        * Environment / version info in the message
        """
        log_level = Logger.__log_level(config['LOGS']['LOGGING_LEVEL'])

        # Clear any pre‑existing handlers
        loguru_logger.remove()

        # Basic console handler – colored by level
        loguru_logger.add(
            sink=sys.stderr,  # stdout
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level}</level> | "
                   "<cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
        )

        # Optional file handler – useful for prototyping
        log_file = config.get("LOGS", {}).get("LOG_FILE", "")  # e.g. LOG_FILE=./app.log
        if log_file:
            loguru_logger.add(
                sink=log_file,
                level=log_level,
                rotation="500 MB",
                compression="zip",
                format="{time} | {level} | {name}:{function}:{line} - {message}",
            )

        # Add a context variable with env/version info
        ENVIRONMENT = config.get("ENVIRONMENT", "")
        VERSION = config.get("VERSION", "")
        if ENVIRONMENT:
            loguru_logger.bind(environment=ENVIRONMENT)
        if VERSION:
            loguru_logger.bind(version=VERSION)

        return loguru_logger

    # --------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------
    @staticmethod
    def __log_level(log_level_string: str) -> int:
        """
        Convert string level → std‑lib level int.

        The same mapping is used for Loguru (`level=log_level` accepts the
        std‑lib numeric values).
        """
        mapping = {
            "debug": std_logger.DEBUG,
            "info": std_logger.INFO,
            "warning": std_logger.WARN,
            "error": std_logger.ERROR,
            "critical": std_logger.CRITICAL,
        }
        return mapping.get(log_level_string.lower(), std_logger.DEBUG)
