from flask import Flask, request, jsonify
import pymysql
import os
import uuid

app = Flask(__name__)

DB_HOST = os.environ.get('DB_HOST', 'rm-bp1414blhva111d46.mysql.rds.aliyuncs.com')
DB_USER = os.environ.get('DB_USER', 'poster_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Poster123!')
DB_NAME = os.environ.get('DB_NAME', 'poster_db')

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/submissions', methods=['POST'])
def create_submission():
    data = request.get_json()
    submission_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO submissions (id, title, description, poster_filename, status, status_note) VALUES (%s, %s, %s, %s, %s, %s)",
        (submission_id, data['title'], data['description'], data['poster_filename'], 'PENDING', 'Processing...')
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'id': submission_id}), 201

@app.route('/submissions/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM submissions WHERE id = %s", (submission_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return jsonify(result)
    return jsonify({'error': 'Not found'}), 404

@app.route('/submissions/<submission_id>/status', methods=['PUT'])
def update_status(submission_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE submissions SET status = %s, status_note = %s WHERE id = %s",
        (data['status'], data.get('status_note', ''), submission_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'updated'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)