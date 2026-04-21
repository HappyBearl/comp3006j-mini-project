import json
import os
from urllib import request, error

DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', 'http://172.17.33.70:5002')

def handler(event, context):
    # Handling events of type bytes
    if isinstance(event, bytes):
        event = event.decode('utf-8')
    if isinstance(event, str):
        event = json.loads(event)
    if 'body' in event:
        body = json.loads(event['body'])
    else:
        body = event

    submission_id = body.get('submission_id')
    status = body.get('status')
    status_note = body.get('status_note', '')

    print(f"result-update-func received submission_id: {submission_id}, status: {status}")

    if not submission_id:
        print("ERROR: No submission_id, aborting update")
        return {'status': 'error', 'message': 'Missing submission_id'}

    url = f"{DATA_SERVICE_URL}/submissions/{submission_id}/status"
    data = json.dumps({'status': status, 'status_note': status_note}).encode('utf-8')
    req = request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='PUT')
    try:
        with request.urlopen(req, timeout=10) as resp:
            response_body = resp.read().decode()
            print(f"Update response: {response_body}")
            return {'status': 'updated', 'response': response_body}
    except error.URLError as e:
        print(f"Error updating data service: {e}")
        return {'status': 'error', 'message': str(e)}