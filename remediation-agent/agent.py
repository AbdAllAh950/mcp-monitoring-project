"""
Remediation Agent - queries the MCP server, diagnoses problems,
and coordinates auto-remediation actions.
Run this separately for interactive CLI demo.
"""
import asyncio
import httpx
import os
from pathlib import Path

# Load .env file manually
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ[_k.strip()] = _v.strip()
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
        console.print("  [cyan]7[/cyan] - AI diagnose active alerts (powered by LLM)")
        console.print("  [cyan]8[/cyan] - 💬 Chat with AI about your cluster (natural language)")
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
        
        
        elif choice == "7":
            console.print("\n[bold cyan]Fetching active alerts and runbooks...[/bold cyan]")
            try:
                alerts_resp = httpx.get(f"{MCP_URL}/tools/get_active_alerts", timeout=10)
                alerts = alerts_resp.json().get("alerts", [])
                runbooks_resp = httpx.get(f"{MCP_URL}/tools/list_runbooks", timeout=10)
                runbook_names = runbooks_resp.json().get("runbooks", [])

                runbooks = {}
                for name in runbook_names:
                    rb_resp = httpx.get(f"{MCP_URL}/tools/get_runbook", params={"alert_name": name}, timeout=10)
                    rb_data = rb_resp.json()
                    if rb_data.get("found"):
                        runbooks[name] = rb_data["runbook"]

                if not alerts:
                    console.print("[green]No active alerts right now — cluster looks healthy![/green]")
                else:
                    console.print(f"[yellow]Diagnosing {len(alerts)} active alert(s) with AI...[/yellow]")
                    diagnosis = ai_diagnose_alerts(alerts, runbooks)
                    console.print(Panel(
                        diagnosis,
                        title="[bold red]AI Diagnosis & Recommendation[/bold red]",
                        border_style="red",
                        padding=(1, 2)
                    ))
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")


        elif choice == "8":
            console.print("\n[bold cyan]💬 AI Chat Mode — type your question, 'quit' to exit[/bold cyan]")
            console.print("[dim]Examples: 'What alerts are firing?', 'Fix the kafka issue', 'Show me spark memory usage'[/dim]\n")
            conversation_history = []
            while True:
                try:
                    user_input = input("You: ").strip()
                except (KeyboardInterrupt, EOFError):
                    break
                if not user_input or user_input.lower() in ["quit", "exit", "q"]:
                    console.print("[dim]Exiting chat mode...[/dim]")
                    break
                console.print("[yellow]🤖 AI is thinking...[/yellow]")
                reply, conversation_history = ai_chat(user_input, conversation_history)
                from rich.markdown import Markdown
                console.print(Panel(
                    Markdown(reply),
                    title="[bold green]🤖 AI Assistant[/bold green]",
                    border_style="green",
                    padding=(1, 2)
                ))
                console.print()

        elif choice == "q":
            console.print("[dim]Goodbye![/dim]")
            break



