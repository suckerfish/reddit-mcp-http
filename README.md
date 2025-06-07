# Reddit MCP Server

A FastMCP server that provides tools for accessing Reddit's public API through the Model Context Protocol (MCP).

## Features

🔥 **8 Reddit Tools** - Access Reddit content through MCP
📡 **Dual Transport** - Supports both stdio and streamable-http transports  
🚀 **Easy Deployment** - One-script VPS deployment with systemd
🔒 **Secure** - No API keys required, uses Reddit's public API
⚡ **Fast** - Built with FastMCP for optimal performance

## Available Tools

- **get_frontpage_posts** - Get hot posts from Reddit frontpage
- **get_subreddit_info** - Get basic information about a subreddit
- **get_subreddit_hot_posts** - Get hot posts from a specific subreddit
- **get_subreddit_new_posts** - Get new posts from a specific subreddit
- **get_subreddit_top_posts** - Get top posts with time filtering
- **get_subreddit_rising_posts** - Get rising posts from a specific subreddit
- **get_post_content** - Get detailed post content including comments
- **get_post_comments** - Get comments from a specific post

## Quick Start

### Local Development

1. **Clone and setup:**
   ```bash
   git clone https://github.com/suckerfish/reddit-mcp-http.git
   cd reddit-mcp-http
   uv venv
   uv pip install -e .
   ```

2. **Test with MCPTools:**
   ```bash
   # List available tools
   mcp tools uv run src/server.py
   
   # Test a tool
   mcp call get_subreddit_info --params '{"subreddit_name":"programming"}' uv run src/server.py
   ```

3. **Run as HTTP server:**
   ```bash
   uv run src/server.py --transport streamable-http --port 8080
   ```

### VPS Deployment

Deploy as a production systemd service:

```bash
sudo ./deploy/vps-deploy.sh
```

See [deploy/README.md](deploy/README.md) for detailed deployment instructions.

## Usage Examples

### Get Subreddit Information
```bash
mcp call get_subreddit_info --params '{"subreddit_name":"python"}' uv run src/server.py
```

### Get Hot Posts from a Subreddit
```bash
mcp call get_subreddit_hot_posts --params '{"subreddit_name":"programming", "limit":5}' uv run src/server.py
```

### Get Reddit Frontpage
```bash
mcp call get_frontpage_posts --params '{"limit":10}' uv run src/server.py
```

## MCP Client Configuration

### Claude Desktop (Local)
```json
{
  "reddit-mcp": {
    "command": "uv",
    "args": [
      "run", 
      "--directory", 
      "/path/to/reddit-mcp-http",
      "src/server.py"
    ]
  }
}
```

### Remote HTTP Connection
```json
{
  "reddit-mcp": {
    "type": "streamable-http",
    "url": "http://your-server:8080/mcp"
  }
}
```

## Architecture

Built with:
- **FastMCP** - Modern MCP server framework
- **redditwarp** - Type-safe Reddit API client
- **Pydantic** - Data validation and serialization
- **uvicorn** - ASGI server for HTTP transport

## API Coverage

This server accesses Reddit's public API through redditwarp:
- No authentication required
- Respects Reddit's rate limits
- Returns structured JSON data
- Handles errors gracefully

## Development

### Project Structure
```
src/
├── server.py          # Main MCP server implementation
├── models/            # Pydantic data models
└── tools/             # MCP tool definitions

deploy/
├── vps-deploy.sh      # Automated deployment script
├── reddit-mcp.service # SystemD service configuration
└── README.md          # Deployment guide
```

### Adding New Tools

1. Add tool function with `@mcp.tool()` decorator
2. Use Pydantic models for validation
3. Follow existing error handling patterns
4. Test with MCPTools

### Testing

```bash
# Test all tools
mcp tools uv run src/server.py

# Test specific tool
mcp call TOOL_NAME --params '{"param":"value"}' uv run src/server.py

# Interactive testing
mcp shell uv run src/server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with MCPTools
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📖 [Deployment Guide](deploy/README.md)
- 🐛 [Issues](https://github.com/suckerfish/reddit-mcp-http/issues)
- 💬 [Discussions](https://github.com/suckerfish/reddit-mcp-http/discussions)