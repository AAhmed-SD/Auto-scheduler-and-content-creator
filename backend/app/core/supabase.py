from supabase import create_client, Client
from .config import get_settings
import os
from dotenv import load_dotenv

load_dotenv()

settings = get_settings()

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_supabase():
    return supabase

async def get_user_by_email(email: str):
    try:
        response = supabase.table('users').select("*").eq('email', email).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        raise Exception(f"Failed to fetch user: {str(e)}")

async def create_user(email: str, password: str, full_name: str):
    try:
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # Create profile in users table
            user_response = supabase.table('users').insert({
                "id": auth_response.user.id,
                "email": email,
                "full_name": full_name,
                "role": "creator"
            }).execute()
            
            return user_response.data[0]
        return None
    except Exception as e:
        raise Exception(f"Failed to create user: {str(e)}")

# Initialize Supabase client
supabase: Client = get_supabase_client() 