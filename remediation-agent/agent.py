"""
Remediation Agent - queries the MCP server, diagnoses problems,
and coordinates auto-remediation actions.
Run this separately for interactive CLI demo.
"""
import asyncio
import httpx
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

console = Console()
MCP_URL = "http://localhost:8888"

async def get_service_health():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{MCP_URL}/tools/get_service_health")
        return resp.json()

async def get_active_alerts():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{MCP_URL}/tools/get_active_alerts")
        return resp.json()

async def get_remediation_history():
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{MCP_URL}/tools/get_remediation_history?limit=10")
        return resp.json()

async def trigger_remediation(alert_name: str, service: str, action: str):
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{MCP_URL}/tools/trigger_remediation", json={
            "alert_name": alert_name,
            "service": service,
            "action": action,
            "reason": "Agent-triggered manual remediation"
        })
        return resp.json()

async def query_metric(service: str, query: str):
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{MCP_URL}/tools/query_prometheus", json={
            "service": service,
            "metric_query": query
        })
        return resp.json()

def display_health(health_data: dict):
    table = Table(title="🏥 Service Health Status", show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan", width=12)
    table.add_column("Health", width=10)
    table.add_column("Critical", justify="center", width=10)
    table.add_column("Warnings", justify="center", width=10)
    table.add_column("Active Alerts", justify="center", width=14)

    for service, data in health_data.get("services", {}).items():
        health = data.get("health", "unknown")
        color = {"healthy": "green", "warning": "yellow", "critical": "red"}.get(health, "white")
        table.add_row(
            service.upper(),
            Text(f"● {health.upper()}", style=color),
            str(data.get("critical", 0)),
            str(data.get("warnings", 0)),
            str(data.get("active_alerts", 0))
        )
    console.print(table)

def display_alerts(alerts_data: dict):
    alerts = alerts_data.get("alerts", [])
    if not alerts:
        console.print(Panel("[green]✅ No active alerts! All systems healthy.[/green]", title="Active Alerts"))
        return
    
    table = Table(title=f"🚨 Active Alerts ({len(alerts)})", show_header=True, header_style="bold red")
    table.add_column("Alert Name", style="yellow", width=30)
    table.add_column("Service", width=10)
    table.add_column("Severity", width=10)
    table.add_column("Status", width=12)
    table.add_column("Summary", width=40)

    for alert in alerts:
        severity = alert.get("severity", "unknown")
        color = {"critical": "red", "warning": "yellow"}.get(severity, "white")
        table.add_row(
            alert.get("name", ""),
            alert.get("service", "").upper(),
            Text(severity.upper(), style=color),
            alert.get("remediation_status", "pending"),
            alert.get("summary", "")[:40]
        )
    console.print(table)

def display_remediation_history(history_data: dict):
    history = history_data.get("history", [])
    if not history:
        console.print("[dim]No remediation history yet.[/dim]")
        return

    table = Table(title="🔧 Recent Remediations", show_header=True, header_style="bold blue")
    table.add_column("Time", width=20)
    table.add_column("Alert", width=28)
    table.add_column("Service", width=10)
    table.add_column("Action", width=20)
    table.add_column("Result", width=10)
    table.add_column("Duration", width=10)

    for rem in reversed(history[-10:]):
        success = rem.get("success", False)
        result_text = Text("✅ OK" if success else "❌ FAIL", style="green" if success else "red")
        ts = rem.get("timestamp", "")[:19].replace("T", " ")
        table.add_row(
            ts,
            rem.get("alert_name", "")[:28],
            rem.get("service", "").upper(),
            rem.get("action", ""),
            result_text,
            f"{rem.get('duration_seconds', 0):.1f}s"
        )
    console.print(table)

async def interactive_menu():
    console.print(Panel.fit(
        "[bold cyan]🤖 MCP Remediation Agent[/bold cyan]\n"
        "[dim]Monitoring & Auto-Diagnostics System[/dim]",
        border_style="cyan"
    ))

    while True:
        console.print("\n[bold]Choose an action:[/bold]")
        console.print("  [cyan]1[/cyan] - View service health")
        console.print("  [cyan]2[/cyan] - View active alerts")
        console.print("  [cyan]3[/cyan] - View remediation history")
        console.print("  [cyan]4[/cyan] - Query a Prometheus metric")
        console.print("  [cyan]5[/cyan] - Manually trigger remediation")
        console.print("  [cyan]6[/cyan] - Live monitor (auto-refresh every 10s)")
        console.print("  [cyan]q[/cyan] - Quit")
        
        choice = input("\nEnter choice: ").strip().lower()
        
        if choice == "1":
            data = await get_service_health()
            display_health(data)
        
        elif choice == "2":
            data = await get_active_alerts()
            display_alerts(data)
        
        elif choice == "3":
            data = await get_remediation_history()
            display_remediation_history(data)
        
        elif choice == "4":
            service = input("Service (kafka/spark/hdfs/system): ").strip()
            query = input("PromQL query (or press Enter for default): ").strip()
            if not query:
                defaults = {"kafka": "kafka_consumer_lag", "spark": "spark_active_tasks",
                           "hdfs": "hdfs_disk_used_percent", "system": "up"}
                query = defaults.get(service, "up")
            data = await query_metric(service, query)
            console.print_json(json.dumps(data, indent=2))
        
        elif choice == "5":
            alert_name = input("Alert name: ").strip()
            service = input("Service: ").strip()
            action = input("Action (e.g. restart_consumer, cleanup_hdfs): ").strip()
            data = await trigger_remediation(alert_name, service, action)
            console.print(f"[green]✅ Remediation triggered:[/green] {data}")
        
        elif choice == "6":
            console.print("[dim]Live monitor running. Press Ctrl+C to stop.[/dim]")
            try:
                while True:
                    console.clear()
                    console.print(f"[dim]Last updated: {datetime.now().strftime('%H:%M:%S')}[/dim]")
                    health_data = await get_service_health()
                    display_health(health_data)
                    alerts_data = await get_active_alerts()
                    display_alerts(alerts_data)
                    history_data = await get_remediation_history()
                    display_remediation_history(history_data)
                    await asyncio.sleep(10)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped live monitor.[/yellow]")
        
        elif choice == "q":
            console.print("[dim]Goodbye![/dim]")
            break

if __name__ == "__main__":
    asyncio.run(interactive_menu())
