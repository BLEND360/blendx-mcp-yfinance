# MCP Server Usage Guide

This guide explains how to use the MCP (Model Context Protocol) server template for creating custom tools that can be deployed locally or in containers.

## Overview

The MCP server provides a standardized way to create tools that can be integrated with AI models and deployed locally or in containers. The server uses Server-Sent Events (SSE) for real-time communication.

## Available Tools

The template includes several example tools:

### 1. example_tool
Processes text input and returns various statistics.

**Input:** `input_param` (string)
**Output:** JSON with processed results and metadata

### 2. text_analyzer
Analyzes text and provides detailed statistics.

**Input:** `text` (string)
**Output:** JSON with text analysis results

### 3. data_processor
Processes numerical data with various statistical operations.

**Input:** 
- `data` (List[float])
- `operation` (string) - "mean", "median", "std", "min", "max", "sum", "variance"

**Output:** JSON with processed data results

### 4. correlation_analyzer
Calculates correlation between two time series.

**Input:**
- `series1` (List[float])
- `series2` (List[float])

**Output:** JSON with correlation analysis

## Running the Server

### Local Development

```bash
# Install dependencies using uv
uv sync

# Run the server
python src/mcp_server.py --port=8081

# Or use the example script
python examples/run_mcp_server.py
```

### Docker

```bash
# Build the image
docker build -t mcp-tool-template .

# Run the container
docker run -p 8081:8081 mcp-tool-template
```

## Testing with CrewAI

The MCP server can be integrated with CrewAI for testing and development. This provides a powerful way to test your tools with AI agents.

### Setup for CrewAI Testing

1. **Install CrewAI dependencies:**
   ```bash
   uv sync --extra crewai
   ```

2. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env and add your OpenAI API key
   nano .env
   ```

   Required environment variables:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   MCP_HOST=localhost
   MCP_PORT=8081
   ```

3. **Start the MCP server:**
   ```bash
   # In one terminal
   python src/mcp_server.py --port=8081
   ```

4. **Run the CrewAI example:**
   ```bash
   # In another terminal
   python examples/crewai_mcp_example.py
   ```

### CrewAI Integration Example

The project includes a complete CrewAI integration example in `examples/crewai_mcp_example.py`. This example demonstrates:

- How to connect CrewAI agents to MCP tools
- How to use environment variables for configuration
- How to handle API keys securely
- How to create multi-agent workflows

```python
from crewai import Agent, Task, Crew
from crewai.tools import MCPTool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure MCP tool
mcp_tool = MCPTool(
    server_params={
        "url": f"http://{os.getenv('MCP_HOST', 'localhost')}:{os.getenv('MCP_PORT', '8081')}/sse"
    }
)

# Create agents with MCP tools
researcher = Agent(
    role='Research Analyst',
    goal='Analyze data and provide insights',
    backstory='Expert in data analysis and research',
    tools=[mcp_tool],
    verbose=True
)

# Create tasks that use MCP tools
analysis_task = Task(
    description='Analyze the provided text using MCP tools',
    agent=researcher,
    expected_output='Detailed analysis report'
)

# Create and run the crew
crew = Crew(
    agents=[researcher],
    tasks=[analysis_task],
    verbose=True
)

result = crew.kickoff()
```

### Testing Different Tools

You can test different MCP tools by modifying the CrewAI example:

1. **Text Analysis:**
   ```python
   # Use text_analyzer tool
   task = Task(
       description='Analyze the text: "The quick brown fox jumps over the lazy dog"',
       agent=researcher
   )
   ```

2. **Data Processing:**
   ```python
   # Use data_processor tool
   task = Task(
       description='Calculate the mean of [1, 2, 3, 4, 5]',
       agent=researcher
   )
   ```

3. **Correlation Analysis:**
   ```python
   # Use correlation_analyzer tool
   task = Task(
       description='Find correlation between [1, 2, 3, 4, 5] and [2, 4, 6, 8, 10]',
       agent=researcher
   )
   ```

### Troubleshooting CrewAI Integration

1. **Connection Issues:**
   - Ensure the MCP server is running on the correct port
   - Check that `MCP_HOST` and `MCP_PORT` are set correctly
   - Verify the server is accessible: `curl http://localhost:8081/health`

2. **API Key Issues:**
   - Ensure `OPENAI_API_KEY` is set in your `.env` file
   - Verify the API key is valid and has sufficient credits

