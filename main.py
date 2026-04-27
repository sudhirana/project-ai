"""
main.py
CLI entry point with rich UI. Demonstrates the full system end-to-end.
"""

import uuid
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box
from rich.text import Text

from facade.lead_management_facade import LeadManagementFacade
from models.agent import Agent
from models.lead import LeadStatus
from strategies.basic_scoring_strategy import BasicScoringStrategy
from strategies.scoring_strategies import PremiumScoringStrategy, RiskBasedScoringStrategy

console = Console()
facade = LeadManagementFacade()


# ── Seed data helpers ──────────────────────────────────────────────────────

def seed_agents():
    agents = [
        Agent(id=str(uuid.uuid4()), name="Sarah Mitchell",
              email="sarah@insure.com", phone="07700111001", max_capacity=5),
        Agent(id=str(uuid.uuid4()), name="James Okafor",
              email="james@insure.com", phone="07700111002", max_capacity=5),
        Agent(id=str(uuid.uuid4()), name="Priya Sharma",
              email="priya@insure.com", phone="07700111003", max_capacity=5),
    ]
    for a in agents:
        facade.add_agent(a)
    console.print("[green]✓ 3 agents seeded[/green]")
    return agents


def seed_leads():
    lead_specs = [
        dict(type="AUTO",   first="Oliver", last="Wright",
             email="oliver@example.com", age=34, income=55000,
             coverage=30000, source="REFERRAL", prior=True),
        dict(type="HEALTH", first="Emma",   last="Thompson",
             email="emma@example.com", age=28, income=42000,
             coverage=100000, source="WEBSITE", prior=False),
        dict(type="LIFE",   first="Raj",    last="Patel",
             email="raj@example.com", age=45, income=120000,
             coverage=500000, source="AGENT", prior=True),
        dict(type="HOME",   first="Sophie", last="Evans",
             email="sophie@example.com", age=52, income=75000,
             coverage=250000, source="COLD_CALL", prior=False),
        dict(type="AUTO",   first="Liam",   last="Johnson",
             email="liam@example.com", age=22, income=28000,
             coverage=15000, source="SOCIAL_MEDIA", prior=False),
    ]
    leads = []
    for s in lead_specs:
        lead = (
            facade.new_lead_builder()
            .of_type(s["type"])
            .for_person(s["first"], s["last"], s["email"], age=s["age"])
            .with_contact(phone="07700900000")
            .with_financials(income=s["income"], coverage_amount=s["coverage"])
            .from_source(s["source"])
            .with_prior_insurance(s["prior"])
            .build()
        )
        facade.submit_lead(lead)
        leads.append(lead)
    console.print(f"[green]✓ {len(leads)} leads created and scored[/green]")
    return leads


# ── Rich UI helpers ────────────────────────────────────────────────────────

def show_banner():
    console.print(Panel.fit(
        "[bold cyan]🛡  Insurance Lead Management System[/bold cyan]\n"
        "[dim]Modular Python · Design Patterns · SQLite[/dim]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
    ))


def show_menu() -> str:
    console.print("\n[bold yellow]MAIN MENU[/bold yellow]")
    options = [
        ("1", "📋 List all leads"),
        ("2", "🔀 Assign all unassigned leads"),
        ("3", "📈 Advance lead status"),
        ("4", "🎯 Re-score lead with different strategy"),
        ("5", "👥 List agents & capacity"),
        ("6", "📊 View summary report"),
        ("7", "🌱 Seed demo data"),
        ("0", "🚪 Exit"),
    ]
    for key, label in options:
        console.print(f"  [bold]{key}[/bold] — {label}")
    return Prompt.ask("\n[cyan]Choose option[/cyan]")


def display_leads_table(leads):
    if not leads:
        console.print("[yellow]No leads found.[/yellow]")
        return
    t = Table(title="Insurance Leads", box=box.ROUNDED, show_lines=True)
    t.add_column("ID", style="dim", width=8)
    t.add_column("Name")
    t.add_column("Type", style="cyan")
    t.add_column("Status", style="magenta")
    t.add_column("Score", justify="right", style="green")
    t.add_column("Source")
    t.add_column("Agent", style="yellow")
    for l in leads:
        t.add_row(
            l.id[:8],
            l.full_name,
            l.lead_type.value,
            l.status.value,
            f"{l.score:.1f}",
            l.lead_source,
            l.agent_id[:8] if l.agent_id else "—",
        )
    console.print(t)


def display_agents_table(agents):
    t = Table(title="Agent Roster", box=box.ROUNDED)
    t.add_column("Name")
    t.add_column("Email")
    t.add_column("Load", justify="right")
    t.add_column("Capacity", justify="right")
    t.add_column("Utilisation", justify="right")
    t.add_column("Available", justify="center")
    for a in agents:
        t.add_row(
            a.name, a.email,
            str(a.current_load), str(a.max_capacity),
            f"{a.utilisation_pct}%",
            "✅" if a.is_available else "❌",
        )
    console.print(t)


