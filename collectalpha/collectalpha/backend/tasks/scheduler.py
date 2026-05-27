import os

from apscheduler.schedulers.blocking import BlockingScheduler

from backend.scanners.opportunity_scanner import scan_market
from backend.alerts.discord_alerts import send_discord_embed

scheduler = BlockingScheduler()


def get_scan_limit():
    value = os.getenv("SCAN_LIMIT", "none").strip().lower()

    if value in ["none", "no_limit", "all", ""]:
        return None

    try:
        return int(value)
    except ValueError:
        print(f"Invalid SCAN_LIMIT={value}. Using no limit.")
        return None


def should_rebuild_universe():
    return os.getenv("REBUILD_UNIVERSE_ON_START", "false").strip().lower() == "true"


def startup_ping():
    send_discord_embed(
        title="🟢 CollectAlpha Online",
        description="Cloud scanner successfully started on Railway.",
        fields=[
            {
                "name": "Status",
                "value": "Operational",
                "inline": True
            },
            {
                "name": "Mode",
                "value": "Automated Cloud Worker",
                "inline": True
            }
        ]
    )


@scheduler.scheduled_job("interval", minutes=15)
def scheduled_market_scan():
    print("Running automated market scan...")

    scan_limit = get_scan_limit()
    rebuild_universe = should_rebuild_universe()

    try:
        results = scan_market(
            limit=scan_limit,
            rebuild_universe=rebuild_universe
        )

        total_results = len(results) if results else 0

        send_discord_embed(
            title="🔍 CollectAlpha Scan Complete",
            description="Automated market scan finished successfully.",
            fields=[
                {
                    "name": "Opportunities Found",
                    "value": str(total_results),
                    "inline": True
                },
                {
                    "name": "Scan Limit",
                    "value": "No limit" if scan_limit is None else str(scan_limit),
                    "inline": True
                },
                {
                    "name": "Rebuild Universe",
                    "value": str(rebuild_universe),
                    "inline": True
                }
            ]
        )

        print(f"Market scan complete. Opportunities found: {total_results}")

    except Exception as e:
        print(f"Market scan failed: {e}")

        send_discord_embed(
            title="⚠️ CollectAlpha Scan Error",
            description="The scanner hit an error, but the worker is still alive.",
            fields=[
                {
                    "name": "Error",
                    "value": str(e)[:900],
                    "inline": False
                }
            ]
        )


if __name__ == "__main__":
    print("CollectAlpha scheduler started...")
    startup_ping()
    scheduled_market_scan()
    scheduler.start()