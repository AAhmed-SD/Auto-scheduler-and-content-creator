from supabase import create_client, Client
from app.core.config import get_settings
import os
from dotenv import load_dotenv

load_dotenv()

settings = get_settings()

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and Key must be set in environment variables")
    
    return create_client(supabase_url, supabase_key)

# Initialize Supabase client
supabase: Client = get_supabase_client() 