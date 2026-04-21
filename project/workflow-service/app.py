from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)

DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', 'http://localhost:5002')
SUBMISSION_EVENT_FUNCTION_URL = os.environ.get('SUBMISSION_EVENT_FUNCTION_URL', '')

@app.route('/submit', methods=['POST', 'OPTIONS'])
def submit():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    
    # Call the Data Service to create a record
    resp = requests.post(f"{DATA_SERVICE_URL}/submissions", json=data)
    print(f"DEBUG: Data Service response status: {resp.status_code}, body: {resp.text}")
    if resp.status_code != 201:
        return jsonify({'error': 'Failed to create'}), 500
    sub = resp.json()
    submission_id = sub.get('id')
    print(f"DEBUG: submission_id from Data Service: {submission_id}")
    
    # Construct event payload
    event_payload = {
        'submission_id': submission_id,
        'title': data.get('title'),
        'description': data.get('description'),
        'poster_filename': data.get('poster_filename')
    }
    print(f"DEBUG: event_payload = {event_payload}")
    
    # Call submite-event-func
    if SUBMISSION_EVENT_FUNCTION_URL:
        payload_str = json.dumps(event_payload)
        print(f"DEBUG: Sending payload to submission-event-func: {payload_str}")
        headers = {'Content-Type': 'application/json'}
        try:
            requests.post(SUBMISSION_EVENT_FUNCTION_URL, data=payload_str, headers=headers, timeout=2)
        except Exception as e:
            print(f"Error calling submission-event-func: {e}")
    else:
        print("SUBMISSION_EVENT_FUNCTION_URL not set")
    
    return jsonify({'submission_id': submission_id}), 202

@app.route('/result/<submission_id>', methods=['GET', 'OPTIONS'])
def result(submission_id):
    if request.method == 'OPTIONS':
        return '', 200
    resp = requests.get(f"{DATA_SERVICE_URL}/submissions/{submission_id}")
    if resp.status_code != 200:
        return jsonify({'error': 'Not found'}), 404
    sub = resp.json()
    return jsonify({
        'status': sub['status'],
        'note': sub.get('status_note', ''),
        'title': sub.get('title'),
        'description': sub.get('description')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)