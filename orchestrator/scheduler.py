import os
import sys
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.news_search import search_recent_news
from notifier.email_sender import send_raw_articles_email
from core.supabase_client import supabase

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AlgarveeumPipeline")

def get_todays_calendar_entry():
    """Fetches the planned content_type from the calendar for today's date."""
    today = datetime.now()
    start_of_day = today.replace(hour=0, minute=0, second=0).isoformat()
    end_of_day = today.replace(hour=23, minute=59, second=59).isoformat()
    
    try:
        res = supabase.table("calendar_entries").select("*").gte("date", start_of_day).lte("date", end_of_day).limit(1).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        logger.error(f"Failed to fetch calendar: {e}")
    return None

def run_daily_pipeline():
    logger.info("Starting Human-First Calendar-Aware Pipeline...")
    try:
        # Step 0: Check Calendar
        cal_entry = get_todays_calendar_entry()
        content_type = cal_entry['content_type'] if cal_entry else "news_reaction"
        calendar_id = cal_entry['id'] if cal_entry else None
        
        logger.info(f"Targeting Editorial Content: {content_type}")
        
        # Step 1: Search News
        articles = search_recent_news(content_type)
        logger.info(f"Retrieved {len(articles)} valid raw articles.")
        
        # Step 2: Insert Raw Articles to DB (bypass Claude Curator)
        raw_db_articles = []
        for art in articles:
            # Check duplicate
            res = supabase.table("published_content").select("id").eq("url", art['url']).execute()
            if len(res.data) == 0:
                # Insert new raw article
                pc_res = supabase.table("published_content").insert({
                    "url": art['url'],
                    "title": art['title'],
                    "summary": art['summary'][:1000] if art['summary'] else "",
                    "status": "raw"
                }).execute()
                
                art['content_id'] = pc_res.data[0]['id']
                raw_db_articles.append(art)
                
        logger.info(f"Saved {len(raw_db_articles)} fresh raw articles to database.")
        
        # Step 3: Trigger Email Notifications for the Human to choose
        if raw_db_articles:
             send_raw_articles_email(raw_db_articles, calendar_id, content_type)
             logger.info("Email of raw articles sent successfully.")
        else:
             logger.info("No new articles to send today. Try running again or check later.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)

if __name__ == "__main__":
    lisbon_tz = "Europe/Lisbon"
    scheduler = BlockingScheduler(timezone=lisbon_tz)
    scheduler.add_job(run_daily_pipeline, 'cron', hour=8, minute=0)
    logger.info(f"Calendar-Aware Scheduler started. Next run scheduled for 08:00 {lisbon_tz}.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
