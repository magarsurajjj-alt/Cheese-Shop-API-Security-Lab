from flask import Flask, request, jsonify, render_template, make_response
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
import json
import time
import xml.etree.ElementTree as ET
import requests

app = Flask(__name__)
# SECURITY MISCONFIGURATION: Using a simple SQLite database and enabling DEBUG mode
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rollercoaster_tycoon.db'
app.config['DEBUG'] = True
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Initialize API with Swagger documentation available at /swagger
api = Api(app, version='1.0', title='Roller Coaster Tycoon API Demo',
          description='A demo API for a roller coaster tycoon game with intentional vulnerabilities for educational purposes',
          doc='/swagger')

# Database model for a user (vulnerable: storing passwords in plain text)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# New model for a coaster (gameplay element)
class Coaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    thrill_level = db.Column(db.Integer, default=5)
    # Owner of the coaster (for simplicity, each coaster is tied to a user)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_request
def before_request():
    db.create_all()

# Basic Authentication: Insecure verification using plain text passwords
@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return user

# API models for Swagger documentation
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='Unique identifier'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password in plain text')
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password in plain text')
})

coaster_model = api.model('Coaster', {
    'id': fields.Integer(readOnly=True, description='Unique coaster identifier'),
    'name': fields.String(required=True, description='Coaster name'),
    'thrill_level': fields.Integer(required=True, description='Thrill level of the coaster')
})

comment_model = api.model('Comment', {
    'content': fields.String(required=True, description='Comment content')
})

xml_model = api.model('XML', {
    'data': fields.String(required=True, description='XML data')
})

# 1. Registration Endpoint (Broken Authentication: plain text passwords)
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

# 2. Login Endpoint (Broken Authentication: returns a fake token)
@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username'], password=data['password']).first()
        if user:
            # Insecure: Returns a fake token in plain text
            return {'message': 'Login successful', 'token': 'fake-jwt-token'}, 200
        return {'message': 'Invalid credentials'}, 401

# 3. Build a new coaster (Gameplay element) - Requires Basic Authentication
@api.route('/build')
class BuildCoaster(Resource):
    @auth.login_required
    @api.expect(coaster_model)
    def post(self):
        data = request.get_json()
        new_coaster = Coaster(name=data['name'], thrill_level=data.get('thrill_level', 5), owner_id=auth.current_user().id)
        db.session.add(new_coaster)
        db.session.commit()
        return {'message': 'Coaster built successfully',
                'coaster': {'id': new_coaster.id, 'name': new_coaster.name, 'thrill_level': new_coaster.thrill_level}}, 201

# 4. List all coasters (Gameplay element) - Requires Basic Authentication
@api.route('/coasters')
class CoasterList(Resource):
    @auth.login_required
    def get(self):
        coasters = Coaster.query.all()
        coaster_list = [{'id': c.id, 'name': c.name, 'thrill_level': c.thrill_level} for c in coasters]
        return {'coasters': coaster_list}, 200

# 5. Ride a coaster (Simulated gameplay) - Vulnerable to SQL injection due to unsafe string concatenation
@api.route('/ride')
class RideCoaster(Resource):
    @auth.login_required
    def get(self):
        coaster_id = request.args.get('id')
        # WARNING: The following query is vulnerable to SQL injection attacks!
        query = "SELECT name, thrill_level FROM coaster WHERE id = " + coaster_id
        result = db.session.execute(query).fetchone()
        if result:
            return {'message': f'You enjoyed the {result[0]} with a thrill level of {result[1]}!'}, 200
        return {'message': 'Coaster not found'}, 404

# 6. Leave a comment about your park (Vulnerable to Cross-Site Scripting - XSS)
@api.route('/comment')
class CommentResource(Resource):
    @auth.login_required
    @api.expect(comment_model)
    def post(self):
        data = request.get_json()
        # XSS vulnerability: unsanitized user input is reflected in the response
        return {'message': f'Comment received: {data["content"]}'}

# 7. Fetch external reviews (Simulating SSRF vulnerability)
@api.route('/review')
class ReviewResource(Resource):
    @auth.login_required
    def get(self):
        url = request.args.get('url')
        try:
            response = requests.get(url)
            # Return only the first 200 characters to limit data exposure
            return {'fetched_review': response.text[:200]}
        except Exception as e:
            return {'error': str(e)}, 400

