#!/bin/bash
set -e

echo "🚀 Reddit MCP Server - VPS Deployment"
echo "====================================="

# Configuration
APP_DIR="/opt/reddit-mcp"
APP_USER="reddit-mcp"
REPO_URL="https://github.com/your-username/reddit-mcp-http.git"  # Update this to your actual repo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo ./vps-deploy.sh)"
    exit 1
fi

echo "📦 Installing system dependencies..."
apt update
apt install -y python3 python3-venv python3-pip git curl

echo "👤 Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --home-dir $APP_DIR --create-home --shell /bin/bash $APP_USER
    echo "✅ Created user: $APP_USER"
else
    echo "ℹ️ User $APP_USER already exists"
fi

echo "📥 Setting up repository..."
if [ -d "$APP_DIR/.git" ]; then
    echo "ℹ️ Repository already exists, pulling latest changes..."
    cd $APP_DIR
    sudo -u $APP_USER git pull
elif [ -d "$APP_DIR" ] && [ "$(ls -A $APP_DIR)" ]; then
    echo "⚠️ Directory exists but is not a git repository. Removing and cloning fresh..."
    rm -rf $APP_DIR
    mkdir -p $APP_DIR
    chown $APP_USER:$APP_USER $APP_DIR
    sudo -u $APP_USER git clone $REPO_URL $APP_DIR
    cd $APP_DIR
else
    echo "📁 Creating application directory and cloning..."
    mkdir -p $APP_DIR
    chown $APP_USER:$APP_USER $APP_DIR
    sudo -u $APP_USER git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

echo "🐍 Setting up Python environment..."
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -e .

echo "📋 Creating logs directory..."
mkdir -p $APP_DIR/logs
chown $APP_USER:$APP_USER $APP_DIR/logs

echo "⚙️ Installing systemd service..."
cp $APP_DIR/deploy/reddit-mcp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable reddit-mcp

echo "🔥 Starting MCP server..."
systemctl start reddit-mcp

# Wait a moment for startup
sleep 3

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📊 Service status:"
systemctl status reddit-mcp --no-pager -l

echo ""
echo "📡 Your Reddit MCP server is running on:"
echo "   http://$(hostname -I | awk '{print $1}'):8080/mcp"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status reddit-mcp     # Check status"
echo "   sudo systemctl restart reddit-mcp    # Restart service"
echo "   sudo journalctl -u reddit-mcp -f     # View logs"
echo "   curl http://localhost:8080/mcp/health # Test endpoint"
echo ""
echo "🔗 Connect your MCP client to:"
echo '   {"type": "streamable-http", "url": "http://YOUR_TAILSCALE_IP:8080/mcp"}'
echo ""
echo "🌐 Available Reddit tools:"
echo "   - get_frontpage_posts"
echo "   - get_subreddit_info"
echo "   - get_subreddit_hot_posts"
echo "   - get_subreddit_new_posts"
echo "   - get_subreddit_top_posts"
echo "   - get_subreddit_rising_posts"
echo "   - get_post_content"
echo "   - get_post_comments"