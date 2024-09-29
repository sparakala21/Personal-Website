from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

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
    conn = sqlite3.connect('personalities.db')
    c = conn.cursor()
    c.execute("INSERT INTO personalities (name, mbti) VALUES (?, ?)",
              (data['name'], data['mbti']))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'name': data['name'], 'mbti': data['mbti']}), 201

if __name__ == '__main__':
    app.run(debug=True)
