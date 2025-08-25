# Dockerfile for MCP Tool
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml README.md ./

# Install dependencies and the project
RUN uv sync

# Copy the rest of the application
COPY . .

# Set environment variables
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/root/.local/bin/:$PATH"

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["uv", "run", "python", "src/mcp_server.py", "--port", "8080"] 
