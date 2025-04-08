from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

conn = sqlite3.connect('orders.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    items TEXT,
    total INTEGER,
    created_at TEXT
)''')
conn.commit()

@app.route('/submit-order', methods=['POST'])
def submit_order():
    data = request.json
    items = data.get('items')
    total = data.get('total')
    from datetime import datetime
    from zoneinfo import ZoneInfo  # Python 3.9+

    created_at = datetime.now(ZoneInfo("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO orders (items, total, created_at) VALUES (?, ?, ?)", (items, total, created_at))
    conn.commit()
    return jsonify({'message': '訂單已送出'})

@app.route('/admin')
def admin():
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = cursor.fetchall()
    return render_template('admin.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
