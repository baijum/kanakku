#!/bin/bash
# Health check script for Kanakku deployment
# This script checks the status of all services and endpoints

set -e

echo "🔍 Kanakku Health Check"
echo "======================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service status
check_service() {
    local service_name=$1
    local display_name=$2

    if systemctl is-active --quiet "$service_name"; then
        echo -e "${GREEN}✅ $display_name: Running${NC}"
        return 0
    else
        echo -e "${RED}❌ $display_name: Not running${NC}"
        return 1
    fi
}

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local name=$2
    local expected_status=${3:-200}

    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo -e "${GREEN}✅ $name: Responding${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: Not responding${NC}"
        return 1
    fi
}

# Function to check database connection
check_database() {
    local db_name=${1:-kanakku}

    if sudo -u postgres psql -d "$db_name" -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database ($db_name): Connected${NC}"
        return 0
    else
        echo -e "${RED}❌ Database ($db_name): Connection failed${NC}"
        return 1
    fi
}

# Check system services
echo "📋 System Services"
echo "------------------"
check_service "nginx" "Nginx"
check_service "postgresql" "PostgreSQL"
check_service "redis-server" "Redis"

echo ""

# Check Kanakku services
echo "🏦 Kanakku Services"
echo "------------------"
check_service "kanakku" "Main Application"
check_service "kanakku-worker" "Email Worker"
check_service "kanakku-scheduler" "Email Scheduler"
check_service "kanakku-admin-server" "Admin Server" || echo -e "${YELLOW}⚠️  Admin server is optional${NC}"

echo ""

# Check database
echo "🗄️  Database"
echo "------------"
check_database

echo ""

# Check HTTP endpoints
echo "🌐 HTTP Endpoints"
echo "----------------"
check_endpoint "http://localhost:8000/api/v1/health" "Backend Health Check"
check_endpoint "http://localhost" "Frontend (via Nginx)" "200\|301\|302"

echo ""

# Check logs for recent errors
echo "📝 Recent Errors"
echo "---------------"
error_count=$(sudo journalctl --since "5 minutes ago" --priority=err --no-pager -q | wc -l)
if [ "$error_count" -eq 0 ]; then
    echo -e "${GREEN}✅ No recent errors in system logs${NC}"
else
    echo -e "${YELLOW}⚠️  Found $error_count recent errors in system logs${NC}"
    echo "Recent errors:"
    sudo journalctl --since "5 minutes ago" --priority=err --no-pager -n 5
fi

echo ""

# Check disk space
echo "💾 Disk Space"
echo "------------"
disk_usage=$(df /opt/kanakku | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    echo -e "${GREEN}✅ Disk usage: ${disk_usage}%${NC}"
elif [ "$disk_usage" -lt 90 ]; then
    echo -e "${YELLOW}⚠️  Disk usage: ${disk_usage}%${NC}"
else
    echo -e "${RED}❌ Disk usage: ${disk_usage}% (Critical)${NC}"
fi

echo ""

# Check memory usage
echo "🧠 Memory Usage"
echo "--------------"
memory_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
memory_usage_int=${memory_usage%.*}
if [ "$memory_usage_int" -lt 80 ]; then
    echo -e "${GREEN}✅ Memory usage: ${memory_usage}%${NC}"
elif [ "$memory_usage_int" -lt 90 ]; then
    echo -e "${YELLOW}⚠️  Memory usage: ${memory_usage}%${NC}"
else
    echo -e "${RED}❌ Memory usage: ${memory_usage}% (High)${NC}"
fi

echo ""

# Summary
echo "📊 Summary"
echo "---------"
echo "Health check completed at $(date)"
echo "For detailed logs, check:"
echo "  - Application logs: /opt/kanakku/logs/"
echo "  - System logs: sudo journalctl -u kanakku"
echo "  - Nginx logs: /var/log/nginx/"

echo ""
echo "🔗 Quick Commands"
echo "----------------"
echo "  Restart all services: sudo systemctl restart kanakku kanakku-worker kanakku-scheduler"
echo "  Check service logs: sudo journalctl -u kanakku -f"
echo "  Check application logs: sudo tail -f /opt/kanakku/logs/kanakku.log"