3. **Tool Execution Errors:**
   - Check the MCP server logs for detailed error messages
   - Verify tool inputs match expected formats
   - Test tools individually before using with CrewAI

### Best Practices for CrewAI Testing

1. **Start Simple:** Begin with basic tools before complex workflows
2. **Monitor Logs:** Check both CrewAI and MCP server logs
3. **Test Incrementally:** Add one tool at a time
4. **Use Environment Variables:** Keep configuration flexible
5. **Handle Errors Gracefully:** Implement proper error handling in tools

## Adding New Tools

To add a new tool to the MCP server:

1. **Create the tool function** in `src/mcp_server.py`:

```python
@mcp.tool()
async def my_new_tool(param1: str, param2: int) -> str:
    """Description of what your tool does.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        JSON string containing results
    """
    try:
        # Your tool logic here
        result = {
            "processed_data": "your result",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Tool failed: {str(e)}"})
```

2. **Add tests** in `tests/test_mcp_server.py`:

```python
def test_my_new_tool(self):
    """Test the new tool function."""
    from src.mcp_server import my_new_tool
    
    result = my_new_tool("test", 123)
    result_data = json.loads(result)
    
    assert "processed_data" in result_data
```

3. **Update tool configuration** in `src/mcp_server.py` if needed

4. **Update documentation** in this file

5. **Test with CrewAI:** Add the new tool to your CrewAI workflows

## Tool Development Best Practices

### 1. Error Handling
Always wrap your tool logic in try-catch blocks and return meaningful error messages:

```python
try:
    # Your logic here
    return json.dumps(result, indent=2)
except Exception as e:
    logger.error(f"Error in tool: {str(e)}")
    return json.dumps({"error": f"Tool failed: {str(e)}"})
```

### 2. Input Validation
Validate inputs before processing:

```python
if not isinstance(data, list):
    return json.dumps({"error": "Data must be a list"})

if not data:
    return json.dumps({"error": "Data cannot be empty"})
```

### 3. Consistent Output Format
Return JSON strings with consistent structure:

```python
result = {
    "data": processed_data,
    "metadata": {
        "timestamp": datetime.utcnow().isoformat(),
        "processing_time": execution_time
    }
}
```

### 4. Logging
Use the provided logging utilities:

```python
from utils.logging_utils import get_logger

logger = get_logger()

logger.info(f"Processing data: {len(data)} items")
logger.error(f"Error occurred: {str(e)}")
```

## Testing Tools

### Unit Tests
Run the test suite:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_mcp_server.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Manual Testing
You can test tools manually by calling them directly:

```python
from src.mcp_server import text_analyzer

result = text_analyzer("Hello world!")
print(json.loads(result))
```

### CrewAI Testing
Test tools with AI agents using the CrewAI integration:

```bash
# Start MCP server
python src/mcp_server.py --port=8081

# Run CrewAI example
python examples/crewai_mcp_example.py
```

## Configuration

The MCP server uses environment variables and command-line arguments for configuration. Key settings:

- **Server port**: Use `--port` argument (default: 8081)
- **Host binding**: Use `--host` argument (default: 0.0.0.0)
- **Debug mode**: Use `--debug` flag
- **Environment variables**: Use `.env` file for API keys and other settings

## Deployment

### Local Testing
```bash
# Build Docker image
docker build -t mcp-tool-template .

# Run locally
docker run -p 8081:8081 mcp-tool-template
```

The deployment process will:
1. Build the Docker image
2. Run the container locally
3. Provide the service URL for testing

## Monitoring

The server provides several endpoints for monitoring:

- `/health` - Health check
- `/ready` - Readiness check
- `/metrics` - Application metrics

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   python src/mcp_server.py --port=8081
   ```

2. **Dependencies missing**
   ```bash
   uv sync
   ```

3. **Configuration errors**
   ```bash
   # Check environment variables
   cat .env
   ```

4. **Test failures**
   ```bash
   pytest tests/ -v
   ```

5. **CrewAI connection issues**
   ```bash
   # Check if MCP server is running
   curl http://localhost:8081/health
   
   # Check environment variables
   echo $OPENAI_API_KEY
   ```

### Logs
Check logs for detailed error information:

```bash
# If running locally
python src/mcp_server.py --debug

# If running in Docker
docker logs <container_id>
```

## Integration with AI Models

The MCP server can be integrated with AI models that support the Model Context Protocol. The server communicates via SSE (Server-Sent Events) and provides a standardized interface for tool execution.

For more information about MCP, see: https://modelcontextprotocol.io/ 