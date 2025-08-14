"""
Simplified configuration management for MCP tools.

This module provides basic configuration loading for MCP tools using environment variables.
"""

import os
from typing import Any, Dict, Optional
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Environment-based configuration manager for MCP tools.
    
    This class handles configuration loading from environment variables and .env files.
    Supports automatic type conversion for boolean and numeric values.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            env_file: Path to the .env file (optional, defaults to .env in current directory)
        """
        self.env_file = env_file or ".env"
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables."""
        # Load .env file if it exists
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)
        else:
            logger.info(f"Environment file {self.env_file} not found, using system environment variables")
        
        # Start with default configuration
        self.config = self._get_default_config()
        
        # Override with environment variables
        self._load_from_env()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "name": "mcp-tool-template",
            "version": "1.0.0",
            "description": "Custom MCP tool template for local development and deployment",
            "protocol_version": "2024-11-05",
            "network": {
                "host": "0.0.0.0",
                "port": 8081
            },
            "logging": {
                "level": "INFO"
            },
            "debug": {
                "enabled": False
            }
        }
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "MCP_LOG_LEVEL": ("logging", "level"),
            "MCP_PORT": ("network", "port"),
            "MCP_HOST": ("network", "host"),
            "MCP_DEBUG": ("debug", "enabled"),
            "MCP_NAME": ("name",),
            "MCP_VERSION": ("version",),
            "MCP_DESCRIPTION": ("description",),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # Handle boolean values
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                # Handle numeric values
                elif value.isdigit():
                    value = int(value)
                self._set_nested_value(self.config, config_path, value)
    
    def _set_nested_value(self, config: Dict[str, Any], path: tuple, value: Any):
        """Set a nested value in the configuration dictionary."""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        current = self.config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get the complete configuration as a dictionary.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get a value directly from environment variables.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Environment variable value with automatic type conversion
        """
        value = os.getenv(key, default)
        if value is None:
            return default
        
        # Handle boolean values
        if isinstance(value, str) and value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        # Handle numeric values
        elif isinstance(value, str) and value.isdigit():
            return int(value)
        
        return value 