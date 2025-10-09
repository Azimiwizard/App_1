# Deployment to Google Cloud Platform (GCP) App Engine

## Prerequisites

- Google Cloud account (free to create)
- Google Cloud CLI (gcloud) installed

## Steps

1. **Create a GCP Project**

   - Go to https://console.cloud.google.com/
   - Create a new project or select existing.

2. **Enable App Engine API**

   - In GCP console, go to APIs & Services > Library
   - Search for "App Engine Admin API" and enable it.

3. **Install and Initialize gcloud CLI**

   - Download from https://cloud.google.com/sdk/docs/install
   - Run `gcloud init` and authenticate with your GCP account.
   - Set the project: `gcloud config set project YOUR_PROJECT_ID`

4. **Set up Cloud SQL (Database)**

   - In GCP console, go to SQL > Create instance > PostgreSQL
   - Choose free tier (if available) or minimal config.
   - Note the instance connection name (e.g., project:region:instance)
   - Create a database named 'stitch_menu' or as needed.
   - Create a user.

5. **Set Environment Variables**

   - In GCP console, go to App Engine > Settings > Environment variables
   - Set SECRET_KEY and DATABASE_URL
   - DATABASE_URL: postgresql://user:password@/database?host=/cloudsql/connection-name

6. **Deploy the App**

   - In your project directory, run:
     ```
     gcloud app deploy
     ```
   - Choose a region if prompted.

7. **Run Initial Commands**

   - After deployment, run:
     ```
     gcloud app instances list
     ```
     Then SSH into an instance or use Cloud Shell to run:
     ```
     flask --app main seed
     flask --app main make_admin
     ```

8. **Access the App**

   - The app will be at https://YOUR_PROJECT_ID.appspot.com

## Notes

- App Engine free tier: 28 instance hours/day, etc.
- Cloud SQL free tier: 1GB storage, etc.
- Costs apply if limits exceeded.
