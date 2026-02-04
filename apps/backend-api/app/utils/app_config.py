"""
App Config Utility
------------------
Provides a centralized object-oriented interface for application configuration,
including loading from environment variables and (optionally) .env files.
"""

import os
from typing import Optional

class AppConfig:
    """
    AppConfig

    Centralizes application configuration and secrets management.
    This class can be extended to support .env files, secret managers, etc.
    """
    # Example default config values (you can expand this as needed)
    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DATABRICKS_URI: Optional[str] = os.getenv("DATABRICKS_URI")
    EMAIL_SMTP_SERVER: Optional[str] = os.getenv("EMAIL_SMTP_SERVER")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM")

    @classmethod
    def reload(cls):
        """
        Reloads all environment variables (useful if env changes at runtime).
        """
        cls.ENV = os.getenv("ENV", "development")
        cls.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        cls.DATABRICKS_URI = os.getenv("DATABRICKS_URI")
        cls.EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
        cls.EMAIL_FROM = os.getenv("EMAIL_FROM")

    @classmethod
    def summary(cls) -> str:
        """
        Returns a human-readable summary of the active config (excluding secrets).
        """
        return (
            f"ENV={cls.ENV}, LOG_LEVEL={cls.LOG_LEVEL}, "
            f"DATABRICKS_URI={'set' if cls.DATABRICKS_URI else 'unset'}, "
            f"EMAIL_SMTP_SERVER={'set' if cls.EMAIL_SMTP_SERVER else 'unset'}, "
            f"EMAIL_FROM={cls.EMAIL_FROM}"
        )

# Example usage
if __name__ == "__main__":
    print("Current Config:", AppConfig.summary())
