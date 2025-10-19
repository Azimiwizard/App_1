# How to Deploy Your Project to Render

Follow these steps to deploy your Flask app to Render:

1.  **Push your code to GitHub:**
    *   Initialize a git repository (if not already done):
        ```
        git init
        ```
    *   Add all files to the repository:
        ```
        git add .
        ```
    *   Commit the files:
        ```
        git commit -m "Initial commit"
        ```
    *   Create a new repository on GitHub:
        *   Go to https://github.com and log in.
        *   Click the "+" icon and select "New repository".
        *   Enter a repository name and create the repo.
    *   Add the remote repository URL (replace `<your-repo-url>` with your GitHub repo URL):
        ```
        git remote add origin <your-repo-url>
        ```
    *   Push the code to GitHub:
        ```
        git push -u origin main
        ```

2.  **Deploy to Render:**
    *   Go to https://render.com and sign up/log in.
    *   Click "New +" and select "Web Service".
    *   Connect your GitHub account and select your repository.
    *   Render will automatically detect it's a Python app and use the `render.yaml` file for configuration.

3.  **Configure Environment Variables in Render:**
    *   In your web service's "Environment" tab, add the following environment variables:
        *   `SUPABASE_URL`: Your Supabase project URL.
        *   `SUPABASE_ANON_KEY`: Your Supabase anon key.
        *   `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key.
        *   `SECRET_KEY`: A random secret key for Flask sessions.
        *   `OPENAI_API_KEY`: Your OpenAI API key for AI order parsing.
        *   `N8N_WEBHOOK_URL`: (Optional) URL for n8n webhook integration.

Your app should now be live on Render!

If you need help with any step, let me know.
