# Setup Guide

## 1. Get a Bungie API Key

1. Go to https://www.bungie.net/en/Application and log in
2. Click **Create New App**
3. Fill in:
   - **App Name**: anything (e.g. "My Progression Assessor")
   - **Website**: your domain
   - **OAuth Client Type**: `Confidential`
   - **Redirect URL**: `https://yourdomain.com/auth/callback`
   - **Scope**: check `Read your Destiny 2 information`
4. Submit — you'll get an **API Key**, **OAuth Client ID**, and **OAuth Client Secret**

## 2. Get an Anthropic API Key

Sign up at https://console.anthropic.com and create an API key.

## 3. Configure the App

Copy `.env.example` to `.env` and fill in all values:

```
BUNGIE_API_KEY=...
BUNGIE_CLIENT_ID=...
BUNGIE_CLIENT_SECRET=...
FLASK_SECRET_KEY=<generate a random 32+ char string>
ANTHROPIC_API_KEY=...
APP_BASE_URL=https://yourdomain.com
```

## 4. Deploy to cPanel

1. Upload all files to a directory on your cPanel host (e.g. `public_html/destiny-assess/` or a subdomain root)
2. In cPanel, go to **Setup Python App**
3. Create a new application:
   - **Python version**: 3.11 or newer
   - **Application root**: the folder you uploaded to
   - **Application URL**: your domain/subdomain
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`
4. Click **Create**, then open the virtual environment terminal in cPanel
5. Run: `pip install -r requirements.txt`
6. Make sure `.env` is in the application root
7. Restart the app

## 5. Test

Visit your domain — you should see the login page. Click **Login with Bungie.net**, authorise, and the assessment will run automatically.
