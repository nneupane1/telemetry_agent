"""
App Logger Utility
------------------
Provides a reusable logging interface for services, agents, and routers in the platform.
"""

import logging

class AppLogger:
    """
    AppLogger

    Singleton-style wrapper for Python's built-in logging.
    Allows standardized logging across all backend modules.
    """
    _logger = None

    @classmethod
    def get_logger(cls, name: str = "genai-platform") -> logging.Logger:
        """
        Returns a logger instance configured for the platform.

        Args:
            name (str): Logger name.

        Returns:
            logging.Logger: Configured logger instance.
        """
        if cls._logger is None:
            cls._logger = logging.getLogger(name)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            cls._logger.addHandler(handler)
            cls._logger.setLevel(logging.INFO)
        return cls._logger

# Example usage
if __name__ == "__main__":
    logger = AppLogger.get_logger()
    logger.info("AppLogger initialized and ready.")
