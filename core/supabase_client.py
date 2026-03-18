import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """
    Initializes and returns a singleton Supabase database client.
    Requires SUPABASE_URL and SUPABASE_KEY environment variables.
    """
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Supabase credentials not found in environment variables.")
        
    return create_client(url, key)

# Singleton instance for direct imports if preferred
supabase = get_supabase_client()
