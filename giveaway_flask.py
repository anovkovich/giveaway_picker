import json
from flask import Flask, render_template, request

app = Flask(__name__)


# --- Route 1: The new settings page ---
@app.route('/')
def settings():
    """Renders the settings page."""
    return render_template('settings.html')


# --- Route 2: The logic to filter contestants and start the giveaway ---
@app.route('/start', methods=['POST'])
def start_giveaway():
    """
    Reads the rules from the settings form, filters the JSON data,
    and renders the giveaway wheel page with the eligible contestants.
    """
    try:
        # 1. Load the raw data
        with open('comments_data.json', 'r', encoding='utf-8') as f:
            all_comments = json.load(f)

        # 2. Get the rules from the form submission
        required_mentions = int(request.form.get('mentions', 0))
        min_followers = int(request.form.get('min_followers', 0))
        allow_multiple_entries = 'allow_multiple' in request.form

        # 3. Filter the comments based on the rules
        eligible_comments = []
        for comment in all_comments:
            # Rule: Minimum followers
            if comment.get('followers', 0) < min_followers:
                continue

            # Rule: Required mentions
            if comment.get('comment', '').count('@') < required_mentions:
                continue

            # If all rules pass, add the comment
            eligible_comments.append(comment)

        # 4. Handle the "allow multiple entries" rule
        if not allow_multiple_entries:
            # If multiple entries are NOT allowed, we need to get unique users
            unique_entrants = {}
            for comment in eligible_comments:
                username = comment['username']
                if username not in unique_entrants:
                    unique_entrants[username] = comment
            # The final list is just the values (the comments) from our unique dictionary
            final_contestants = list(unique_entrants.values())
        else:
            # If multiple entries ARE allowed, the list is already good to go
            final_contestants = eligible_comments

        # 5. Render the wheel page, passing both the raw comments (for display)
        # and the filtered list of contestants (for the wheel).
        return render_template(
            'index.html',
            raw_comments_json=json.dumps(all_comments),
            contestants_json=json.dumps(final_contestants),
            required_mentions=required_mentions,
            allow_multiple_entries=allow_multiple_entries
        )

    except FileNotFoundError:
        return "Error: comments_data.json not found. Please run main.py first.", 404
    except Exception as e:
        return f"An error occurred: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)