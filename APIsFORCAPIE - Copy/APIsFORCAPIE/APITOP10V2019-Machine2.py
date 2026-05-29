from flask import Flask, request, jsonify, render_template, make_response
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
import json
import time
import xml.etree.ElementTree as ET
import requests

app = Flask(__name__)
# SECURITY MISCONFIGURATION: Using a simple SQLite database and enabling DEBUG mode
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insecure_api.db'
app.config['DEBUG'] = True
db = SQLAlchemy(app)

# Initialize API with Swagger documentation available at /swagger
api = Api(app, version='1.0', title='Insecure API Demo',
          description='A demo API containing intentional vulnerabilities for educational purposes',
          doc='/swagger')

# Database model for a user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # SENSITIVE DATA EXPOSURE: Storing passwords in plain text
    password = db.Column(db.String(120), nullable=False)

@app.before_request
def before_request():
    db.create_all()

# Define API models for Swagger documentation
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='Unique identifier'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password in plain text')
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password in plain text')
})

comment_model = api.model('Comment', {
    'content': fields.String(required=True, description='Comment content')
})

xml_model = api.model('XML', {
    'data': fields.String(required=True, description='XML data')
})

# 1. Broken Authentication: User registration with plain text password storage
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

# 2. Broken Authentication: Insecure login without proper token management
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

# 3. Sensitive Data Exposure: Exposing user data including passwords
@api.route('/user/<int:id>')
class UserResource(Resource):
    def get(self, id):
        user = User.query.get_or_404(id)
        return {'id': user.id, 'username': user.username, 'password': user.password}

# 4. Excessive Data Exposure: Endpoint that returns a large dataset without rate limiting
@api.route('/data')
class DataResource(Resource):
    def get(self):
        data = ["item" + str(i) for i in range(1000)]
        return {'data': data}

# 5. Broken Access Control: Admin endpoint accessible without any authentication
@api.route('/admin')
class AdminResource(Resource):
    def get(self):
        return {'message': 'Admin data: Confidential admin information'}

# 6. Injection: SQL Injection vulnerability via unsafe string concatenation
@api.route('/sqli')
class SQLiResource(Resource):
    def get(self):
        user_id = request.args.get('id')
        # WARNING: The following query is vulnerable to SQL injection attacks!
        query = "SELECT username FROM user WHERE id = " + user_id
        result = db.engine.execute(query).fetchone()
        if result:
            return {'username': result[0]}
        return {'message': 'User not found'}

# 7. Cross-Site Scripting (XSS): Reflecting unsanitized user input
@api.route('/comment')
class CommentResource(Resource):
    @api.expect(comment_model)
    def post(self):
        data = request.get_json()
        return {'message': f'Comment received: {data["content"]}'}

# 8. Insecure Deserialization: Directly deserializing JSON without validation
@api.route('/deserialize')
class DeserializeResource(Resource):
    def post(self):
        data = json.loads(request.data)
        return data

# 9. Using Components with Known Vulnerabilities: Simulated warning message
@api.route('/components')
class ComponentsResource(Resource):
    def get(self):
        return {'message': 'Warning: You are using an outdated component with known vulnerabilities'}

# 10. Insufficient Logging & Monitoring: Attack simulation without proper logging
@api.route('/attack')
class AttackResource(Resource):
    def get(self):
        time.sleep(1)
        return {'message': 'Attack simulated without proper logging'}

# 11. Server-Side Request Forgery (SSRF): Fetching external URLs based on user input
@api.route('/ssrf')
class SSRFResource(Resource):
    def get(self):
        url = request.args.get('url')
        try:
            response = requests.get(url)
            # Return only the first 200 characters to limit data exposure
            return {'fetched_data': response.text[:200]}
        except Exception as e:
            return {'error': str(e)}, 400

