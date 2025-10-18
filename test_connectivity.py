from dotenv import load_dotenv
import os
import urllib.request
import urllib.error

url = 'https://mthtuygkcygsctcjbyzk.supabase.co/auth/v1/health'
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im10aHR1eWdrY3lnc2N0Y2pieXprIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg5MzM3NDUsImV4cCI6MjA0NDUwOTc0NX0'}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        print(f"Success: {response.status}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
except urllib.error.URLError as e:
    print(f"URL Error: {e.reason}")
except Exception as e:
    print(f"Other Error: {e}")

# Test database connection
load_dotenv()
database_url = os.environ.get('DATABASE_URL')
print(f"DATABASE_URL: {database_url[:50]}...")

try:
    import psycopg2
    conn = psycopg2.connect(database_url)
    print("Database connection successful")
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
