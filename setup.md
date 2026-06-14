# Destiny 2 Progression Assessor – Setup Guide

## Prerequisites

- Python 3.11+
- A Bungie.net developer account
- An Anthropic API key
- A web host with cPanel (for production) or any Python-capable server

---

## 1. Get a Bungie API Key

1. Go to https://www.bungie.net/en/Application and sign in.
2. Click **Create New App**.
3. Fill in the form:
   - **Application Name**: anything descriptive (e.g. "My D2 Assessor")
   - **Website**: your domain (e.g. `https://yourdomain.com`)
   - **Application Status**: Private (for personal use) or Public
   - **OAuth Client Type**: **Confidential**
   - **Redirect URL**: `https://yourdomain.com/auth/callback`
     - For local dev: `http://localhost:5000/auth/callback`
   - **Scope**: Check **Read your Destiny 2 information** (and any others you need)
   - **Origin Header**: `https://yourdomain.com`
4. Submit. You'll receive:
   - **API Key** → `BUNGIE_API_KEY`
   - **OAuth client_id** → `BUNGIE_CLIENT_ID`
   - **OAuth client_secret** → `BUNGIE_CLIENT_SECRET`

---

## 2. Get an Anthropic API Key

1. Go to https://console.anthropic.com/ and sign in or create an account.
2. Navigate to **API Keys** and create a new key.
3. Copy the key → `ANTHROPIC_API_KEY`

---

## 3. Configure the App

Copy `.env.example` to `.env` and fill in all values:

```bash
cp .env.example .env
```

Edit `.env`:

```
BUNGIE_API_KEY=your_actual_api_key
BUNGIE_CLIENT_ID=your_actual_client_id
BUNGIE_CLIENT_SECRET=your_actual_client_secret
FLASK_SECRET_KEY=some_long_random_string_here
ANTHROPIC_API_KEY=your_actual_anthropic_key
APP_BASE_URL=https://yourdomain.com
```

Generate a secure `FLASK_SECRET_KEY` with:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 4. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit http://localhost:5000

> **Note**: For local OAuth to work, temporarily add `http://localhost:5000/auth/callback`
> as a redirect URL in your Bungie app settings, and set `APP_BASE_URL=http://localhost:5000` in `.env`.

---

## 5. cPanel Deployment

### Upload Files

1. In cPanel, open **File Manager** and navigate to your domain's root (e.g. `public_html`) or a subdirectory.
2. Upload all project files, or use FTP/SFTP.

Alternatively, use Git:
```bash
git clone <your-repo-url> /home/yourusername/character-assess
```

### Set Up Python App in cPanel

1. In cPanel, find **Setup Python App** (under Software).
2. Click **Create Application**.
3. Configure:
   - **Python version**: 3.11 (or highest available)
   - **Application root**: path to your uploaded folder (e.g. `/home/user/character-assess`)
   - **Application URL**: your domain or subdomain
   - **Application startup file**: `passenger_wsgi.py`
   - **Application Entry point**: `application`
4. Click **Create**.

### Install Requirements

In the cPanel Python App interface, there is a pip/requirements section, or you can run via the terminal:

```bash
source /home/yourusername/virtualenv/character-assess/3.11/bin/activate
cd /home/yourusername/character-assess
pip install -r requirements.txt
```

### Create .env File

In File Manager or via SSH, create `.env` in the application root:

```bash
cp .env.example .env
nano .env  # fill in real values
```

### Restart the App

In the cPanel Python App interface, click **Restart** after making changes.

---

## 6. Bungie Redirect URL

Make sure the redirect URL registered in your Bungie app exactly matches:

```
https://yourdomain.com/auth/callback
```

(No trailing slash, correct protocol.)

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ErrorCode` not 1 from Bungie API | Check your API key and OAuth credentials |
| OAuth redirect mismatch | Ensure `APP_BASE_URL` in `.env` matches the redirect URL in Bungie app settings |
| No Destiny 2 account found | User must have played Destiny 2 and have an active character |
| Claude API error | Check `ANTHROPIC_API_KEY` and account credit balance |
| 500 errors on cPanel | Check the error log in cPanel > Errors, or `stderr.log` in your app folder |
