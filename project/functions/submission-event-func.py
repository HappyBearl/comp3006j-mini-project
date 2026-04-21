import json
import os
from urllib import request, error

PROCESSING_FUNCTION_URL = os.environ.get('PROCESSING_FUNCTION_URL', '')

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

    print(f"submission-event-func received submission_id: {submission_id}")

    if PROCESSING_FUNCTION_URL and submission_id:
        data = json.dumps({
            'submission_id': submission_id,
            'title': title,
            'description': description,
            'poster_filename': poster_filename
        }).encode('utf-8')
        req = request.Request(PROCESSING_FUNCTION_URL, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with request.urlopen(req, timeout=5) as resp:
                print(f"Response from processing-func: {resp.read().decode()}")
        except error.URLError as e:
            print(f"Error: {e}")
    else:
        print("PROCESSING_FUNCTION_URL not set or submission_id missing")

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Event received'})
    }