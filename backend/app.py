from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_file
from flask_cors import CORS
import sqlite3
from datetime import datetime
import csv
import io
from pytz import timezone

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

# 登入帳號設定
USERNAME = '2plus2'
PASSWORD = '039771814'

# 資料庫連線
conn = sqlite3.connect('orders.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    items TEXT,
    total INTEGER,
    created_at TEXT
)''')
conn.commit()

# 登入頁面
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

# 訂單送出 API
@app.route('/submit-order', methods=['POST'])
def submit_order():
    data = request.json
    items = data.get('items')
    total = data.get('total')
    tz = timezone('Asia/Taipei')
    created_at = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO orders (items, total, created_at) VALUES (?, ?, ?)", (items, total, created_at))
    conn.commit()
    return jsonify({'message': '訂單已送出'})

# 後台管理畫面
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

# 刪除單筆訂單
@app.route('/delete/<int:order_id>')
def delete_order(order_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    return redirect(url_for('admin'))

# 匯出 CSV
@app.route('/export')
def export():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '品項', '總金額', '時間'])
    for order in orders:
        writer.writerow(order)

    output.seek(0)
    return send_file(io.BytesIO(output.read().encode()), mimetype='text/csv', as_attachment=True, download_name='orders.csv')

if __name__ == '__main__':
    app.run(debug=True)
