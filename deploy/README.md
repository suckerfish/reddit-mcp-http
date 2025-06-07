# VPS Deployment Guide

This guide walks you through deploying the Reddit MCP Server on your VPS as an always-on systemd service with streamable HTTP transport.

## Quick Start

1. **Clone the repository on your VPS:**
   ```bash
   git clone https://github.com/suckerfish/reddit-mcp-http.git
   cd reddit-mcp-http
   ```

2. **Run the deployment script:**
   ```bash
   sudo chmod +x deploy/vps-deploy.sh
   sudo ./deploy/vps-deploy.sh
   ```

3. **Test the deployment:**
   ```bash
   curl http://localhost:8080/mcp/health
   ```

That's it! Your Reddit MCP server is now running as a systemd service.

## What the deployment script does:

1. ✅ Installs Python 3, git, and other dependencies
2. ✅ Creates a dedicated `reddit-mcp` user for security
3. ✅ Sets up the application in `/opt/reddit-mcp/`
4. ✅ Creates a Python virtual environment and installs dependencies
5. ✅ Configures a systemd service for auto-start and restarts
6. ✅ Starts the MCP server with streamable HTTP on port 8080

## Available Tools

The Reddit MCP Server provides 8 tools for accessing Reddit's public API:

- **get_frontpage_posts** - Get hot posts from Reddit frontpage
- **get_subreddit_info** - Get basic information about a subreddit  
- **get_subreddit_hot_posts** - Get hot posts from a specific subreddit
- **get_subreddit_new_posts** - Get new posts from a specific subreddit
- **get_subreddit_top_posts** - Get top posts with time filtering
- **get_subreddit_rising_posts** - Get rising posts from a specific subreddit
- **get_post_content** - Get detailed post content including comments
- **get_post_comments** - Get comments from a specific post

## Service Management

**Check status:**
```bash
sudo systemctl status reddit-mcp
```

**View live logs:**
```bash
sudo journalctl -u reddit-mcp -f
```

**Restart service:**
```bash
sudo systemctl restart reddit-mcp
```

**Stop/Start service:**
```bash
sudo systemctl stop reddit-mcp
sudo systemctl start reddit-mcp
```

## Testing the MCP Server

**Health check:**
```bash
curl http://localhost:8080/mcp/health
```

**Test tools endpoint:**
```bash
curl http://localhost:8080/mcp/tools
```

**Test frontpage posts:**
```bash
curl -X POST http://localhost:8080/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_frontpage_posts", 
    "arguments": {
      "limit": 5
    }
  }'
```

**Test subreddit info:**
```bash
curl -X POST http://localhost:8080/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_subreddit_info", 
    "arguments": {
      "subreddit_name": "programming"
    }
  }'
```

**Test subreddit posts:**
```bash
curl -X POST http://localhost:8080/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_subreddit_hot_posts", 
    "arguments": {
      "subreddit_name": "python",
      "limit": 3
    }
  }'
```

## Client Configuration

Connect your MCP client using streamable HTTP:

```json
{
  "type": "streamable-http", 
  "url": "http://YOUR_TAILSCALE_IP:8080/mcp"
}
```

Replace `YOUR_TAILSCALE_IP` with your VPS's Tailscale IP address.

## Resource Usage

- **RAM**: ~100-150MB
- **Storage**: ~400MB
- **Network**: Port 8080 (adjust firewall as needed)

## Security Notes

- Service runs as dedicated `reddit-mcp` user (not root)
- Uses systemd security features (NoNewPrivileges, ProtectSystem, etc.)
- Binds to all interfaces (0.0.0.0) - secure with firewall/Tailscale
- Logs are handled by systemd journal
- No API keys required (uses Reddit's public API)

## Troubleshooting

**Service won't start:**
```bash
sudo journalctl -u reddit-mcp --no-pager -l
```

**Check Python dependencies:**
```bash
sudo -u reddit-mcp /opt/reddit-mcp/venv/bin/pip list
```

**Manual test:**
```bash
sudo -u reddit-mcp /opt/reddit-mcp/venv/bin/python /opt/reddit-mcp/src/server.py --transport streamable-http --host 0.0.0.0 --port 8080
```

**Update to latest code:**
```bash
cd /opt/reddit-mcp
sudo -u reddit-mcp git pull
sudo systemctl restart reddit-mcp
```

**Test with MCPTools locally:**
```bash
cd /opt/reddit-mcp
sudo -u reddit-mcp mcp tools /opt/reddit-mcp/venv/bin/python src/server.py
```

## Advanced Configuration

The systemd service file is located at:
- `/etc/systemd/system/reddit-mcp.service`

To modify configuration:
1. Edit the service file
2. Run `sudo systemctl daemon-reload`
3. Run `sudo systemctl restart reddit-mcp`

## Logs Location

- **systemd logs**: `sudo journalctl -u reddit-mcp`
- **Application logs**: `/opt/reddit-mcp/logs/` (if file logging is enabled)

## Rate Limiting

Reddit's public API has rate limits. The server will handle rate limiting gracefully:
- Default limits are usually sufficient for normal usage
- Error messages will indicate if rate limits are exceeded
- Consider adding delays between requests for high-volume usage

## Reddit API Details

This server uses the `redditwarp` library to access Reddit's public API:
- No authentication required
- Accesses publicly available content only
- Respects Reddit's terms of service
- Uses proper User-Agent headers