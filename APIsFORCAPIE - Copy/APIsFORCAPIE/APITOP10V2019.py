from flask import Flask, request, jsonify, render_template
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
import json
import time

# Initialize Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vulnerable_api.db'
db = SQLAlchemy(app)

# Initialize API and change default Swagger route
api = Api(app, version='1.0', title='CAPIE Practice Machine OWASP 2019', description='CAPIE - Certified API Hacking Expert', doc='/swagger')

# Define data models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Initialize the database
@app.before_request
def before_request():
    db.create_all()

# Define API models
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a user'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

# Endpoint for user registration (Broken Authentication)
@api.route('/register')
class Register(Resource):
    @api.expect(user_model)
    def post(self):
        data = request.get_json()
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'User already exists'}, 400
        new_user = User(username=data['username'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully'}, 201

# Endpoint demonstrating Excessive Data Exposure
@api.route('/user/<int:id>')
class UserResource(Resource):
    def get(self, id):
        user = User.query.get_or_404(id)
        # Exposing sensitive information like password without consideration
        return {'id': user.id, 'username': user.username, 'password': user.password}

# Endpoint demonstrating Lack of Resources & Rate Limiting
@api.route('/data')
class DataResource(Resource):
    def get(self):
        # Returning large data without rate limiting
        data = ["item" + str(i) for i in range(1000)]
        return {'data': data}

# Endpoint demonstrating Broken Function Level Authorization
@api.route('/admin')
class AdminResource(Resource):
    def get(self):
        # No authorization checks; any user can access admin data
        return {'message': 'Admin data accessed'}

# Endpoint for SQL Injection (SQLi)
@api.route('/user/<int:id>/sqli')
class SQLiResource(Resource):
    def get(self, id):
        # Allowing SQLi in user retrieval
        user = User.query.filter_by(id=id).first()
        return {'user': user.username if user else 'Not found'}

# Endpoint demonstrating Cross-Site Scripting (XSS)
@api.route('/comment')
class CommentResource(Resource):
    @api.expect(api.model('Comment', {
        'content': fields.String(required=True, description='Content of the comment')
    }))
    def post(self):
        # Accepting unsafe content and reflecting it back without sanitization (XSS)
        data = request.get_json()
        return {'content': f'Comment received: {data["content"]}'}

# Endpoint demonstrating Insecure Deserialization
@api.route('/deserialize')
class DeserializeResource(Resource):
    def post(self):
        # Allowing insecure deserialization without proper validation
        data = request.get_json()
        return jsonify(data)

# Endpoint demonstrating Using Components with Known Vulnerabilities
@api.route('/components')
class ComponentsResource(Resource):
    def get(self):
        # Simulating a vulnerable third-party component without updating
        return {'message': 'You are using an outdated, vulnerable component'}

# Endpoint demonstrating Insufficient Logging & Monitoring
@api.route('/perform_attack')
class AttackResource(Resource):
    def get(self):
        # Simulating an attack that the system doesn't log
        time.sleep(2)
        return {'message': 'Attack performed, no logs generated'}

# Endpoint demonstrating Server-Side Request Forgery (SSRF)
@api.route('/fetch_url')
class SSRFResource(Resource):
    def get(self):
        url = request.args.get('url')
        # Simulating SSRF by allowing user input to fetch internal services
        return jsonify({"message": f"Attempted to fetch: {url}"})

# Serve the instructional HTML page on the /home route
@app.route('/home')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
