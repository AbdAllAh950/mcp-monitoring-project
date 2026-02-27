.PHONY: help setup start stop restart logs mcp-server agent status clean demo

help:
	@echo ""
	@echo "╔═══════════════════════════════════════╗"
	@echo "║   MCP Monitoring Project - Commands   ║"
	@echo "╚═══════════════════════════════════════╝"
	@echo ""
	@echo "  make setup        Install Python dependencies"
	@echo "  make start        Start ALL services (Docker + MCP + Agent)"
	@echo "  make stop         Stop all services"
	@echo "  make restart      Restart all services"
	@echo "  make logs         Follow all Docker logs"
	@echo "  make mcp-server   Start MCP server only"
	@echo "  make agent        Start Remediation Agent CLI"
	@echo "  make status       Show status of all services"
	@echo "  make demo         Open all demo URLs"
	@echo "  make clean        Stop and remove all data"
	@echo ""

setup:
	@echo "Installing MCP server dependencies..."
	cd mcp-server && pip3 install -r requirements.txt
	@echo "Installing Agent dependencies..."
	cd remediation-agent && pip3 install -r requirements.txt
	@echo "✅ Dependencies installed"

start:
	@echo "🚀 Starting Docker monitoring stack..."
	cd monitoring && docker compose up -d --build
	@echo "⏳ Waiting 15 seconds for services to initialize..."
	@sleep 15
	@echo "🤖 Starting MCP Server..."
	@cd mcp-server && python3 mcp_server.py &
	@echo "✅ All services started!"
	@echo ""
	@echo "📊 Prometheus:    http://localhost:9090"
	@echo "📈 Grafana:       http://localhost:3000  (admin/admin123)"
	@echo "🤖 MCP Server:    http://localhost:8888"
	@echo "🔔 Alertmanager:  http://localhost:9093"

stop:
	@echo "Stopping Docker stack..."
	cd monitoring && docker compose down
	@echo "Stopping MCP server..."
	@pkill -f mcp_server.py 2>/dev/null || true
	@echo "✅ All stopped"

restart: stop start

logs:
	cd monitoring && docker compose logs -f

mcp-server:
	cd mcp-server && python3 mcp_server.py

agent:
	cd remediation-agent && python3 agent.py

status:
	@echo "=== Docker Services ==="
	cd monitoring && docker compose ps
	@echo ""
	@echo "=== MCP Server ==="
	@curl -s http://localhost:8888/health 2>/dev/null || echo "MCP Server: NOT RUNNING"
	@echo ""
	@echo "=== Prometheus ==="
	@curl -s http://localhost:9090/-/healthy 2>/dev/null || echo "Prometheus: NOT RUNNING"

demo:
	@open http://localhost:3000
	@open http://localhost:9090
	@open http://localhost:8888/docs
	@open http://localhost:9093

clean:
	cd monitoring && docker compose down -v
	@pkill -f mcp_server.py 2>/dev/null || true
	@echo "✅ All cleaned"

