import sqlite3
import jwt
import time
from flask import Flask, request, jsonify
from flasgger import Swagger

app = Flask(__name__)
# Swagger UI configuration
title = 'Cheese Shop Inventory API'
app.config['SWAGGER'] = {
    'title': title,
    'uiversion': 3
}
swagger = Swagger(app)

# Secret key for JWT
SECRET_KEY = 'supercheesesecret'


def init_db():
    """Initializes the SQLite database and creates tables."""
    conn = sqlite3.connect('cheese_shop.db')
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    # Cheeses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cheeses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Ensure the database is initialized
init_db()


def check_jwt():
    """
    Verify JWT token from Authorization header.
    Returns payload or error response.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, (jsonify({'error': 'Missing authorization header'}), 401)
    parts = auth_header.split()
    if parts[0] != 'Bearer' or len(parts) != 2:
        return None, (jsonify({'error': 'Invalid token format'}), 401)
    token = parts[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, (jsonify({'error': 'Token expired'}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({'error': 'Invalid token'}), 401)


@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    parameters:
      - in: body
        schema:
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: User registered successfully
      400:
        description: Registration failed
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    conn = sqlite3.connect('cheese_shop.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'User already exists'}), 400
    conn.close()
    return jsonify({'message': 'User registered successfully'})


@app.route('/login', methods=['POST'])
def login():
    """
    User login to receive JWT token.
    ---
    parameters:
      - in: body
        schema:
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Authentication successful
      401:
        description: Authentication failed
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    conn = sqlite3.connect('cheese_shop.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if not row or row[0] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    # Create token valid for one hour
    token = jwt.encode({'username': username, 'exp': time.time() + 3600}, SECRET_KEY, algorithm='HS256')
    return jsonify({'token': token})


@app.route('/cheeses', methods=['GET'])
def list_cheeses():
    """
    List all cheeses in inventory.
    ---
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
    responses:
      200:
        description: List of cheeses
    """
    payload, error = check_jwt()
    if error:
        return error
    conn = sqlite3.connect('cheese_shop.db')
    c = conn.cursor()
    c.execute('SELECT id, name, description, price, stock FROM cheeses')
    cheeses = [{'id': r[0], 'name': r[1], 'description': r[2], 'price': r[3], 'stock': r[4]} for r in c.fetchall()]
    conn.close()
    return jsonify({'cheeses': cheeses})


@app.route('/cheeses', methods=['POST'])
def add_cheese():
    """
    Add a new cheese to inventory.
    ---
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
      - in: body
        schema:
          required:
            - name
            - price
            - stock
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
    responses:
      200:
        description: Cheese added successfully
      400:
        description: Invalid input
    """
    payload, error = check_jwt()
    if error:
        return error
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description', '')
    price = data.get('price')
    stock = data.get('stock')
    if not name or price is None or stock is None:
        return jsonify({'error': 'Name, price, and stock are required'}), 400
    conn = sqlite3.connect('cheese_shop.db')
    c = conn.cursor()
    c.execute('INSERT INTO cheeses (name, description, price, stock) VALUES (?, ?, ?, ?)',
              (name, description, price, stock))
    conn.commit()
    cheese_id = c.lastrowid
    conn.close()
    return jsonify({'message': 'Cheese added', 'id': cheese_id})


@app.route('/cheeses/<int:cheese_id>', methods=['GET'])
def get_cheese(cheese_id):
    """
    Get details of a specific cheese.
    ---
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
      - name: cheese_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Cheese details
      404:
        description: Cheese not found
    """
    payload, error = check_jwt()
    if error:
        return error
    conn = sqlite3.connect('cheese_shop.db')
    c = conn.cursor()
    c.execute('SELECT id, name, description, price, stock FROM cheeses WHERE id = ?', (cheese_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Cheese not found'}), 404
    cheese = {'id': row[0], 'name': row[1], 'description': row[2], 'price': row[3], 'stock': row[4]}
    return jsonify(cheese)


@app.route('/cheeses/<int:cheese_id>', methods=['PUT'])
def update_cheese(cheese_id):
    """
    Update cheese information or stock.
    ---
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
      - name: cheese_id
        in: path
        required: true
        type: integer
      - in: body
        schema:
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            stock:
              type: integer
    responses:
      200:
        description: Cheese updated
      404:
        description: Cheese not found
    """
    payload, error = check_jwt()
    if error:
        return error
    data = request.get_json() or {}
    fields = []
    values = []
    for field in ['name', 'description', 'price', 'stock']:
        if field in data:
            fields.append(f"{field} = ?")
            values.append(data[field])
    if not fields:
        return jsonify({'error': 'No fields to update'}), 400
    values.append(cheese_id)
    query = f"UPDATE cheeses SET {', '.join(fields)} WHERE id = ?"
    conn = sqlite3.connect('cheese_shop.db')
    c = conn.cursor()
    c.execute(query, tuple(values))
    if c.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Cheese not found'}), 404
    conn.commit()
    conn.close()
    return jsonify({'message': 'Cheese updated'})


@app.route('/cheeses/<int:cheese_id>/sell', methods=['POST'])
def sell_cheese(cheese_id):
    """
    Sell a quantity of cheese (decrease stock).
    ---
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
      - name: cheese_id
        in: path
        required: true
        type: integer
      - in: body
        schema:
          required:
            - quantity
          properties:
            quantity:
              type: integer
    responses:
      200:
        description: Sale successful
      400:
        description: Insufficient stock
      404:
        description: Cheese not found
    """
    payload, error = check_jwt()
    if error:
        return error
    data = request.get_json() or {}
    qty = data.get('quantity')
    if qty is None or qty <= 0:
        return jsonify({'error': 'Positive quantity required'}), 400
    conn = sqlite3.connect('cheese_shop.db')
    c = conn.cursor()
    c.execute('SELECT stock FROM cheeses WHERE id = ?', (cheese_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Cheese not found'}), 404
    if row[0] < qty:
        conn.close()
        return jsonify({'error': 'Insufficient stock'}), 400
    c.execute('UPDATE cheeses SET stock = stock - ? WHERE id = ?', (qty, cheese_id))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Sold {qty} unit(s) of cheese'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5107)