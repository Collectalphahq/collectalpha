from apscheduler.schedulers.blocking import BlockingScheduler
from backend.scanners.opportunity_scanner import scan_market

scheduler = BlockingScheduler()


@scheduler.scheduled_job("interval", minutes=1)
def scheduled_market_scan():
    print("Running automated market scan...")
    scan_market(limit=100)


if __name__ == "__main__":
    print("CollectAlpha scheduler started...")
    scheduler.start()