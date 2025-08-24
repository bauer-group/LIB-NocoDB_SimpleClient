"""Configuration management for NocoDB Simple Client.

MIT License

Copyright (c) BAUER GROUP

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class NocoDBConfig:
    """Configuration settings for NocoDB client.

    Attributes:
        base_url: The base URL of the NocoDB instance
        api_token: The API authentication token
        access_protection_auth: Optional access protection token
        access_protection_header: Custom header name for access protection
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff factor for retries
        pool_connections: Number of connection pools
        pool_maxsize: Maximum size of connection pool
        verify_ssl: Whether to verify SSL certificates
        user_agent: Custom user agent string
        debug: Enable debug mode
        log_level: Logging level
    """

    base_url: str
    api_token: str
    access_protection_auth: str | None = None
    access_protection_header: str = "X-BAUERGROUP-Auth"
    timeout: float = 30.0
    max_retries: int = 3
    backoff_factor: float = 0.3
    pool_connections: int = 10
    pool_maxsize: int = 20
    verify_ssl: bool = True
    user_agent: str = "nocodb-simple-client"
    debug: bool = False
    log_level: str = "INFO"
    extra_headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls, env_prefix: str = "NOCODB_") -> "NocoDBConfig":
        """Create configuration from environment variables.

        Args:
            env_prefix: Prefix for environment variable names

        Returns:
            NocoDBConfig instance populated from environment

        Raises:
            ValueError: If required environment variables are missing
        """
        base_url = os.getenv(f"{env_prefix}BASE_URL")
        api_token = os.getenv(f"{env_prefix}API_TOKEN") or os.getenv(f"{env_prefix}TOKEN")

        if not base_url:
            raise ValueError(f"Environment variable {env_prefix}BASE_URL is required")
        if not api_token:
            raise ValueError(
                f"Environment variable {env_prefix}API_TOKEN or {env_prefix}TOKEN is required"
            )

        return cls(
            base_url=base_url,
            api_token=api_token,
            access_protection_auth=os.getenv(f"{env_prefix}PROTECTION_AUTH"),
            access_protection_header=os.getenv(
                f"{env_prefix}PROTECTION_HEADER", "X-BAUERGROUP-Auth"
            ),
            timeout=float(os.getenv(f"{env_prefix}TIMEOUT", "30.0")),
            max_retries=int(os.getenv(f"{env_prefix}MAX_RETRIES", "3")),
            backoff_factor=float(os.getenv(f"{env_prefix}BACKOFF_FACTOR", "0.3")),
            pool_connections=int(os.getenv(f"{env_prefix}POOL_CONNECTIONS", "10")),
            pool_maxsize=int(os.getenv(f"{env_prefix}POOL_MAXSIZE", "20")),
            verify_ssl=os.getenv(f"{env_prefix}VERIFY_SSL", "true").lower() == "true",
            user_agent=os.getenv(f"{env_prefix}USER_AGENT", "nocodb-simple-client"),
            debug=os.getenv(f"{env_prefix}DEBUG", "false").lower() == "true",
            log_level=os.getenv(f"{env_prefix}LOG_LEVEL", "INFO"),
        )

    @classmethod
    def from_file(cls, config_path: Path) -> "NocoDBConfig":
        """Load configuration from a file.

        Args:
            config_path: Path to configuration file (JSON, YAML, or TOML)

        Returns:
            NocoDBConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is unsupported
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        suffix = config_path.suffix.lower()

        if suffix == ".json":
            import json

            with open(config_path) as f:
                data = json.load(f)
        elif suffix in [".yaml", ".yml"]:
            try:
                import yaml

                with open(config_path) as f:
                    data = yaml.safe_load(f)
            except ImportError as e:
                raise ValueError("PyYAML is required to load YAML configuration files") from e
        elif suffix == ".toml":
            try:
                import tomli

                with open(config_path, "rb") as f:
                    data = tomli.load(f)
            except ImportError as e:
                raise ValueError("tomli is required to load TOML configuration files") from e
        else:
            raise ValueError(f"Unsupported configuration file format: {suffix}")

        return cls(**data)

    def setup_logging(self) -> None:
        """Configure logging based on configuration settings."""
        level = getattr(logging, self.log_level.upper(), logging.INFO)

        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            if not self.debug
            else "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )

        logging.basicConfig(level=level, format=format_string, datefmt="%Y-%m-%d %H:%M:%S")

        # Set specific logger levels
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        if not self.debug:
            logging.getLogger("requests").setLevel(logging.WARNING)

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.base_url:
            raise ValueError("base_url cannot be empty")
        if not self.api_token:
            raise ValueError("api_token cannot be empty")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.backoff_factor < 0:
            raise ValueError("backoff_factor cannot be negative")
        if self.pool_connections <= 0:
            raise ValueError("pool_connections must be positive")
        if self.pool_maxsize <= 0:
            raise ValueError("pool_maxsize must be positive")

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "base_url": self.base_url,
            "api_token": "***" if self.api_token else None,  # Mask sensitive data
            "access_protection_auth": "***" if self.access_protection_auth else None,
            "access_protection_header": self.access_protection_header,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "backoff_factor": self.backoff_factor,
            "pool_connections": self.pool_connections,
            "pool_maxsize": self.pool_maxsize,
            "verify_ssl": self.verify_ssl,
            "user_agent": self.user_agent,
            "debug": self.debug,
            "log_level": self.log_level,
            "extra_headers": self.extra_headers,
        }


def load_config(
    config_path: Path | None = None, env_prefix: str = "NOCODB_", use_env: bool = True
) -> NocoDBConfig:
    """Load configuration from file or environment variables.

    Args:
        config_path: Path to configuration file (optional)
        env_prefix: Prefix for environment variables
        use_env: Whether to use environment variables as fallback

    Returns:
        NocoDBConfig instance

    Raises:
        ValueError: If configuration cannot be loaded
    """
    if config_path and config_path.exists():
        return NocoDBConfig.from_file(config_path)
    elif use_env:
        return NocoDBConfig.from_env(env_prefix)
    else:
        raise ValueError("No configuration source available")
