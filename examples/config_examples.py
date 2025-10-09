"""
Configuration examples for NocoDB Simple Client.

This example demonstrates different ways to configure the NocoDB client
using direct parameters, environment variables, and configuration files.
"""

import os
from pathlib import Path

from nocodb_simple_client import NocoDBClient, NocoDBConfig


def example_1_direct_parameters():
    """Example 1: Direct parameter configuration (simplest)."""
    print("\n" + "=" * 60)
    print("Example 1: Direct Parameters")
    print("=" * 60)

    client = NocoDBClient(
        base_url="https://app.nocodb.com",
        db_auth_token="your-api-token-here",
        timeout=30,
        max_redirects=3,
    )

    print("✓ Client initialized with direct parameters")
    client.close()


def example_2_environment_variables():
    """Example 2: Configuration from environment variables."""
    print("\n" + "=" * 60)
    print("Example 2: Environment Variables")
    print("=" * 60)

    # Set environment variables (in practice, these would be set in your shell or .env file)
    os.environ["NOCODB_BASE_URL"] = "https://app.nocodb.com"
    os.environ["NOCODB_API_TOKEN"] = "your-api-token-here"
    os.environ["NOCODB_TIMEOUT"] = "60.0"
    os.environ["NOCODB_MAX_RETRIES"] = "5"
    os.environ["NOCODB_DEBUG"] = "false"

    # Load configuration from environment
    config = NocoDBConfig.from_env()
    client = NocoDBClient(config)

    print("✓ Client initialized from environment variables")
    print(f"  Base URL: {config.base_url}")
    print(f"  Timeout: {config.timeout}s")
    print(f"  Max Retries: {config.max_retries}")
    client.close()


def example_3_config_object():
    """Example 3: Using NocoDBConfig object."""
    print("\n" + "=" * 60)
    print("Example 3: Config Object")
    print("=" * 60)

    # Create a config object with all options
    config = NocoDBConfig(
        base_url="https://app.nocodb.com",
        api_token="your-api-token-here",
        access_protection_auth="optional-protection-token",
        access_protection_header="X-BAUERGROUP-Auth",
        timeout=60.0,
        max_retries=5,
        backoff_factor=0.5,
        pool_connections=20,
        pool_maxsize=40,
        verify_ssl=True,
        user_agent="my-app/1.0",
        debug=False,
        log_level="INFO",
    )

    # Validate configuration
    config.validate()
    print("✓ Configuration validated")

    # Setup logging based on configuration
    config.setup_logging()

    # Initialize client with config
    client = NocoDBClient(config)

    print("✓ Client initialized with config object")
    print(f"  Configuration: {config.to_dict()}")
    client.close()


def example_4_config_from_json():
    """Example 4: Load configuration from JSON file."""
    print("\n" + "=" * 60)
    print("Example 4: JSON Configuration File")
    print("=" * 60)

    # Create example JSON config file
    config_data = """{
    "base_url": "https://app.nocodb.com",
    "api_token": "your-api-token-here",
    "timeout": 60.0,
    "max_retries": 5,
    "debug": false
}"""

    config_path = Path("nocodb_config.json")
    config_path.write_text(config_data)

    # Load configuration from JSON
    config = NocoDBConfig.from_file(config_path)
    client = NocoDBClient(config)

    print("✓ Client initialized from JSON configuration file")
    print(f"  Config file: {config_path}")

    client.close()

    # Cleanup
    config_path.unlink()
    print("  Cleaned up config file")


def example_5_custom_headers():
    """Example 5: Configuration with custom headers."""
    print("\n" + "=" * 60)
    print("Example 5: Custom Headers")
    print("=" * 60)

    config = NocoDBConfig(
        base_url="https://app.nocodb.com",
        api_token="your-api-token-here",
        access_protection_auth="custom-auth-token",
        access_protection_header="X-Custom-Protection",
        extra_headers={"X-Request-ID": "123456", "X-Client-Version": "1.0.0"},
    )

    client = NocoDBClient(config)

    print("✓ Client initialized with custom headers")
    print(f"  Headers: {client.headers}")

    client.close()


def example_6_production_config():
    """Example 6: Production-ready configuration."""
    print("\n" + "=" * 60)
    print("Example 6: Production Configuration")
    print("=" * 60)

    config = NocoDBConfig(
        base_url="https://production.nocodb.com",
        api_token="production-api-token",
        # Timeouts and retry configuration
        timeout=120.0,  # Longer timeout for production
        max_retries=3,
        backoff_factor=1.0,  # Exponential backoff between retries
        # Connection pooling for better performance
        pool_connections=50,
        pool_maxsize=100,
        # SSL verification (important for production!)
        verify_ssl=True,
        # Logging configuration
        debug=False,
        log_level="WARNING",  # Less verbose in production
        # Custom user agent for tracking
        user_agent="MyApp-Production/2.0",
    )

    # Validate before using in production
    config.validate()

    client = NocoDBClient(config)

    print("✓ Production client initialized")
    print(f"  Timeout: {config.timeout}s")
    print(f"  Connection Pool: {config.pool_connections}/{config.pool_maxsize}")
    print(f"  SSL Verification: {config.verify_ssl}")

    client.close()


def example_7_development_config():
    """Example 7: Development configuration."""
    print("\n" + "=" * 60)
    print("Example 7: Development Configuration")
    print("=" * 60)

    config = NocoDBConfig(
        base_url="http://localhost:8080",  # Local NocoDB instance
        api_token="development-token",
        # Development settings
        timeout=30.0,
        max_retries=1,  # Fail fast in development
        debug=True,  # Enable debug mode
        log_level="DEBUG",  # Verbose logging
        verify_ssl=False,  # May be needed for local development
        user_agent="MyApp-Development/1.0-dev",
    )

    # Setup debug logging
    config.setup_logging()

    client = NocoDBClient(config)

    print("✓ Development client initialized")
    print(f"  Base URL: {config.base_url}")
    print(f"  Debug Mode: {config.debug}")
    print(f"  Log Level: {config.log_level}")

    client.close()


def example_8_multiple_environments():
    """Example 8: Managing multiple environments."""
    print("\n" + "=" * 60)
    print("Example 8: Multiple Environments")
    print("=" * 60)

    environments = {
        "development": NocoDBConfig(
            base_url="http://localhost:8080", api_token="dev-token", debug=True
        ),
        "staging": NocoDBConfig(
            base_url="https://staging.nocodb.com", api_token="staging-token", debug=False
        ),
        "production": NocoDBConfig(
            base_url="https://production.nocodb.com",
            api_token="prod-token",
            debug=False,
            timeout=120.0,
        ),
    }

    # Select environment (e.g., from environment variable)
    current_env = os.getenv("APP_ENV", "development")
    config = environments[current_env]

    client = NocoDBClient(config)

    print(f"✓ Client initialized for '{current_env}' environment")
    print(f"  Base URL: {config.base_url}")
    print(f"  Debug: {config.debug}")

    client.close()


def main():
    """Run all configuration examples."""
    print("\n" + "=" * 60)
    print("NOCODB SIMPLE CLIENT - CONFIGURATION EXAMPLES")
    print("=" * 60)

    # Run examples
    example_1_direct_parameters()
    example_2_environment_variables()
    example_3_config_object()
    example_4_config_from_json()
    example_5_custom_headers()
    example_6_production_config()
    example_7_development_config()
    example_8_multiple_environments()

    print("\n" + "=" * 60)
    print("All configuration examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
