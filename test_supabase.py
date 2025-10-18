import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.environ.get('SUPABASE_URL')
supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY')
supabase_service_role_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
database_url = os.environ.get('DATABASE_URL')

print("SUPABASE_URL:", supabase_url)
print("SUPABASE_ANON_KEY:",
      supabase_anon_key[:10] + "..." if supabase_anon_key else None)
print("SUPABASE_SERVICE_ROLE_KEY:",
      supabase_service_role_key[:10] + "..." if supabase_service_role_key else None)
print("DATABASE_URL:", database_url[:20] + "..." if database_url else None)

if supabase_url and supabase_anon_key:
    try:
        supabase: Client = create_client(supabase_url, supabase_anon_key)
        print("Supabase client created successfully.")
        # Try a simple query
        response = supabase.table('users').select('*').limit(1).execute()
        print("Supabase query successful.")
    except Exception as e:
        print(f"Supabase error: {e}")
else:
    print("Supabase credentials not found.")
