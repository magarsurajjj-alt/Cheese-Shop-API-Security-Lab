import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_register():
    url = f"{BASE_URL}/register"
    data = {"username": "testuser", "password": "password"}
    response = requests.post(url, json=data)
    print("Register:", response.status_code, response.text)

def test_login():
    url = f"{BASE_URL}/login"
    data = {"username": "testuser", "password": "password"}
    response = requests.post(url, json=data)
    print("Login:", response.status_code, response.text)

def test_user():
    url = f"{BASE_URL}/user/1"
    response = requests.get(url)
    print("User:", response.status_code, response.text)

def test_data():
    url = f"{BASE_URL}/data"
    response = requests.get(url)
    print("Data:", response.status_code, response.text[:200], "...")
    
def test_admin():
    url = f"{BASE_URL}/admin"
    response = requests.get(url)
    print("Admin:", response.status_code, response.text)

def test_sqli():
    url = f"{BASE_URL}/sqli"
    # Attempting SQL injection by passing an injected query in the id parameter
    params = {"id": "1 OR 1=1"}
    response = requests.get(url, params=params)
    print("SQLi:", response.status_code, response.text)

def test_comment():
    url = f"{BASE_URL}/comment"
    data = {"content": "<script>alert('XSS')</script>"}
    response = requests.post(url, json=data)
    print("Comment:", response.status_code, response.text)

def test_deserialize():
    url = f"{BASE_URL}/deserialize"
    data = {"key": "value", "list": [1, 2, 3]}
    response = requests.post(url, json=data)
    print("Deserialize:", response.status_code, response.text)

def test_components():
    url = f"{BASE_URL}/components"
    response = requests.get(url)
    print("Components:", response.status_code, response.text)

def test_attack():
    url = f"{BASE_URL}/attack"
    response = requests.get(url)
    print("Attack:", response.status_code, response.text)

def test_ssrf():
    url = f"{BASE_URL}/ssrf"
    params = {"url": "http://example.com"}
    response = requests.get(url, params=params)
    print("SSRF:", response.status_code, response.text)

def test_xxe():
    url = f"{BASE_URL}/xxe"
    # A simple XML payload; for real XXE testing, you might include external entity definitions.
    xml_payload = """
    <root>
        <test>data</test>
    </root>
    """
    data = {"data": xml_payload}
    response = requests.post(url, json=data)
    print("XXE:", response.status_code, response.text)

def test_home():
    url = f"{BASE_URL}/home"
    response = requests.get(url)
    # Print only the first 200 characters for brevity
    print("Home:", response.status_code, response.text[:200], "...")

def test_fuzzing():
    url = f"{BASE_URL}/fuzzing"
    response = requests.get(url)
    print("Fuzzing:", response.status_code, response.text[:200], "...")

def test_swagger():
    url = f"{BASE_URL}/swagger"
    response = requests.get(url)
    print("Swagger:", response.status_code, response.text[:200], "...")

if __name__ == "__main__":
    print("Testing Insecure API Endpoints...\n")
    test_register()
    test_login()
    test_user()
    test_data()
    test_admin()
    test_sqli()
    test_comment()
    test_deserialize()
    test_components()
    test_attack()
    test_ssrf()
    test_xxe()
    test_home()
    test_fuzzing()
    test_swagger()