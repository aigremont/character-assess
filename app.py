import os
from flask import Flask, redirect, request, session, url_for, render_template
from dotenv import load_dotenv
from bungie import BungieClient
from build_prompt import build_prompt

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-me')
app.config['APPLICATION_ROOT'] = os.environ.get('APPLICATION_ROOT', '/')
app.config['PREFERRED_URL_SCHEME'] = 'https'

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
        return render_template('error.html', message='No authorization code received from Bungie.')
    try:
        token_data = bungie.exchange_code(code)
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data.get('refresh_token', '')
        session['membership_id'] = token_data.get('membership_id', '')
        return redirect(url_for('assess'))
    except Exception as e:
        return render_template('error.html', message=f'Token exchange failed: {str(e)}')


@app.route('/assess')
def assess():
    if 'access_token' not in session:
        return redirect(url_for('index'))
    try:
        access_token = session['access_token']
        memberships = bungie.get_memberships(access_token)
        # Find primary destiny membership (not BungieNext=254)
        destiny_memberships = [
            m for m in memberships.get('destinyMemberships', [])
            if m.get('membershipType') != 254
        ]
        if not destiny_memberships:
            return render_template('error.html', message='No Destiny 2 account found.')
        # Prefer the primary membership
        primary = next(
            (m for m in destiny_memberships if m.get('crossSaveOverride') == m.get('membershipType')),
            destiny_memberships[0]
        )
        membership_type = primary['membershipType']
        membership_id = primary['membershipId']
        display_name = primary.get('displayName', 'Guardian')

        profile_data = bungie.get_characters(access_token, membership_type, membership_id)
        characters_data = profile_data.get('Response', {}).get('characters', {}).get('data', {})

        activity_histories = {}
        for char_id in characters_data:
            try:
                history = bungie.get_activity_history(access_token, membership_type, membership_id, char_id)
                activity_histories[char_id] = history
            except Exception:
                activity_histories[char_id] = {}

        full_data = {
            'profile': profile_data.get('Response', {}),
            'activity_histories': activity_histories,
            'display_name': display_name,
            'membership_type': membership_type,
            'membership_id': membership_id,
        }

        prompt = build_prompt(full_data)

        # Build character summaries for display
        characters = []
        char_component = profile_data.get('Response', {}).get('characters', {}).get('data', {})
        class_map = {0: 'Titan', 1: 'Hunter', 2: 'Warlock'}
        race_map = {0: 'Human', 1: 'Awoken', 2: 'Exo'}
        gender_map = {0: 'Male', 1: 'Female'}
        for char_id, char in char_component.items():
            characters.append({
                'id': char_id,
                'class': class_map.get(char.get('classType', -1), 'Unknown'),
                'race': race_map.get(char.get('raceType', -1), 'Unknown'),
                'gender': gender_map.get(char.get('genderType', -1), 'Unknown'),
                'light': char.get('light', 0),
                'emblem': char.get('emblemBackgroundPath', ''),
                'minutes_played': char.get('minutesPlayedTotal', 0),
            })

        return render_template('assess.html',
                               characters=characters,
                               prompt=prompt,
                               display_name=display_name)
    except Exception as e:
        return render_template('error.html', message=f'Assessment failed: {str(e)}')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
