from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# In-memory store for IP addresses that have already made a request
ip_store = set()

def init_db():
    conn = sqlite3.connect('personalities.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS personalities
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  mbti TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/persons', methods=['GET'])
def get_persons():
    conn = sqlite3.connect('personalities.db')
    c = conn.cursor()
    c.execute("SELECT * FROM personalities")
    persons = [{'id': row[0], 'name': row[1], 'mbti': row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(persons)

@app.route('/api/persons', methods=['POST'])
def add_person():
    data = request.json
    if not data or 'name' not in data or 'mbti' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    # Get the client IP address
    client_ip = request.remote_addr

    # Check if this IP has already made a request
    if client_ip in ip_store:
        return jsonify({'error': 'This IP has already made a request'}), 429

    try:
        conn = sqlite3.connect('personalities.db')
        c = conn.cursor()

        # Check if the person already exists
        c.execute("SELECT * FROM personalities WHERE name = ? AND mbti = ?", (data['name'], data['mbti']))
        existing_person = c.fetchone()
        if existing_person:
            return jsonify({'error': 'Person with this name and MBTI type already exists.'}), 409

        # Insert the new person if they are unique
        c.execute("INSERT INTO personalities (name, mbti) VALUES (?, ?)", (data['name'], data['mbti']))
        conn.commit()
        new_id = c.lastrowid

        # Add the IP to the store after successful request
        ip_store.add(client_ip)

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'id': new_id, 'name': data['name'], 'mbti': data['mbti']}), 201

@app.route('/api/reset', methods=['DELETE'])
def reset_database():
    try:
        conn = sqlite3.connect('personalities.db')
        c = conn.cursor()
        c.execute("DELETE FROM personalities")  # Clear all records
        ip_store = set()
        conn.commit()
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    # Clear the IP store as well after resetting the database
    ip_store.clear()

    return jsonify({'message': 'Database reset successful'}), 200

if __name__ == '__main__':
    app.run(debug=True)
