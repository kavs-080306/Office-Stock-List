from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # Allow frontend connection

stocks = []  # {"name": "Pens", "quantity": 10, "category": "Stationery"}
history = []  # Transaction log

@app.route('/api/stocks', methods=['GET', 'POST'])
def handle_stocks():
    if request.method == 'GET':
        return jsonify({'stocks': stocks})
    
    data = request.json
    # Add or update stock
    for i, stock in enumerate(stocks):
        if stock['name'] == data['name']:
            stocks[i]['quantity'] += data['quantity']
            return jsonify({'message': 'Stock updated'})
    
    # New stock
    stocks.append({
        'name': data['name'],
        'quantity': data['quantity'],
        'category': data['category'],
        'updatedAt': pd.Timestamp.now().isoformat()
    })
    return jsonify({'message': 'Stock added'}), 201

@app.route('/api/stocks/remove', methods=['POST'])
def remove_stock():
    data = request.json
    global stocks, history
    
    for i, stock in enumerate(stocks):
        if stock['name'] == data['name'] and stock['quantity'] >= data['quantity']:
            stock['quantity'] -= data['quantity']
            history.append({
                'date_time': pd.Timestamp.now().isoformat(),
                'stock_name': data['name'],
                'quantity': data['quantity'],
                'person': data['person'],
                'action': 'REMOVE'
            })
            return jsonify({'message': 'Stock removed'})
    
    return jsonify({'error': 'Insufficient stock'}), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # ← NETWORK ACCESS!
