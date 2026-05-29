from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# -------------------------------------------------------------------
# Hardcoded credentials/tokens for DEMO ONLY! Do not do this in real apps.
# -------------------------------------------------------------------
VALID_USERNAME      = "student"
VALID_PASSWORD      = "python123"
VALID_API_KEY       = "myapikey"
OAUTH_CLIENT_ID     = "myclientid"
OAUTH_CLIENT_SECRET = "myclientsecret"
FAKE_OAUTH_TOKEN    = "fake_oauth_token"
# -------------------------------------------------------------------

@app.route("/home")
def home():
    """
    Serves an HTML page showing instructions and sample code for each 
    authentication method.
    """
    # HTML content for demonstration instructions
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <title>API Authentication Demo</title>
</head>
<body>
    <h1>API Authentication Demo</h1>
    <p>This application demonstrates the following authentication methods:</p>
    <ol>
        <li>No Authentication</li>
        <li>Basic Authentication</li>
        <li>API Key Authentication</li>
        <li>OAuth-like Flow (simplified example)</li>
    </ol>
    <hr/>
    
    <h2>1. No Authentication</h2>
    <p><strong>Endpoint:</strong> <code>/public</code></p>
    <p>No credentials required.</p>
    <pre><code>import requests

response = requests.get("http://localhost:5000/public")
print("Status:", response.status_code)
print("Body:", response.json())
</code></pre>
    
    <hr/>
    
    <h2>2. Basic Authentication</h2>
    <p><strong>Endpoint:</strong> <code>/basic</code></p>
    <p><strong>Valid Credentials:</strong> student / python123</p>
    <pre><code>import requests

url = "http://localhost:5000/basic"
auth = ("student", "python123")  # Basic Auth
response = requests.get(url, auth=auth)

print("Status:", response.status_code)
print("Body:", response.text)
</code></pre>

    <hr/>

    <h2>3. API Key Authentication</h2>
    <p><strong>Endpoint:</strong> <code>/api-key</code></p>
    <p><strong>Valid API Key:</strong> myapikey</p>
    <p>This demo expects the key in the <code>X-API-KEY</code> header.</p>
    <pre><code>import requests

url = "http://localhost:5000/api-key"
headers = {
    "X-API-KEY": "myapikey"
}
response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print("Body:", response.text)
</code></pre>

    <hr/>

    <h2>4. OAuth-like Flow</h2>
    <p>This demo simulates a very simplified OAuth-like flow. In a real scenario, you'd implement or integrate with a full OAuth provider.</p>
    
    <ol>
        <li><strong>Obtain Token</strong> from <code>/oauth/token</code> using <code>client_id</code> and <code>client_secret</code>.</li>
        <li><strong>Use Token</strong> to access <code>/oauth/protected</code> with <code>Authorization: Bearer &lt;token&gt;</code>.</li>
    </ol>

    <h3>4a. Obtain Token from /oauth/token</h3>
    <p><strong>Valid client_id/client_secret:</strong> myclientid / myclientsecret</p>
    <pre><code>import requests

url = "http://localhost:5000/oauth/token"
data = {
    "client_id": "myclientid",
    "client_secret": "myclientsecret"
}
response = requests.post(url, data=data)

if response.status_code == 200:
    token_info = response.json()
    print("Access Token:", token_info["access_token"])
</code></pre>

    <h3>4b. Call Protected Endpoint /oauth/protected</h3>
    <p>Use the token obtained from <code>/oauth/token</code>.</p>
    <pre><code>import requests

token = "fake_oauth_token"  # from the previous step
headers = {
    "Authorization": f"Bearer {token}"
}
url = "http://localhost:5000/oauth/protected"
response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print("Body:", response.text)
</code></pre>

    <hr/>

    <p><em>Note:</em> This is a very simplified demo! In real-world OAuth scenarios, 
    you would have a full authorize flow, redirect URIs, state, scopes, etc.</p>
</body>
</html>
"""

@app.route("/public")
def public_endpoint():
    """
    Public endpoint (no authentication).
    """
    return jsonify({"message": "Public endpoint: no authentication required."})

@app.route("/basic")
def basic_auth_endpoint():
    """
    Basic authentication endpoint.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return Response("Missing Authorization header", status=401)
    
    # Typically: "Basic <base64-encoded username:password>"
    try:
        # Remove 'Basic ' from the beginning
        import base64
        encoded_creds = auth_header.split()[1]
        decoded_bytes = base64.b64decode(encoded_creds)
        decoded_creds = decoded_bytes.decode("utf-8")
        username, password = decoded_creds.split(":")
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            return jsonify({"message": f"Welcome, {username}! Basic Auth successful."})
        else:
            return Response("Invalid username or password", status=401)
    except Exception:
        return Response("Invalid Authorization header format", status=400)

@app.route("/api-key")
def api_key_endpoint():
    """
    API Key endpoint.
    Expects an 'X-API-KEY' header with the correct key.
    """
    api_key = request.headers.get("X-API-KEY")
    if not api_key:
        return Response("Missing X-API-KEY header", status=401)
    
    if api_key == VALID_API_KEY:
        return jsonify({"message": "API Key authentication succeeded."})
    else:
        return Response("Invalid API Key", status=401)

@app.route("/oauth/token", methods=["POST"])
def oauth_token():
    """
    Simulated OAuth token endpoint.
    Expects client_id and client_secret as form data.
    If valid, returns a JSON with 'access_token'.
    """
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    
    if client_id == OAUTH_CLIENT_ID and client_secret == OAUTH_CLIENT_SECRET:
        # Return a fake token (in real OAuth, you'd generate a JWT or random token)
        return jsonify({
            "access_token": FAKE_OAUTH_TOKEN,
            "token_type": "bearer"
        })
    else:
        return Response("Invalid client credentials", status=401)

@app.route("/oauth/protected")
def oauth_protected():
    """
    Simulated OAuth protected endpoint.
    Expects 'Authorization: Bearer <token>'.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return Response("Missing Authorization header", status=401)

    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
        if token == FAKE_OAUTH_TOKEN:
            return jsonify({"message": "OAuth-protected resource accessed!"})
        else:
            return Response("Invalid or expired token", status=401)
    else:
        return Response("Invalid Authorization header format. Expected 'Bearer <token>'.", status=400)

if __name__ == "__main__":
    app.run(debug=True)
