import os
import sys
import pytz
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

# Ensure we can import from local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.news_search import search_recent_news
from orchestrator.curator import curate_and_prepare_content

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AlgarveeumPipeline")

def run_daily_pipeline():
    logger.info("Starting Algarve É Um daily pipeline...")
    try:
        # Step 1: Search News
        logger.info("Step 1: Searching for recent news (Tavily)...")
        articles = search_recent_news()
        logger.info(f"Retrieved {len(articles)} raw articles.")
        
        # Step 2: AI Curation (Select, Generate, Score, Save)
        logger.info("Step 2: AI Curation, Generation, and Scoring...")
        curated_results = curate_and_prepare_content(articles)
        logger.info(f"Approved {len(curated_results)} content packages.")
        
        # Step 3: Trigger Email Notifications (Mock placeholder for Phase 5)
        logger.info("Step 3: Triggering Email Dispatch...")
        from notifier.email_sender import send_approval_email
        if curated_results:
             send_approval_email(curated_results)
             logger.info("Email sent successfully.")
        
        logger.info("Daily pipeline completed successfully.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    lisbon_tz = "Europe/Lisbon"
    scheduler = BlockingScheduler(timezone=lisbon_tz)
    
    # Schedule to run every day at 08:00 Lisbon time
    scheduler.add_job(run_daily_pipeline, 'cron', hour=8, minute=0)
    
    logger.info(f"Scheduler started successfully. Next automated run scheduled for 08:00 {lisbon_tz}.")
    
    # Enable this loop to keep scheduler running.
    # To run instantly for debugging, call run_daily_pipeline() manually.
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user.")
