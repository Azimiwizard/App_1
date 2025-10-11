# How to Deploy Your Project to Railway

Follow these steps to deploy your Flask app to Railway:

1. Push your code to GitHub:
   - Initialize a git repository (if not already done):
     ```
     git init
     ```
   - Add all files to the repository:
     ```
     git add .
     ```
   - Commit the files:
     ```
     git commit -m "Initial commit"
     ```
   - Create a new repository on GitHub:
     - Go to https://github.com and log in.
     - Click the "+" icon and select "New repository".
     - Enter a repository name and create the repo.
   - Add the remote repository URL (replace `<your-repo-url>` with your GitHub repo URL):
     ```
     git remote add origin <your-repo-url>
     ```
   - Push the code to GitHub:
     ```
     git push -u origin main
     ```

2. Deploy to Railway:
   - Go to https://railway.app and sign up/log in.
   - Click "New Project" and select "Deploy from GitHub repo".
   - Connect your GitHub account and select your repository.
   - Railway will automatically detect it's a Python app and deploy it.

3. Configure Environment Variables in Railway:
   - In your Railway project dashboard, go to "Variables" tab.
   - Add the following environment variables:
     - `SECRET_KEY`: A random secret key for Flask sessions.
     - `OPENAI_API_KEY`: Your OpenAI API key for AI order parsing.
     - `N8N_WEBHOOK_URL`: (Optional) URL for n8n webhook integration.
   - Railway provides `DATABASE_URL` automatically for PostgreSQL.

4. Database Setup:
   - Railway provides PostgreSQL automatically.
   - The app will create tables on startup.

Your app should now be live on Railway!

If you need help with any step, let me know.
