from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_cors import CORS
import sqlite3
from datetime import datetime
import csv
import io
from pytz import timezone
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

USERNAME = '2plus2'
PASSWORD = '039771814'

# 資料庫連線與初始化
conn = sqlite3.connect('orders.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    items TEXT,
    total INTEGER,
    created_at TEXT,
    status TEXT DEFAULT '未結帳'
)''')

# 安全地新增欄位：桌號與備註（如尚未存在）
try:
    cursor.execute("ALTER TABLE orders ADD COLUMN table_number TEXT;")
except:
    pass

try:
    cursor.execute("ALTER TABLE orders ADD COLUMN note TEXT;")
except:
    pass

conn.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='帳號或密碼錯誤')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/submit-order', methods=['POST'])
def submit_order():
    data = request.json
    items = data.get('items')
    total = data.get('total')
    table = data.get('table')
    note = data.get('note')
    tz = timezone('Asia/Taipei')
    created_at = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO orders (items, total, created_at, status, table_number, note) VALUES (?, ?, ?, ?, ?, ?)", (items, total, created_at, '未結帳', table, note))
    conn.commit()
    return jsonify({'message': '訂單已送出'})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    keyword = request.form.get('keyword', '') if request.method == 'POST' else ''
    if keyword:
        cursor.execute("SELECT * FROM orders WHERE items LIKE ? ORDER BY created_at DESC", (f'%{keyword}%',))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = cursor.fetchall()
    return render_template('admin.html', orders=orders, keyword=keyword)

@app.route('/checkout/<int:order_id>')
def checkout_order(order_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cursor.execute("UPDATE orders SET status='已結帳' WHERE id=?", (order_id,))
    conn.commit()
    return redirect(url_for('admin'))

@app.route('/delete/<int:order_id>')
def delete_order(order_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    return redirect(url_for('admin'))

@app.route('/export')
def export():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '品項', '總金額', '時間', '狀態', '桌號', '備註'])
    for order in orders:
        writer.writerow(order)

    output.seek(0)
    return send_file(io.BytesIO(output.read().encode()), mimetype='text/csv', as_attachment=True, download_name='orders.csv')

if __name__ == '__main__':
    app.run(debug=True)
