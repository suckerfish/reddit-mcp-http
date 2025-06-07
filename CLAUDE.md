# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**✅ COMPLETED PROJECT**: Reddit MCP Server using FastMCP

This is a complete, production-ready FastMCP server that provides 8 tools for accessing Reddit's public API through the Model Context Protocol (MCP). The server supports both local (stdio) and remote (streamable-http) transport modes with automated VPS deployment.

**🚀 Project Status: COMPLETE & DEPLOYED**
- ✅ All 8 Reddit API tools implemented and tested
- ✅ FastMCP integration with dual transport support
- ✅ Production deployment with systemd service
- ✅ Comprehensive documentation and testing
- ✅ GitHub repository created and published
- ✅ Uses redditwarp library for Reddit API access

**🔗 Repository**: https://github.com/suckerfish/reddit-mcp-http

## Quick Commands

### Testing Reddit MCP Server

Use MCPTools to test the Reddit MCP server:

```bash
# List all available Reddit tools 
mcp tools uv run src/server.py

# Test specific Reddit tools
mcp call get_subreddit_info --params '{"subreddit_name":"programming"}' uv run src/server.py
mcp call get_frontpage_posts --params '{"limit":5}' uv run src/server.py
mcp call get_subreddit_hot_posts --params '{"subreddit_name":"python","limit":3}' uv run src/server.py

# Start interactive testing shell
mcp shell uv run src/server.py

# Run as HTTP server for remote testing
uv run src/server.py --transport streamable-http --port 8081
```

### Available Reddit Tools
- `get_frontpage_posts` - Get hot posts from Reddit frontpage
- `get_subreddit_info` - Get basic information about a subreddit  
- `get_subreddit_hot_posts` - Get hot posts from a specific subreddit
- `get_subreddit_new_posts` - Get new posts from a specific subreddit
- `get_subreddit_top_posts` - Get top posts with time filtering
- `get_subreddit_rising_posts` - Get rising posts from a specific subreddit
- `get_post_content` - Get detailed post content including comments
- `get_post_comments` - Get comments from a specific post

### Package Management

```bash
# Install dependencies manually
uv pip install -e .

# Add a new dependency
uv add <package_name>
```

**Note**: When using UV with MCP servers, add `[tool.hatch.build.targets.wheel]` and `packages = ["src"]` to pyproject.toml.

## Essential FastMCP Patterns

### Basic Server Setup
```python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool()
async def example_tool(parameter: str) -> dict:
    """Tool documentation here."""
    return {"result": "value"}

if __name__ == "__main__":
    mcp.run()
```

### Input Validation with Pydantic
```python
from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')

@mcp.tool()
def create_user(request: UserRequest) -> dict:
    """Create user with validated input."""
    return {"user_id": "123", "name": request.name}
```

### Error Handling
```python
from fastmcp.exceptions import ToolError

@mcp.tool()
def safe_tool(param: str) -> str:
    try:
        # Your tool logic
        return result
    except ValueError as e:
        # Client sees generic error
        raise ValueError("Invalid input")
    except SomeError as e:
        # Client sees specific error
        raise ToolError(f"Tool failed: {str(e)}")
```

### Authentication Context
```python
from fastmcp import Context

@mcp.tool()
async def authenticated_tool(param: str, ctx: Context) -> dict:
    """Tool requiring authentication."""
    user_id = ctx.client_id
    scopes = ctx.scopes
    
    if "required_scope" not in scopes:
        raise ToolError("Insufficient permissions")
    
    return {"result": f"Hello user {user_id}"}
```

## Production Deployment

### VPS Deployment (Automated)
```bash
# Clone and deploy to VPS
git clone https://github.com/suckerfish/reddit-mcp-http.git
cd reddit-mcp-http
sudo ./deploy/vps-deploy.sh
```

### Service Management
```bash
# Check service status
sudo systemctl status reddit-mcp

# View logs
sudo journalctl -u reddit-mcp -f

# Restart service  
sudo systemctl restart reddit-mcp

# Test deployment
curl http://localhost:8081/mcp/health
```

## Implementation Details

**✅ Architecture**:
- Built with FastMCP framework
- Uses `redditwarp` library for Reddit API access
- Pydantic models for data validation and serialization
- Dual transport: stdio (local) and streamable-http (remote)
- Default port: 8081

**✅ No Authentication Required**: 
- Uses Reddit's public API only
- No API keys or credentials needed
- Rate limiting handled gracefully

## MCP Server Types

- **Local Servers**: Run as subprocesses, communicate via STDIO, good for file system access
- **Remote Servers**: Run as web services, support OAuth 2.1, better for SaaS integrations

## Transport Protocols

