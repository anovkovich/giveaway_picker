import json
import os
from flask import Flask, render_template, request, redirect, url_for, session
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, LoginRequired, UserNotFound

app = Flask(__name__)
app.secret_key = 'a-very-secret-key-for-giveaway-app'

SESSIONS_FOLDER = 'sessions'
if not os.path.exists(SESSIONS_FOLDER):
    os.makedirs(SESSIONS_FOLDER)


# --- ROUTE 1: The main entry point - Login Page ---
@app.route('/')
def login_page():
    return render_template('login.html')


# --- ROUTE 2: Handle scraping and session management ---
@app.route('/scrape', methods=['POST'])
def scrape_comments():
    cl = Client()

    username = request.form.get('username')
    password = request.form.get('password')
    shortcode = request.form.get('shortcode')
    verification_code = request.form.get('verification_code')

    fetch_followers = 'fetch_followers' in request.form

    session_file = os.path.join(SESSIONS_FOLDER, f"{username}.json")
    cl.delay_range = [1, 3]

    try:
        if os.path.exists(session_file):
            print(f"Found session file: {session_file}")
            cl.load_settings(session_file)
            cl.login(username, password)
            cl.get_timeline_feed()
            print("✅ Session loaded and valid.")
        else:
            print("No session file found, attempting fresh login.")
            if verification_code:
                cl.login(username, password, verification_code=verification_code)
            else:
                cl.login(username, password)
            cl.dump_settings(session_file)
            print(f"✅ New session saved to {session_file}")

        print(f"Fetching comments for shortcode: {shortcode}")
        media_pk = cl.media_pk_from_code(shortcode)
        comments = cl.media_comments(media_pk)
        print(f"Found {len(comments)} comments. Now fetching follower counts...")

        comments_data = []
        # ======================= THIS IS THE CRITICAL FIX =======================
        # We must loop through each comment and fetch the full user profile
        # to get the follower count.
        if fetch_followers:
            for comment in comments:
                try:
                    # Make the extra API call to get the full user object
                    user_info = cl.user_info_by_username(comment.user.username)
                    followers = user_info.follower_count
                except (UserNotFound, Exception) as e:
                    # If user is private, not found, or any other error, default to 0
                    print(f"Could not fetch info for {comment.user.username}: {e}")
                    followers = 0

                comments_data.append({
                    "username": comment.user.username,
                    "followers": followers,
                    "comment": comment.text
                })
        else:
            print("Skipping follower count fetch (fast).")
            for comment in comments:
                comments_data.append({
                    "username": comment.user.username,
                    "followers": 0,  # Default to 0 if not fetched
                    "comment": comment.text
                })
        # ======================================================================

        with open("comments_data.json", "w", encoding="utf-8") as f:
            json.dump(comments_data, f, ensure_ascii=False, indent=4)
        print("✅ Comments data saved to comments_data.json")

        session['followers_fetched'] = fetch_followers

        return redirect(url_for('settings_page'))

    except TwoFactorRequired:
        print("⚠️ 2FA required. Re-rendering login page.")
        return render_template('login.html',
                               two_factor_required=True,
                               username=username,
                               password=password,
                               shortcode=shortcode)
    except LoginRequired:
        print("LoginRequired error. Session might be corrupt. Deleting.")
        if os.path.exists(session_file):
            os.remove(session_file)
        return render_template('login.html', error="Your session was invalid. Please log in again.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('login.html', error=str(e))


# --- ROUTE 3: The giveaway rules settings page ---
@app.route('/settings')
def settings_page():
    return render_template('settings.html')


# --- ROUTE 4: Filter and start the actual giveaway ---
@app.route('/start', methods=['POST'])
def start_giveaway():
    try:
        with open('comments_data.json', 'r', encoding='utf-8') as f:
            all_comments = json.load(f)

        required_mentions = int(request.form.get('mentions', 0))
        min_followers = int(request.form.get('min_followers', 0))
        allow_multiple_entries = 'allow_multiple' in request.form

        eligible_comments = []
        for comment in all_comments:
            # Ensure followers is an integer before comparing
            follower_count = comment.get('followers', 0)
            if not isinstance(follower_count, int):
                follower_count = 0

            if follower_count < min_followers: continue
            if comment.get('comment', '').count('@') < required_mentions: continue
            eligible_comments.append(comment)

        if not allow_multiple_entries:
            # Use a dictionary to keep only the first eligible comment from each user
            unique_entrants = {c['username']: c for c in eligible_comments}
            final_contestants = list(unique_entrants.values())
        else:
            final_contestants = eligible_comments

        return render_template(
            'index.html',
            raw_comments_json=json.dumps(all_comments),
            contestants_json=json.dumps(final_contestants),
            required_mentions=required_mentions,
            allow_multiple_entries=allow_multiple_entries
        )
    except Exception as e:
        return f"An error occurred while starting the giveaway: {e}", 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)