def ai_chat(user_message: str, conversation_history: list) -> tuple[str, list]:
    """Full conversational AI that uses MCP tools to answer questions"""
    try:
        from openai import OpenAI
        import json

        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        )
        model = os.environ.get("OPENAI_MODEL", "qwen/qwen3-8b")

        # Fetch live context from MCP server
        try:
            alerts = httpx.get(f"{MCP_URL}/tools/get_active_alerts", timeout=5).json().get("alerts", [])
            health = httpx.get(f"{MCP_URL}/tools/get_service_health", timeout=5).json()
            history = httpx.get(f"{MCP_URL}/tools/get_remediation_history", timeout=5).json().get("history", [])[-5:]
            runbooks = httpx.get(f"{MCP_URL}/tools/list_runbooks", timeout=5).json().get("runbooks", [])
        except Exception as e:
            alerts, health, history, runbooks = [], {}, [], []

        system_prompt = f"""You are an expert SRE AI assistant for a big data platform monitoring system.
You have access to real-time data from the MCP monitoring server.

CURRENT SYSTEM STATE:
- Active Alerts ({len(alerts)}): {json.dumps([(a.get("alert_name") or a.get("name","?")) + " [" + a.get("severity","?") + "]" for a in alerts]) if alerts else "None - all healthy"}
- Service Health: {json.dumps(health.get("services", {}), indent=None)}
- Recent Remediations (last 5): {json.dumps([h.get("alert_name") + " -> " + h.get("action") + " [" + ("✅" if h.get("success") else "❌") + "]" for h in history]) if history else "None yet"}
- Available Runbooks: {", ".join(runbooks)}

AVAILABLE MCP TOOLS YOU CAN CALL:
- GET /tools/get_active_alerts → lists currently firing alerts
- GET /tools/get_service_health → kafka/spark/hdfs health status
- GET /tools/get_remediation_history → past remediation actions
- GET /tools/get_runbook?alert_name=X → get runbook for specific alert
- POST /tools/trigger_remediation {{alert_name, service, action}} → execute remediation
- POST /tools/query_prometheus {{query: "promql"}} → query metrics directly

INSTRUCTIONS:
- Answer concisely and directly based on the real-time data above
- When the user asks to fix/remediate something, call trigger_remediation and report the result
- When asked about metrics, call query_prometheus with the appropriate PromQL
- Always cite which tool data you used in your answer
- Be actionable: if there are alerts, always suggest the next step
- Format responses cleanly - use bullet points for lists"""

        # Build messages with history
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-6:])  # keep last 3 exchanges
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=400
        )

        ai_reply = response.choices[0].message.content.strip()

        # Check if AI wants to trigger remediation
        if any(word in user_message.lower() for word in ["fix", "remediate", "restart", "resolve", "trigger"]):
            if alerts:
                alert = alerts[0]
                try:
                    result = httpx.post(
                        f"{MCP_URL}/tools/trigger_remediation",
                        json={
                            "alert_name": alert.get("alert_name") or alert.get("name"),
                            "service": alert.get("service"),
                            "action": alert.get("action")
                        },
                        timeout=15
                    ).json()
                    ai_reply += f"\n\n✅ **Action taken**: Triggered `{alert.get('action')}` for `{alert.get('alert_name')}`. Result: {result.get('status', 'executed')}"
                except Exception as e:
                    ai_reply += f"\n\n⚠️ Could not trigger remediation: {str(e)}"

        # Update conversation history
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": ai_reply})

        return ai_reply, conversation_history

    except Exception as e:
        return f"AI chat unavailable: {str(e)}", conversation_history

def ai_diagnose_alerts(alerts: list, runbooks: dict) -> str:
    """Use LLM to diagnose active alerts and recommend remediation"""
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        )
        model = os.environ.get("OPENAI_MODEL", "qwen/qwen3-8b")

        if not alerts:
            return "No active alerts to diagnose."

        alert_lines = []
        for a in alerts:
            alert_lines.append(
                f"- Alert: {a.get('alert_name','?')} | Service: {a.get('service','?')} | "
                f"Severity: {a.get('severity','?')} | Status: {a.get('status','?')}"
            )
        alert_summary = "\n".join(alert_lines)

        runbook_lines = []
        for a in alerts:
            rb = runbooks.get(a.get("alert_name", ""))
            if rb:
                symptom = rb.get("symptom", "")
                actions = rb.get("remediation_actions", [])
                action_str = ", ".join([x.get("action","") for x in actions])
                runbook_lines.append(f"- {a.get('alert_name')}: {symptom} → actions: {action_str}")

        runbook_context = "\n".join(runbook_lines) if runbook_lines else "No runbooks matched."

        prompt = f"""You are an expert SRE engineer monitoring a big data cluster with Kafka, Spark, and HDFS.

Currently firing alerts:
{alert_summary}

Available runbooks for these alerts:
{runbook_context}

Based on this information:
1. Identify the most critical issue
2. Explain the likely root cause in one sentence
3. Recommend the exact remediation action to take
4. Estimate the business impact if not resolved

Be concise and direct. Max 5 sentences total."""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"AI diagnosis unavailable: {str(e)}"

if __name__ == "__main__":
    asyncio.run(interactive_menu())