- **STDIO**: For local servers (subprocess communication)
- **Streamable HTTP**: Modern protocol for remote servers (recommended)
- **HTTP+SSE**: Legacy protocol for backward compatibility

## Project Structure

```
src/
├── server.py          # Main MCP server implementation
├── tools/             # Tool definitions organized by domain
├── resources/         # Resource handlers for static/dynamic data
├── models/            # Pydantic models for validation
└── config/            # Configuration and settings
```

## Essential Dependencies

- `fastmcp` - MCP server framework
- `pydantic` - Data validation and models
- `aiohttp` - Async HTTP client for external APIs
- `uvicorn` - ASGI server for production (remote servers)

## Comprehensive Documentation

For detailed implementation guidance, see:

- **[Quick Start Guide](docs/quickstart.md)** - Setup, basic server creation, first tools
- **[Authentication Guide](docs/authentication.md)** - OAuth 2.1, security patterns, context injection
- **[Deployment Guide](docs/deployment.md)** - Production deployment, Docker, cloud platforms
- **[Testing Guide](docs/testing.md)** - MCPTools usage, unit testing, integration testing
- **[Best Practices](docs/best-practices.md)** - Error handling, performance, security, code quality
- **[MCPTools Documentation](docs/mcptools.md)** - Detailed testing and validation guide

## Common Patterns for Claude Code

When working with this codebase, focus on:

1. **Tool Creation**: Add new tools in `src/tools/` following existing patterns
2. **Input Validation**: Always use Pydantic models for complex inputs
3. **Error Handling**: Use `ToolError` for user-facing errors, log detailed errors server-side
4. **Testing**: Test every tool with MCPTools before considering it complete
5. **Authentication**: Use Context for user-specific operations
6. **Documentation**: Include clear docstrings for all tools and functions

## Reddit MCP Server Configuration

**✅ Default Configuration**:
- Port: 8081 (HTTP transport)
- Host: 0.0.0.0 (production) / 127.0.0.1 (local)
- Transport: stdio (local) / streamable-http (remote)
- No environment variables required
- No API keys needed

**Command-line options**:
```bash
uv run src/server.py --transport streamable-http --host 0.0.0.0 --port 8081
```

## Configuration Patterns

### Command-Line Arguments
```python
import argparse

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Your MCP Server')
    parser.add_argument('--api-key', help='API Key')
    parser.add_argument('--config-param', help='Configuration parameter')
    return parser.parse_args()

def main():
    """Main entry point for the MCP server."""
    args = parse_arguments()
    from src.config.settings import initialize_config
    initialize_config(api_key=args.api_key, config_param=args.config_param)
    mcp.run()

if __name__ == "__main__":
    main()
```

### Flexible Configuration Pattern
```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Global variables that can be set by command-line arguments
API_KEY = None
CONFIG_PARAM = None

def initialize_config(api_key=None, config_param=None):
    """Initialize configuration with command-line arguments or environment variables."""
    global API_KEY, CONFIG_PARAM
    
    # Use command-line arguments if provided, otherwise fall back to environment variables
    API_KEY = api_key or os.getenv('API_KEY')
    CONFIG_PARAM = config_param or os.getenv('CONFIG_PARAM')
    
    if not API_KEY:
        raise ValueError("API key must be provided via --api-key argument or API_KEY environment variable")
```

### Configuration Import Timing
**Important**: Import configuration modules inside tool functions to avoid timing issues:

```python
# WRONG - imports at module level before config is initialized
from src.config.settings import API_KEY

@mcp.tool()
async def my_tool():
    # API_KEY will be None here
    pass

# CORRECT - import inside function after config is set
@mcp.tool()
async def my_tool():
    from src.config.settings import API_KEY  # Gets current value
    # API_KEY has correct value here
```

### Client Configuration Example
```json
"your-mcp": {
  "command": "uv",
  "args": [
    "run",
    "--directory",
    "/path/to/your/mcp",
    "src/server.py",
    "--api-key",
    "YOUR_API_KEY",
    "--config-param",
    "YOUR_VALUE"
  ]
}
```

## Troubleshooting

- **Tool not found**: Check tool is registered with `@mcp.tool()` decorator
- **Validation errors**: Verify Pydantic model matches expected input
- **Authentication issues**: Check Context usage and scope validation
- **Connection issues**: Verify server is running and accessible
- **Testing failures**: Use `mcp tools --server-logs` to see detailed errors
- **Variables showing as None**: Import configuration modules inside tool functions, not at module level
- **Build wheel errors**: Add `[tool.hatch.build.targets.wheel]` and `packages = ["src"]` to pyproject.toml
- **Command-line args not working**: Ensure `initialize_config()` is called in `main()` before `mcp.run()`