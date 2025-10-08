# Deployment Instructions for Heroku

This document provides steps to deploy the Flask app to Heroku using Gunicorn as the production WSGI server.

## Prerequisites

- Install [Git](https://git-scm.com/download/win) for Windows
- Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install)
- Have a Heroku account and verify it by adding payment information at https://heroku.com/verify (required to create apps)

## Steps

1. **Login to Heroku**

```bash
heroku login
```

2. **Create a new Heroku app**

```bash
heroku create your-app-name
```

3. **Set environment variables**

Set your SECRET_KEY and any other environment variables:

```bash
heroku config:set SECRET_KEY='your-secret-key'
```

If you want to use a Heroku Postgres database, add the addon:

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

4. **Push your code to Heroku**

```bash
git push heroku main
```

5. **Run database migrations or seed data**

If you have CLI commands to create tables or seed data, run them:

```bash
heroku run flask seed
heroku run flask make_admin
```

6. **Scale the web dyno**

```bash
heroku ps:scale web=1
```

7. **Open your app**

```bash
heroku open
```

## Notes

- The `Procfile` specifies to use Gunicorn to run the app: `web: gunicorn main:app`
- The `runtime.txt` specifies the Python version for Heroku
- The app creates the database tables on startup automatically

For more details, see the [Heroku Flask Deployment Guide](https://devcenter.heroku.com/articles/getting-started-with-python).
