from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, quantity INTEGER, category TEXT, 
                  updatedAt TEXT)''')
    conn.commit()
    conn.close()
    print("✅ Products table ready")

def init_history_table():
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stock_history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  stock_name TEXT, 
                  quantity INTEGER, 
                  person TEXT,
                  action TEXT,
                  date_time TEXT)''')
    conn.commit()
    conn.close()
    print("✅ History table ready")

init_db()
init_history_table()

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY name")
    stocks = []
    for row in c.fetchall():
        stocks.append({
            'id': row[0], 
            'name': row[1], 
            'quantity': row[2], 
            'category': row[3], 
            'updatedAt': row[4] or datetime.datetime.now().isoformat()
        })
    conn.close()
    return jsonify(stocks)

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    c.execute("""
        SELECT stock_name, quantity, person, action, date_time 
        FROM stock_history 
        ORDER BY date_time DESC
    """)
    history = []
    for row in c.fetchall():
        history.append({
            'stock_name': row[0],
            'quantity': row[1],
            'person': row[2],
            'action': row[3],
            'date_time': row[4]
        })
    conn.close()
    return jsonify(history)

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    print("📥 ADD request received!")
    try:
        data = request.get_json()
        print(f"Data received: {data}")
        
        name = data['name'].strip()
        quantity = int(data['quantity'])
        category = data['category']
        
        conn = sqlite3.connect('stock.db')
        c = conn.cursor()
        
        # Check if exists, update or insert
        c.execute("SELECT id, quantity FROM products WHERE name=?", (name,))
        existing = c.fetchone()
        
        if existing:
            new_qty = existing[1] + quantity
            c.execute("UPDATE products SET quantity=?, category=?, updatedAt=? WHERE id=?", 
                     (new_qty, category, datetime.datetime.now().isoformat(), existing[0]))
            action = "UPDATE"
            action_msg = f"UPDATED {name}: {existing[1]} + {quantity} = {new_qty}"
        else:
            c.execute("INSERT INTO products (name, quantity, category, updatedAt) VALUES (?, ?, ?, ?)",
                     (name, quantity, category, datetime.datetime.now().isoformat()))
            action = "ADD"
            action_msg = f"ADDED NEW {name}: {quantity}"
        
        # ✅ CHANGED: "Silver Spring" instead of "Stock Manager"
        c.execute("INSERT INTO stock_history (stock_name, quantity, person, action, date_time) VALUES (?, ?, ?, ?, ?)",
                 (name, quantity, "Silver Spring", action, datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        print(f"✅ {action_msg}")
        return jsonify({'success': True, 'message': action_msg}), 200
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/stocks/<int:id>', methods=['PUT'])
def update_stock(id):
    try:
        data = request.get_json()
        conn = sqlite3.connect('stock.db')
        c = conn.cursor()
        c.execute("UPDATE products SET quantity=?, updatedAt=? WHERE id=?", 
                 (int(data['quantity']), datetime.datetime.now().isoformat(), id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except:
        return jsonify({'error': 'Update failed'}), 400

@app.route('/api/stocks/remove', methods=['POST'])
def remove_stock():
    print("➖ REMOVE request received!")
    try:
        data = request.get_json()
        print(f"Remove data: {data}")
        
        name = data['name'].strip()
        quantity_out = int(data['quantity'])
        person = data.get('person', 'Unknown')
        
        conn = sqlite3.connect('stock.db')
        c = conn.cursor()
        c.execute("SELECT id, quantity FROM products WHERE name=?", (name,))
        existing = c.fetchone()
        
        if not existing:
            conn.close()
            return jsonify({'error': 'Stock not found'}), 404
        
        current_qty = existing[1]
        if quantity_out > current_qty:
            conn.close()
            return jsonify({'error': f'Not enough stock! Only {current_qty} available'}), 400
        
        new_qty = current_qty - quantity_out
        c.execute("UPDATE products SET quantity=?, updatedAt=? WHERE id=?", 
                 (new_qty, datetime.datetime.now().isoformat(), existing[0]))
        
        # ✅ LOG TO HISTORY
        c.execute("INSERT INTO stock_history (stock_name, quantity, person, action, date_time) VALUES (?, ?, ?, ?, ?)",
                 (name, quantity_out, person, "REMOVE", datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ {person} took {quantity_out} from {name}: {current_qty} → {new_qty}")
        return jsonify({
            'success': True, 
            'message': f'{person} took {quantity_out} from {name}',
            'remaining': new_qty
        }), 200
        
    except Exception as e:
        print(f"❌ REMOVE ERROR: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
