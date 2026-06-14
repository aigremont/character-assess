# Destiny 2 Progression Assessor – Setup Guide

## What you need

- A cPanel web hosting account (with Python app support)
- A Bungie.net account
- A Claude Pro account at claude.ai

---

## 1. Get a Bungie API Key

1. Go to https://www.bungie.net/en/Application and sign in.
2. Click **Create New App** and fill in the form:
   - **Application Name**: anything (e.g. "My D2 Assessor")
   - **Website**: your domain (e.g. `https://yourdomain.com`)
   - **OAuth Client Type**: **Confidential**
   - **Redirect URL**: `https://yourdomain.com/auth/callback`
   - **Scope**: Check **Read your Destiny 2 information**
   - **Origin Header**: `https://yourdomain.com`
3. Submit. Note down:
   - **API Key** → `BUNGIE_API_KEY`
   - **OAuth client_id** → `BUNGIE_CLIENT_ID`
   - **OAuth client_secret** → `BUNGIE_CLIENT_SECRET`

---

## 2. Upload the App to cPanel

1. Log in to cPanel and open **File Manager**.
2. Navigate to the folder where you want to host the app (e.g. a subdomain folder).
3. Upload all the project files — or use cPanel's **Git Version Control** to clone the repository directly on the server.

---

## 3. Set Up the Python App in cPanel

1. In cPanel, go to **Software → Setup Python App**.
2. Click **Create Application** and configure:
   - **Python version**: 3.11 (or highest available)
   - **Application root**: the folder you uploaded to
   - **Application URL**: your domain or subdomain
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`
3. Click **Create**.
4. In the app interface, find the **pip install** / requirements section and point it at `requirements.txt`. cPanel will install the dependencies on the server.

---

## 4. Create the .env File

In cPanel **File Manager**, open the application folder and create a new file called `.env`. You can copy the contents of `.env.example` as a starting point, then fill in your real values:

```
BUNGIE_API_KEY=your_actual_api_key
BUNGIE_CLIENT_ID=your_actual_client_id
BUNGIE_CLIENT_SECRET=your_actual_client_secret
FLASK_SECRET_KEY=any_long_random_string
APP_BASE_URL=https://yourdomain.com
```

For `FLASK_SECRET_KEY`, just type a long random string of letters and numbers — it only needs to be unguessable.

---

## 5. Restart the App

Back in **Setup Python App**, click **Restart**. The app should now be live at your domain.

---

## 6. Bungie Redirect URL

Make sure the redirect URL in your Bungie app settings exactly matches:

```
https://yourdomain.com/auth/callback
```

No trailing slash, correct protocol. If these don't match, OAuth login will fail.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| OAuth redirect mismatch | Check that `APP_BASE_URL` in `.env` matches the redirect URL in your Bungie app settings exactly |
| `ErrorCode` not 1 from Bungie API | Check your `BUNGIE_API_KEY` is correct |
| No Destiny 2 account found | Your Bungie account must have an active Destiny 2 character |
| 500 errors | Check cPanel > Errors log, or `stderr.log` in your app folder |