# 12. XML External Entities (XXE): Vulnerable XML parsing without proper security measures
@api.route('/xxe', methods=['POST'])
class XXEResource(Resource):
    @api.expect(xml_model)
    def post(self):
        xml_data = request.get_json().get('data')
        try:
            root = ET.fromstring(xml_data)
            result = {child.tag: child.text for child in root}
            return {'parsed_data': result}
        except Exception as e:
            return {'error': str(e)}, 400

# Home route with an explanation of vulnerabilities and exploitation hints for students
@app.route('/home')
def home():
    explanation = """
    <html>
    <head><title>Insecure API Exploitation Guide</title></head>
    <body>
      <h1>Welcome to the Insecure API Demo</h1>
      <p>This API is intentionally designed with multiple security vulnerabilities for educational purposes.</p>
      <h2>OWASP Top 10 Vulnerabilities Demonstrated:</h2>
      <ol>
      <li><a href=/fuzzing>fuzzing</a></li>
        <li><strong>Injection (SQLi):</strong> The <code>/sqli</code> endpoint concatenates user input into SQL queries.
            <br><em>Exploit hint:</em> Try passing <code>1 OR 1=1</code> as the <code>id</code> parameter.</li>
        <li><strong>Broken Authentication:</strong> The <code>/register</code> and <code>/login</code> endpoints use plain text credentials.</li>
        <li><strong>Sensitive Data Exposure:</strong> The <code>/user/&lt;id&gt;</code> endpoint returns sensitive information including passwords.</li>
        <li><strong>Broken Access Control:</strong> The <code>/admin</code> endpoint is accessible without any authentication checks.</li>
        <li><strong>Security Misconfiguration:</strong> Debug mode is enabled and outdated components are used.</li>
        <li><strong>Cross-Site Scripting (XSS):</strong> The <code>/comment</code> endpoint reflects unsanitized input.
            <br><em>Exploit hint:</em> Try sending a script tag (e.g. <code>&lt;script&gt;alert(1)&lt;/script&gt;</code>).</li>
        <li><strong>Insecure Deserialization:</strong> The <code>/deserialize</code> endpoint deserializes JSON without validation.</li>
        <li><strong>Using Components with Known Vulnerabilities:</strong> The <code>/components</code> endpoint warns about outdated libraries.</li>
        <li><strong>Insufficient Logging & Monitoring:</strong> The <code>/attack</code> endpoint simulates an attack without logging.</li>
        <li><strong>Server-Side Request Forgery (SSRF):</strong> The <code>/ssrf</code> endpoint fetches external URLs provided by the user.
            <br><em>Exploit hint:</em> Provide internal IP addresses or localhost URLs.</li>
        <li><strong>XML External Entities (XXE):</strong> The <code>/xxe</code> endpoint processes XML without disabling external entities.
            <br><em>Exploit hint:</em> Try including external entity definitions in your XML input.</li>
      </ol>
      <p><strong>Disclaimer:</strong> This API is for educational purposes only. Only test these vulnerabilities in a safe, legal, and controlled environment.</p>
      <p>Recommended tools for testing include curl, SQLMap, and Burp Suite.</p>
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
      <p>Fuzzing is an automated testing technique that provides random, unexpected, or invalid data as input to an application in order to find vulnerabilities, such as input validation errors, crashes, or hidden endpoints.</p>
      <p>In web applications, fuzzers can be used to discover endpoints by trying a list of common paths. For example, consider the following wordlist:</p>
      <ul>
        <li>/admin</li>
        <li>/login</li>
        <li>/register</li>
        <li>/swagger</li>
        <li>/data</li>
        <li>/user</li>
      </ul>
      <p>A fuzzer would use these entries to probe the application. If the fuzzer finds that the <code>/swagger</code> endpoint exists, it can confirm that the Swagger documentation is available.</p>
      <p><strong>Disclaimer:</strong> Always ensure you have explicit permission before fuzzing any application.</p>
    </body>
    </html>
    """
    return make_response(fuzzing_explanation, 200, {'Content-Type': 'text/html'})

if __name__ == '__main__':
    app.run(debug=True)