# 8. Deserialize game configuration (Insecure deserialization without validation)
@api.route('/deserialize')
class DeserializeResource(Resource):
    @auth.login_required
    def post(self):
        data = json.loads(request.data)
        return data

# 9. Schedule park events using XML (Vulnerable to XML External Entities - XXE)
@api.route('/schedule', methods=['POST'])
class ScheduleResource(Resource):
    @auth.login_required
    @api.expect(xml_model)
    def post(self):
        xml_data = request.get_json().get('data')
        try:
            root = ET.fromstring(xml_data)
            schedule = {child.tag: child.text for child in root}
            return {'schedule': schedule}
        except Exception as e:
            return {'error': str(e)}, 400

# 10. Admin endpoint for park management (Broken Access Control: no authentication required)
@api.route('/admin')
class AdminResource(Resource):
    def get(self):
        return {'message': 'Admin data: Confidential park management information'}

# 11. Warning about outdated components (Simulated vulnerability)
@api.route('/components')
class ComponentsResource(Resource):
    def get(self):
        return {'message': 'Warning: You are using an outdated component with known vulnerabilities'}

# 12. Attack simulation with insufficient logging & monitoring
@api.route('/attack')
class AttackResource(Resource):
    def get(self):
        time.sleep(1)
        return {'message': 'Attack simulated without proper logging'}

# Home route with an explanation of the game and vulnerabilities
@app.route('/home')
def home():
    explanation = """
    <html>
    <head><title>Roller Coaster Tycoon API Demo</title></head>
    <body>
      <h1>Welcome to the Roller Coaster Tycoon API Demo</h1>
      <p>This API simulates a basic roller coaster tycoon game. You can build coasters, ride them, and manage your park – all while demonstrating several common security vulnerabilities.</p>
      <h2>OWASP Top 10 Vulnerabilities Demonstrated:</h2>
      <ol>
        <li><strong>Broken Authentication:</strong> Registration and login endpoints use plain text credentials.</li>
        <li><strong>Sensitive Data Exposure:</strong> User passwords are stored and sometimes returned in plain text.</li>
        <li><strong>Broken Access Control:</strong> The <code>/admin</code> endpoint is accessible without authentication.</li>
        <li><strong>Injection (SQLi):</strong> The <code>/ride</code> endpoint concatenates user input into SQL queries.
            <br><em>Exploit hint:</em> Try passing <code>1 OR 1=1</code> as the <code>id</code> parameter.</li>
        <li><strong>Cross-Site Scripting (XSS):</strong> The <code>/comment</code> endpoint reflects unsanitized input.
            <br><em>Exploit hint:</em> Try sending a script tag (e.g. <code>&lt;script&gt;alert(1)&lt;/script&gt;</code>).</li>
        <li><strong>Insecure Deserialization:</strong> The <code>/deserialize</code> endpoint deserializes JSON without validation.</li>
        <li><strong>Server-Side Request Forgery (SSRF):</strong> The <code>/review</code> endpoint fetches external URLs.
            <br><em>Exploit hint:</em> Provide internal IP addresses or localhost URLs.</li>
        <li><strong>XML External Entities (XXE):</strong> The <code>/schedule</code> endpoint processes XML without disabling external entities.
            <br><em>Exploit hint:</em> Try including external entity definitions in your XML input.</li>
      </ol>
      <p><strong>Disclaimer:</strong> This API is for educational purposes only. Only test these vulnerabilities in a safe, legal, and controlled environment.</p>
    </body>
    </html>
    """
    return make_response(explanation, 200, {'Content-Type': 'text/html'})

# Extra route explaining fuzzing and demonstrating a simple wordlist including /swagger
@app.route('/fuzzing')
def fuzzing():
    fuzzing_explanation = """
    <html>
    <head><title>Fuzzing and Wordlist Example</title></head>
    <body>
      <h1>Fuzzing Explained</h1>
      <p>Fuzzing is an automated testing technique that provides random, unexpected, or invalid data as input to an application to find vulnerabilities.</p>
      <p>Example wordlist:</p>
      <ul>
        <li>/admin</li>
        <li>/login</li>
        <li>/register</li>
        <li>/swagger</li>
        <li>/coasters</li>
        <li>/build</li>
      </ul>
      <p><strong>Disclaimer:</strong> Always ensure you have explicit permission before fuzzing any application.</p>
    </body>
    </html>
    """
    return make_response(fuzzing_explanation, 200, {'Content-Type': 'text/html'})

if __name__ == '__main__':
    app.run(debug=True)
