import json
import os
from urllib import request, error

RESULT_UPDATE_FUNCTION_URL = os.environ.get('RESULT_UPDATE_FUNCTION_URL', '')

def apply_rules(title, description, poster_filename):
    if not title or not description or not poster_filename:
        return 'INCOMPLETE', 'Missing required fields'
    if len(description) < 30:
        return 'NEEDS_REVISION', f'Description too short ({len(description)} chars, need 30)'
    valid = ['.jpg', '.jpeg', '.png']
    if not any(poster_filename.lower().endswith(ext) for ext in valid):
        return 'NEEDS_REVISION', f'Invalid filename extension (must be .jpg/.jpeg/.png)'
    return 'READY', 'All checks passed'

def handler(event, context):
    if isinstance(event, bytes):
        event = event.decode('utf-8')
    if isinstance(event, str):
        event = json.loads(event)
    if 'body' in event:
        body = json.loads(event['body'])
    else:
        body = event

    submission_id = body.get('submission_id')
    title = body.get('title')
    description = body.get('description')
    poster_filename = body.get('poster_filename')

    print(f"processing-func received submission_id: {submission_id}")

    status, note = apply_rules(title, description, poster_filename)

    if RESULT_UPDATE_FUNCTION_URL and submission_id:
        data = json.dumps({
            'submission_id': submission_id,
            'status': status,
            'status_note': note
        }).encode('utf-8')
        req = request.Request(RESULT_UPDATE_FUNCTION_URL, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with request.urlopen(req, timeout=5) as resp:
                print(f"Response from result-update-func: {resp.read().decode()}")
        except error.URLError as e:
            print(f"Error calling result update function: {e}")
    else:
        print("RESULT_UPDATE_FUNCTION_URL not set or submission_id missing")

    return {
        'submission_id': submission_id,
        'status': status,
        'note': note
    }