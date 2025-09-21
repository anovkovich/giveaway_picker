import json
from flask import Flask, render_template, jsonify

# Initialize the Flask application
app = Flask(__name__)

# --- Route 1: The main webpage ---
# This tells Flask that when someone visits the main URL ('/'),
# it should run this function.
@app.route('/')
def index():
    """
    Renders the main giveaway page (index.html).
    """
    return render_template('index.html')

# --- Route 2: The data endpoint ---
# This creates a URL '/get_comments' that the JavaScript on your
# webpage can call to get the giveaway participants' data.
@app.route('/get_comments')
def get_comments():
    """
    Opens the JSON file, reads the data, and returns it.
    This acts as an API for our front end.
    """
    try:
        with open('comments_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        # If the file doesn't exist, return an error message.
        return jsonify({"error": "comments_data.json not found"}), 404
    except json.JSONDecodeError:
        # If the file is empty or corrupted, return an error.
        return jsonify({"error": "Failed to decode JSON from comments_data.json"}), 500


# This is the standard entry point for a Flask application.
# It tells Python to run the web server if this script is executed directly.
if __name__ == '__main__':
    # debug=True allows you to see errors in the browser and automatically
    # reloads the server when you make changes to the code.
    app.run(debug=True)