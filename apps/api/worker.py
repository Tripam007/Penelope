"""
PENELOPE Backend - Dedicated Background Ingestion & Simulation Worker
Runs the APScheduler event loop for river gauge simulation, weather ingestion,
and automated early-warning risk evaluation in the worker container.
"""

import os
import time
import signal
import logging
from apps.api.database import init_db
from apps.api.seed import seed_database
from apps.api.ingestion.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("penelope.worker")

running = True


def handle_exit(signum, frame):
    global running
    logger.info("Shutdown signal received in worker. Stopping scheduler...")
    running = False
    stop_scheduler()


def run_worker():
    global running
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    logger.info("Starting PENELOPE background worker process...")
    init_db()
    seed_database()

    scheduler = start_scheduler()
    logger.info(f"Worker scheduler started with {len(scheduler.get_jobs())} background tasks.")

    try:
        while running:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        stop_scheduler()
        logger.info("PENELOPE background worker terminated gracefully.")


if __name__ == "__main__":
    run_worker()

