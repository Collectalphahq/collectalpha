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


@scheduler.scheduled_job("interval", minutes=15)
def scheduled_market_scan():
    print("Running automated market scan...")
    scan_market(limit=100)


if __name__ == "__main__":
    print("CollectAlpha scheduler started...")
    startup_ping()
    scheduler.start()