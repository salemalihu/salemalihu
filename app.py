
from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('accounting.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    chicken_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    amount_paid REAL NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.json
    conn = sqlite3.connect('accounting.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (data['name'], data['phone']))
        conn.commit()
        response = {'status': 'success', 'message': 'تم إضافة العميل بنجاح'}
    except sqlite3.IntegrityError:
        response = {'status': 'error', 'message': 'اسم العميل موجود بالفعل'}
    conn.close()
    return jsonify(response)

@app.route('/get_customers', methods=['GET'])
def get_customers():
    conn = sqlite3.connect('accounting.db')
    c = conn.cursor()
    c.execute("SELECT id, name, phone FROM customers")
    customers = [{'id': row[0], 'name': row[1], 'phone': row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(customers)

@app.route('/add_sale', methods=['POST'])
def add_sale():
    data = request.json
    conn = sqlite3.connect('accounting.db')
    c = conn.cursor()
    c.execute('''INSERT INTO sales (customer_id, date, chicken_type, quantity, price, amount_paid)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (data['customer_id'], data['date'], data['chicken_type'], data['quantity'], data['price'], data['amount_paid']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'تمت إضافة عملية البيع بنجاح'})

@app.route('/get_sales/<int:customer_id>', methods=['GET'])
def get_sales(customer_id):
    conn = sqlite3.connect('accounting.db')
    c = conn.cursor()
    c.execute('''SELECT date, chicken_type, quantity, price, amount_paid 
                 FROM sales WHERE customer_id = ?''', (customer_id,))
    sales = [{'date': row[0], 'chicken_type': row[1], 'quantity': row[2], 'price': row[3], 'amount_paid': row[4]} for row in c.fetchall()]
    conn.close()
    return jsonify(sales)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
