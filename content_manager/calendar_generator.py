import os
import sys
import json
import random
from datetime import datetime, timedelta

# Ensure we can import from local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import supabase
from content_manager.templates_library import get_all_templates

def generate_calendar_data(start_date=None, days=30):
    """
    Generates a 30-day content calendar spanning all types of templates.
    Ensures a varied mix of posts, optimal for the Portuguese audience.
    """
    if not start_date:
        start_date = datetime.now()
        
    templates = get_all_templates()
    
    # Weightings or custom logic could go here to prioritize 'news_reaction' during weekdays etc.
    calendar_plan = []
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        # Best posting times in Portugal are often ~18:00 on weekdays, ~10:00 or ~19:00 on weekends
        is_weekend = current_date.weekday() >= 5
        post_hour = 10 if is_weekend else 18
        
        post_time = current_date.replace(hour=post_hour, minute=0, second=0, microsecond=0)
        
        # Select a random template mix (ensuring we rotate through all pillars)
        content_type = random.choice(templates)
        
        entry = {
            "date": post_time.isoformat(),
            "content_type": content_type,
            "topic": f"Tópico autogerado ({content_type}) - Preencher depois",
            "platform": "instagram_post",
            "status": "planned"
        }
        calendar_plan.append(entry)
        
    return calendar_plan

def push_calendar_to_db(calendar_plan):
    """Inserts the generated calendar entries into the Supabase database."""
    try:
        supabase.table("calendar_entries").insert(calendar_plan).execute()
        print(f"Successfully inserted {len(calendar_plan)} days into the calendar database.")
    except Exception as e:
        print(f"Error inserting calendar: {e}")

def export_calendar_markdown(calendar_plan, filename="content_calendar.md"):
    """Exports the plan to a readable markdown file."""
    markdown = "# Algarve É Um - Content Calendar (30 Dias)\n\n"
    markdown += "| Data/Hora | Plataforma | Tipo de Conteúdo | Tópico/Notas |\n"
    markdown += "|-----------|------------|------------------|--------------|\n"
    
    for entry in calendar_plan:
        dt = datetime.fromisoformat(entry['date']).strftime('%Y-%m-%d %H:%00')
        markdown += f"| {dt} | {entry['platform']} | `{entry['content_type']}` | {entry['topic']} |\n"
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Exported plan to {filename}")

if __name__ == "__main__":
    print("Generating 30-day calendar...")
    plan = generate_calendar_data()
    # push_calendar_to_db(plan)
    export_calendar_markdown(plan)
