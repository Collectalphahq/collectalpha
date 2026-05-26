from apscheduler.schedulers.blocking import BlockingScheduler
from backend.scanners.opportunity_scanner import scan_market
from backend.alerts.discord_alerts import send_discord_embed

scheduler = BlockingScheduler()


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


@scheduler.scheduled_job("interval", minutes=1)
def scheduled_market_scan():
    print("Running automated market scan...")

    try:
        results = scan_market(limit=100)

        total_results = len(results) if results else 0

        send_discord_embed(
            title="🔍 CollectAlpha Scan Complete",
            description="Automated market scan finished successfully.",
            fields=[
                {
                    "name": "Results Found",
                    "value": str(total_results),
                    "inline": True
                },
                {
                    "name": "Scan Limit",
                    "value": "100",
                    "inline": True
                }
            ]
        )

        print(f"Market scan complete. Results found: {total_results}")

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
    scheduler.start()