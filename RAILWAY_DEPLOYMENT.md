# Deployment to Railway

Railway is a modern cloud platform for deploying apps.

## Prerequisites

- Railway account (free tier available)
- GitHub account (for connecting repo)

## Steps

1. **Connect GitHub Repo**

   - Go to https://railway.app
   - Create a new project
   - Connect your GitHub repository

2. **Add Database**

   - In Railway dashboard, add a PostgreSQL database
   - Railway will set DATABASE_URL automatically

3. **Set Environment Variables**

   - In Railway project settings, add:
     - SECRET_KEY: (required) Generate a strong secret key, e.g., using `openssl rand -hex 32`
     - DATABASE_URL: (auto-set by Railway PostgreSQL service)
     - TWILIO_ACCOUNT_SID: (optional, if using Twilio voice/WhatsApp)
     - TWILIO_AUTH_TOKEN: (optional, if using Twilio)
     - OPENAI_API_KEY: (optional, if using AI order parsing)
     - N8N_WEBHOOK_URL: (optional, if using n8n for order processing)

4. **Deploy**

   - Push code to GitHub, Railway deploys automatically
   - Or trigger deploy in dashboard

5. **Run Initial Commands (if needed)**

   - Use Railway CLI or web shell to run:
     ```
     python scripts/init_db_command.py
     ```
     Or seed via app if implemented.

6. **Access the App**

   - Railway provides a URL like https://your-app.railway.app

## Notes

- Railway uses Procfile if present for web command
- Database init is handled in main.py on startup; seeding runs automatically on first deploy
- Free tier: 512MB RAM, 1GB disk, etc.

## Troubleshooting

- **DB Connection Issues**: Check Railway logs for "DATABASE_URL environment variable is required" – ensure PostgreSQL service is added and DATABASE_URL is set.
- **Import Errors**: If errors due to nested directories, ensure only root files are committed (duplicates in stitch_app/ should be ignored).
- **Seeding Not Working**: Check logs for seeding messages; if not, run `python scripts/init_db_command.py` manually in Railway shell.
- **Admin User**: After deploy, use Railway shell: `python make_admin.py` to promote first user to admin.
