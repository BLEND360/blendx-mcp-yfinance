# MCP Tool Template

This GitHub template provides a foundation for creating custom tools that can be packaged and deployed as Model Context Protocol (MCP) components for local development and containerized deployment.

## 🚀 Quick Start

1. **Use this template** - Click "Use this template" to create a new repository
2. **Set up environment** - Copy `env.example` to `.env` and configure your variables
3. **Customize your tools** - Modify the tool logic in `src/mcp_server.py` or add new tools
4. **Test locally** - Run `pytest` to verify your implementation
5. **Run MCP server** - Execute `python src/mcp_server.py --port=8081`
6. **Deploy with Docker** - Use the provided Docker configuration

## 📁 Project Structure

```
├── src/
│   ├── mcp_server.py   # Main MCP server implementation with all tools
│   ├── config/         # Configuration management
│   └── utils/          # Shared utilities
├── tests/              # Test suite
├── docs/               # Documentation
├── examples/           # Usage examples
├── Dockerfile         # Container configuration
├── pyproject.toml     # Python project configuration
├── env.example        # Environment variables template
```

## 🛠️ Features

- **MCP Integration**: Built-in support for Model Context Protocol
- **Docker Ready**: Optimized for containerized deployment
- **Testing Framework**: Comprehensive test suite with pytest
- **Modern Python**: Uses `uv` and `pyproject.toml` for dependency management
- **Configuration Management**: Environment-based configuration system
- **Documentation**: Auto-generated API documentation

## 📋 Prerequisites

- Python 3.10+
- Docker (optional, for containerized deployment)
- GitHub account

## 🔧 Development

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd <your-repo-name>

# Install dependencies using uv
uv sync

# Run tests
pytest

# Start local development server
python src/mcp_server.py --port=8081
```

### Adding a New Tool

1. Add a new tool function in `src/mcp_server.py` using the `@mcp.tool()` decorator
2. Implement the tool logic following the MCP interface
3. Add tests in `tests/test_mcp_server.py`
4. Update documentation

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_mcp_server.py

# Run with coverage
pytest --cov=src
```

## 🔐 Configuration Management

### Environment Variables Setup

The project uses a robust configuration management system that supports environment variables for all settings. This is especially useful when your tools need API keys or other sensitive configuration.

#### 1. Basic Setup

```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your actual values
nano .env
```

#### 2. Using Config Manager in Your Tools

When you need to access environment variables in your tools (especially for API keys), use the `ConfigManager`:

```python
from src.config.config_manager import ConfigManager

# Initialize config manager
config = ConfigManager()

# Access environment variables
api_key = config.get_env('OPENAI_API_KEY')
host = config.get_env('MCP_HOST', 'localhost')
port = config.get_env('MCP_PORT', 8081)
debug = config.get_env('MCP_DEBUG', False)
```

#### 3. Example: Adding API Key Support to a Tool

```python
from mcp.server.fastmcp import FastMCP
from src.config.config_manager import ConfigManager
import openai

# Initialize config manager
config = ConfigManager()

@mcp.tool()
async def ai_text_generator(prompt: str) -> str:
    """Generate text using OpenAI API.
    
    Args:
        prompt: The text prompt to generate from
        
    Returns:
        Generated text from OpenAI
    """
    try:
        # Get API key from environment
        api_key = config.get_env('OPENAI_API_KEY')
        if not api_key:
            return json.dumps({"error": "OPENAI_API_KEY not configured"})
        
        # Configure OpenAI client
        openai.api_key = api_key
        
        # Make API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.dumps({
            "generated_text": response.choices[0].message.content,
            "model": "gpt-3.5-turbo"
        })
        
    except Exception as e:
        return json.dumps({"error": f"Text generation failed: {str(e)}"})
```

#### 4. Available Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI services | - | For AI tools |
| `MCP_HOST` | Server host address | localhost | No |
| `MCP_PORT` | Server port number | 8081 | No |
| `MCP_NAME` | Server name | "MCP Tool Template" | No |
| `MCP_VERSION` | Server version | "1.0.0" | No |
| `MCP_DESCRIPTION` | Server description | Custom description | No |
| `MCP_LOG_LEVEL` | Log level (DEBUG, INFO, etc.) | INFO | No |
| `MCP_DEBUG` | Enable debug mode | false | No |

#### 5. Advanced Configuration

The `ConfigManager` supports nested configuration and automatic type conversion:

```python
# Get nested configuration
log_level = config.get('logging.level', 'INFO')
network_host = config.get('network.host', '0.0.0.0')

# Automatic type conversion
debug_enabled = config.get_env('MCP_DEBUG', False)  # Returns boolean
port_number = config.get_env('MCP_PORT', 8081)      # Returns integer
```

## 🚀 Deployment

### Local Testing

```bash
# Run the server locally
python src/mcp_server.py --port=8081

# Test the health endpoint
curl http://localhost:8081/health
```

### Docker Deployment

```bash
# Build Docker image
docker build -t mcp-tool-template .

# Run with Docker
docker run -d -p 8081:8081 mcp-tool-template

# Test the container
curl http://localhost:8081/health
```

### Environment Variables in Docker

For Docker deployment, you can pass environment variables:

```bash
# Run with custom environment variables
docker run -d -p 8081:8081 \
  -e OPENAI_API_KEY=your_api_key_here \
  -e MCP_DEBUG=true \
  mcp-tool-template
```

## 📚 Documentation

- [MCP Specification](https://modelcontextprotocol.io/)
- [Tool Development Guide](docs/mcp_usage.md)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue for bugs or feature requests
- Check the [documentation](docs/) for detailed guides
- Join our community discussions

---

