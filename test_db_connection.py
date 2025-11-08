import os
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

supabase = create_client(os.environ.get('SUPABASE_URL'),
                         os.environ.get('SUPABASE_ANON_KEY'))
print('Testing Supabase connection...')

try:
    response = supabase.table('users').select('*').limit(1).execute()
    print('Connection successful, found', len(response.data), 'users')
except Exception as e:
    print('Connection failed:', str(e)[:100])
