import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY or not SUPABASE_ANON_KEY:
    raise ValueError("Supabase environment variables not set.")

# Use the Service Role Key for backend operations for full access (bypasses RLS)
# Or use the Anon Key if you want RLS to apply to your backend as well.
# For this app, we'll use the Service Key for admin-like access from backend.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# You might also want a client that respects RLS for certain operations
# supabase_rls: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
