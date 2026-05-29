from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# In a real application, do not hard-code credentials or tokens.
# Store them securely, e.g. in environment variables or a secrets manager.
VALID_USERNAME = "student"
VALID_PASSWORD = "python123"
VALID_TOKEN = "mysecrettoken"


@app.route("/home")
def home():
    """
    This route returns an HTML page with instructions and sample Python code 
    that demonstrate how to authenticate against various endpoints.
    """
    # Embed the HTML directly as a string for simplicity.
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <title>API Authentication Examples</title>
</head>
<body>
    <h1>Welcome to the API Authentication Demo</h1>
    
    <p>This simple API demonstrates three forms of access:</p>
    <ol>
        <li><strong>Public access</strong> (no authentication)</li>
        <li><strong>Basic authentication</strong></li>
        <li><strong>Token-based authentication</strong></li>
    </ol>
    
    <hr/>
    
    <h2>1. Public Endpoint (No Authentication)</h2>
    <p>Endpoint: <code>/public</code></p>
    <p><strong>Example Python code to call:</strong></p>
    <pre><code>import requests

response = requests.get('http://localhost:5000/public')
if response.status_code == 200:
    print(response.json())  # Should return {'message': 'This endpoint does not require authentication.'}
</code></pre>
    
    <hr/>
    
    <h2>2. Basic Authentication</h2>
    <p>Endpoint: <code>/basic</code></p>
    <p><strong>Valid Credentials:</strong> student / python123</p>
    <p><strong>Example Python code to call:</strong></p>
    <pre><code>import requests

url = 'http://localhost:5000/basic'
# Provide the username and password
auth = ('student', 'python123')
response = requests.get(url, auth=auth)

if response.status_code == 200:
    print(response.json())  # Should show success message
else:
    print("Authentication failed:", response.status_code, response.text)
</code></pre>

    <hr/>

    <h2>3. Token-Based Authentication</h2>
    <p>Endpoint: <code>/token</code></p>
    <p><strong>Valid Token:</strong> mysecrettoken</p>
    <p><strong>Example Python code to call:</strong></p>
    <pre><code>import requests

url = 'http://localhost:5000/token'
headers = {
    'Authorization': 'Bearer mysecrettoken'
}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print(response.json())  # Should show success message
else:
    print("Authentication failed:", response.status_code, response.text)
</code></pre>
    
    <hr/>
    
    <p>
        Feel free to modify this demo to explore other authentication methods such as 
        OAuth, JWT, or session/cookie-based approaches.
    </p>
</body>
</html>
"""


@app.route("/public")
def public_endpoint():
    """
    This endpoint requires no authentication. Anyone can access it.
    """
    return jsonify({"message": "This endpoint does not require authentication."})


@app.route("/basic")
def basic_auth_endpoint():
    """
    This endpoint requires Basic Authentication. 
    Provide your credentials via the Authorization header as "Basic base64(username:password)".
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return Response("Missing Authorization header", status=401)
    
    # Basic auth header is typically: "Basic <base64-encoded username:password>"
    try:
        # Remove "Basic " from the beginning of the header
        encoded_creds = auth_header.split()[1]
        import base64
        decoded_bytes = base64.b64decode(encoded_creds)
        decoded_creds = decoded_bytes.decode("utf-8")
        username, password = decoded_creds.split(":")
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            return jsonify({"message": f"Welcome, {username}! You have successfully authenticated with Basic Auth."})
        else:
            return Response("Invalid username or password", status=401)
    except Exception:
        # If there's any issue parsing credentials, respond with an error
        return Response("Invalid Authorization header format", status=400)


@app.route("/token")
def token_auth_endpoint():
    """
    This endpoint requires a token via the 'Authorization' header as "Bearer <token>".
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return Response("Missing Authorization header", status=401)
    
    # Expected format: "Bearer <token>"
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
        if token == VALID_TOKEN:
            return jsonify({"message": "You have accessed a token-protected endpoint."})
        else:
            return Response("Invalid token", status=401)
    else:
        return Response("Invalid Authorization header format. Expected 'Bearer <token>'.", status=400)


if __name__ == "__main__":
    # Run the Flask application
    # Access the app via http://localhost:5000 in a web browser or HTTP client.
    app.run(debug=True)
