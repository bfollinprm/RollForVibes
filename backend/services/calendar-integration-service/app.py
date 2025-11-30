import os
import datetime
import yaml
from flask import Flask, jsonify
from flask_cors import CORS
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)
# Allow CORS so the frontend (port 8080) can talk to this backend (port 5000)
CORS(app)

def get_config():
    """Reads the shared campaign.yml file."""
    try:
        with open('.env', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return {}

@app.route('/api/next-session', methods=['GET'])
def next_session():
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    # Read Calendar ID from the shared yaml file, or fallback to env var
    config = get_config()
    calendar_id = config.get('calendar', {}).get('calendarId') or os.environ.get('GOOGLE_CALENDAR_ID')

    if not api_key or not calendar_id:
        return jsonify({"error": "Missing API Key or Calendar ID"}), 500

    try:
        service = build('calendar', 'v3', developerKey=api_key)
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=1,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        if not events:
            return jsonify({"message": "No upcoming sessions found."})

        event = events[0]
        start = event['start'].get('dateTime', event['start'].get('date'))
        
        # Format the date nicely (e.g., "Nov 28, 2025")
        date_obj = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
        formatted_date = date_obj.strftime("%b %d, %Y")

        return jsonify({
            "title": event.get('summary', 'Next Session'),
            "date": formatted_date,
            "link": event.get('htmlLink')
        })

    except HttpError as error:
        return jsonify({"error": str(error)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)