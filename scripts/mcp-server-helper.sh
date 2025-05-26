#!/bin/bash

# MCP Server Helper Script
# Provides common operations for the Kanakku MCP Server

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SERVICE_NAME="kanakku-mcp-server"
MCP_PATH="/opt/kanakku/mcp-server"

usage() {
    echo "Usage: $0 {status|start|stop|restart|logs|test|deploy}"
    echo ""
    echo "Commands:"
    echo "  status   - Show service status"
    echo "  start    - Start the MCP server service"
    echo "  stop     - Stop the MCP server service"
    echo "  restart  - Restart the MCP server service"
    echo "  logs     - Show service logs (follow mode)"
    echo "  test     - Run connection test"
    echo "  deploy   - Deploy/update MCP server"
    exit 1
}

check_permissions() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}This script must be run as root (use sudo)${NC}"
        exit 1
    fi
}

service_status() {
    echo -e "${YELLOW}Checking MCP server status...${NC}"
    systemctl status $SERVICE_NAME --no-pager
}

service_start() {
    echo -e "${YELLOW}Starting MCP server...${NC}"
    systemctl start $SERVICE_NAME
    sleep 2
    systemctl is-active $SERVICE_NAME && echo -e "${GREEN}MCP server started successfully${NC}"
}

service_stop() {
    echo -e "${YELLOW}Stopping MCP server...${NC}"
    systemctl stop $SERVICE_NAME
    echo -e "${GREEN}MCP server stopped${NC}"
}

service_restart() {
    echo -e "${YELLOW}Restarting MCP server...${NC}"
    systemctl restart $SERVICE_NAME
    sleep 2
    systemctl is-active $SERVICE_NAME && echo -e "${GREEN}MCP server restarted successfully${NC}"
}

service_logs() {
    echo -e "${YELLOW}Showing MCP server logs (Ctrl+C to exit)...${NC}"
    journalctl -u $SERVICE_NAME -f
}

run_test() {
    echo -e "${YELLOW}Running MCP server connection test...${NC}"
    if [ -d "$MCP_PATH" ]; then
        cd "$MCP_PATH"
        if [ -f "test-connection.py" ]; then
            sudo -u kanakku python test-connection.py
        else
            echo -e "${RED}test-connection.py not found in $MCP_PATH${NC}"
            exit 1
        fi
    else
        echo -e "${RED}MCP server directory not found: $MCP_PATH${NC}"
        exit 1
    fi
}

deploy_mcp() {
    echo -e "${YELLOW}Deploying/updating MCP server...${NC}"

    # Stop service if running
    systemctl stop $SERVICE_NAME || true

    # Run deployment script
    if [ -d "$MCP_PATH" ]; then
        cd "$MCP_PATH"
        if [ -f "deploy-production.sh" ]; then
            sudo -u kanakku ./deploy-production.sh
        else
            echo -e "${RED}deploy-production.sh not found in $MCP_PATH${NC}"
            exit 1
        fi
    else
        echo -e "${RED}MCP server directory not found: $MCP_PATH${NC}"
        exit 1
    fi

    # Restart service
    systemctl daemon-reload
    systemctl start $SERVICE_NAME
    sleep 2

    if systemctl is-active $SERVICE_NAME > /dev/null; then
        echo -e "${GREEN}MCP server deployed and started successfully${NC}"
    else
        echo -e "${RED}MCP server failed to start after deployment${NC}"
        exit 1
    fi
}

# Main script logic
case "${1:-}" in
    status)
        service_status
        ;;
    start)
        check_permissions
        service_start
        ;;
    stop)
        check_permissions
        service_stop
        ;;
    restart)
        check_permissions
        service_restart
        ;;
    logs)
        service_logs
        ;;
    test)
        run_test
        ;;
    deploy)
        check_permissions
        deploy_mcp
        ;;
    *)
        usage
        ;;
esac
