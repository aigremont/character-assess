# app.py
import os
from flask import Flask, render_template, redirect, request, session, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

from bungie import BungieClient
from claude_assess import assess_character

bungie = BungieClient()

@app.route('/')
def index():
    logged_in = 'access_token' in session
    return render_template('index.html', logged_in=logged_in)

@app.route('/auth/start')
def auth_start():
    return redirect(bungie.get_auth_url())

@app.route('/auth/callback')
def auth_callback():
    code = request.args.get('code')
    if not code:
        return render_template('error.html', error="No authorization code received from Bungie.")
    try:
        token_data = bungie.exchange_code(code)
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data.get('refresh_token', '')
        session['membership_id'] = token_data.get('membership_id', '')
        return redirect(url_for('assess'))
    except Exception as e:
        return render_template('error.html', error=f"Authentication failed: {str(e)}")

@app.route('/assess')
def assess():
    if 'access_token' not in session:
        return redirect(url_for('index'))
    try:
        access_token = session['access_token']
        memberships = bungie.get_memberships(access_token)

        # Find primary membership (not BungieNext/254)
        primary = None
        for m in memberships.get('destinyMemberships', []):
            if m.get('membershipType') != 254:
                primary = m
                break

        if not primary:
            return render_template('error.html', error="No Destiny 2 membership found.")

        membership_type = primary['membershipType']
        membership_id = primary['membershipId']
        display_name = primary.get('displayName', 'Guardian')

        # Get character data
        profile_data = bungie.get_characters(access_token, membership_type, membership_id)

        # Get activity history for each character
        characters = profile_data.get('Response', {}).get('characters', {}).get('data', {})
        activity_histories = {}
        for char_id in characters:
            try:
                activities = bungie.get_activity_history(access_token, membership_type, membership_id, char_id)
                activity_histories[char_id] = activities
            except Exception:
                activity_histories[char_id] = {}

        combined_data = {
            'profile': profile_data.get('Response', {}),
            'activity_histories': activity_histories,
            'display_name': display_name,
        }

        assessment_md = assess_character(combined_data)

        # Build character summary for template
        char_summaries = []
        for char_id, char in characters.items():
            char_summaries.append({
                'id': char_id,
                'class': _class_name(char.get('classType', 0)),
                'race': _race_name(char.get('raceType', 0)),
                'light': char.get('light', 0),
                'emblem': char.get('emblemBackgroundPath', ''),
            })

        import markdown as md
        assessment_html = md.markdown(assessment_md)

        return render_template('assess.html',
                               display_name=display_name,
                               characters=char_summaries,
                               assessment_html=assessment_html)
    except Exception as e:
        return render_template('error.html', error=f"Failed to fetch data: {str(e)}")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def _class_name(class_type):
    return {0: 'Titan', 1: 'Hunter', 2: 'Warlock'}.get(class_type, 'Unknown')

def _race_name(race_type):
    return {0: 'Human', 1: 'Awoken', 2: 'Exo'}.get(race_type, 'Unknown')

if __name__ == '__main__':
    app.run(debug=True)