def display_report(report: dict):
    console.print(Panel("[bold]📊 Summary Report[/bold]", style="blue"))

    # Leads by status
    t1 = Table(title="Leads by Status", box=box.SIMPLE)
    t1.add_column("Status"); t1.add_column("Count", justify="right")
    for status, count in report["leads_by_status"].items():
        t1.add_row(status, str(count))
    console.print(t1)

    # Agent performance
    t2 = Table(title="Agent Performance", box=box.SIMPLE)
    t2.add_column("Agent"); t2.add_column("Total"); t2.add_column("Converted"); t2.add_column("Rate")
    for row in report["agent_performance"]:
        t2.add_row(row["agent"], str(row["total_leads"]),
                   str(row["converted"]), f"{row['conversion_rate']}%")
    console.print(t2)

    # Top scored
    t3 = Table(title="Top 5 Scored Leads", box=box.SIMPLE)
    t3.add_column("Name"); t3.add_column("Type"); t3.add_column("Score"); t3.add_column("Status")
    for row in report["top_scored_leads"]:
        t3.add_row(row["name"], row["type"], f"{row['score']:.1f}", row["status"])
    console.print(t3)


# ── Menu actions ───────────────────────────────────────────────────────────

def action_list_leads():
    display_leads_table(facade.list_leads())


def action_assign_leads():
    leads = facade.list_leads()
    unassigned = [l for l in leads if not l.agent_id]
    if not unassigned:
        console.print("[yellow]All leads already assigned.[/yellow]")
        return
    for lead in unassigned:
        console.print(f"\n[cyan]Assigning lead {lead.full_name}...[/cyan]")
        agent = facade.assign_lead(lead.id)
        if agent:
            console.print(f"  ✅ Assigned to [bold]{agent.name}[/bold]")
        else:
            console.print("  ❌ No available agents")


def action_advance_status():
    leads = facade.list_leads()
    if not leads:
        console.print("[yellow]No leads.[/yellow]"); return
    display_leads_table(leads)
    lead_id_prefix = Prompt.ask("Enter lead ID prefix (first 8 chars)")
    matched = [l for l in leads if l.id.startswith(lead_id_prefix)]
    if not matched:
        console.print("[red]Lead not found.[/red]"); return
    lead = matched[0]
    statuses = [s.value for s in LeadStatus if lead.can_transition_to(s)]
    if not statuses:
        console.print("[yellow]No valid transitions from current status.[/yellow]"); return
    choice = Prompt.ask("New status", choices=statuses)
    console.print(f"\n[cyan]Transitioning {lead.full_name}...[/cyan]")
    facade.update_lead_status(lead.id, LeadStatus(choice))
    console.print(f"  ✅ Status updated to [bold]{choice}[/bold]")


def action_rescore():
    leads = facade.list_leads()
    if not leads:
        console.print("[yellow]No leads.[/yellow]"); return
    display_leads_table(leads)
    lead_id_prefix = Prompt.ask("Enter lead ID prefix")
    matched = [l for l in leads if l.id.startswith(lead_id_prefix)]
    if not matched:
        console.print("[red]Lead not found.[/red]"); return
    lead = matched[0]
    strategy_name = Prompt.ask("Strategy", choices=["basic", "premium", "risk"])
    strategy_map = {
        "basic": BasicScoringStrategy(),
        "premium": PremiumScoringStrategy(),
        "risk": RiskBasedScoringStrategy(),
    }
    updated = facade.rescore_lead(lead.id, strategy_map[strategy_name])
    console.print(f"  ✅ New score: [bold green]{updated.score}[/bold green] "
                  f"(using {strategy_name} strategy)")


# ── Main loop ──────────────────────────────────────────────────────────────

def main():
    show_banner()
    console.print("\n[dim]Tip: Run option 7 first to seed demo data.[/dim]")

    while True:
        choice = show_menu()
        console.rule()

        if choice == "1":
            action_list_leads()
        elif choice == "2":
            action_assign_leads()
        elif choice == "3":
            action_advance_status()
        elif choice == "4":
            action_rescore()
        elif choice == "5":
            display_agents_table(facade.list_agents())
        elif choice == "6":
            display_report(facade.get_report())
        elif choice == "7":
            console.print("[cyan]Seeding demo data...[/cyan]")
            seed_agents()
            seed_leads()
        elif choice == "0":
            console.print("[bold cyan]Goodbye! 👋[/bold cyan]")
            break
        else:
            console.print("[red]Invalid option.[/red]")


if __name__ == "__main__":
    main()
