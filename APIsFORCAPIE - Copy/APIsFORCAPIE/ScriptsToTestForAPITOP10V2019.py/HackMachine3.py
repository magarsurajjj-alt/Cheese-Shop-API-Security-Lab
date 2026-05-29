import requests
from requests.auth import HTTPBasicAuth
import json

BASE_URL = "http://127.0.0.1:5000"

def test_register():
    url = f"{BASE_URL}/register"
    payload = {
        "username": "testuser",
        "password": "testpass"
    }
    response = requests.post(url, json=payload)
    print("Register:", response.status_code, response.json())

def test_login():
    url = f"{BASE_URL}/login"
    payload = {
        "username": "testuser",
        "password": "testpass"
    }
    response = requests.post(url, json=payload)
    print("Login:", response.status_code, response.json())

def test_build_coaster():
    url = f"{BASE_URL}/build"
    payload = {
        "name": "Thunderbolt",
        "thrill_level": 8
    }
    response = requests.post(url, json=payload, auth=HTTPBasicAuth("testuser", "testpass"))
    print("Build Coaster:", response.status_code, response.json())

def test_list_coasters():
    url = f"{BASE_URL}/coasters"
    response = requests.get(url, auth=HTTPBasicAuth("testuser", "testpass"))
    print("List Coasters:", response.status_code, response.json())
    return response.json()

def test_ride_coaster():
    # Get the list of coasters to retrieve an ID for riding.
    coasters = test_list_coasters()
    if "coasters" in coasters and coasters["coasters"]:
        coaster_id = coasters["coasters"][0]["id"]
        url = f"{BASE_URL}/ride?id={coaster_id}"
        response = requests.get(url, auth=HTTPBasicAuth("testuser", "testpass"))
        print("Ride Coaster:", response.status_code, response.json())
    else:
        print("No coasters available to ride.")

def test_comment():
    url = f"{BASE_URL}/comment"
    payload = {"content": "<script>alert('XSS');</script>"}
    response = requests.post(url, json=payload, auth=HTTPBasicAuth("testuser", "testpass"))
    print("Comment:", response.status_code, response.json())

def test_review():
    # SSRF: Fetch external data; using httpbin.org as an example
    url = f"{BASE_URL}/review?url=https://httpbin.org/get"
    response = requests.get(url, auth=HTTPBasicAuth("testuser", "testpass"))
    print("Review:", response.status_code, response.json())

def test_deserialize():
    url = f"{BASE_URL}/deserialize"
    payload = {"game": "Roller Coaster Tycoon", "version": "1.0"}
    response = requests.post(url, json=payload, auth=HTTPBasicAuth("testuser", "testpass"))
    print("Deserialize:", response.status_code, response.json())

def test_schedule():
    # XML payload for scheduling park events
    url = f"{BASE_URL}/schedule"
    xml_data = """
    <schedule>
        <event>Grand Opening</event>
        <time>10:00AM</time>
    </schedule>
    """
    payload = {"data": xml_data}
    response = requests.post(url, json=payload, auth=HTTPBasicAuth("testuser", "testpass"))
    print("Schedule:", response.status_code, response.json())

def test_admin():
    # Admin endpoint intentionally not protected by authentication.
    url = f"{BASE_URL}/admin"
    response = requests.get(url)
    print("Admin:", response.status_code, response.json())

def test_components():
    url = f"{BASE_URL}/components"
    response = requests.get(url)
    print("Components:", response.status_code, response.json())

def test_attack():
    url = f"{BASE_URL}/attack"
    response = requests.get(url)
    print("Attack:", response.status_code, response.json())

if __name__ == "__main__":
    print("=== Testing Registration ===")
    test_register()
    
    print("\n=== Testing Login ===")
    test_login()
    
    print("\n=== Testing Build Coaster ===")
    test_build_coaster()
    
    print("\n=== Testing List Coasters ===")
    test_list_coasters()
    
    print("\n=== Testing Ride Coaster ===")
    test_ride_coaster()
    
    print("\n=== Testing Leave Comment ===")
    test_comment()
    
    print("\n=== Testing External Review (SSRF) ===")
    test_review()
    
    print("\n=== Testing Deserialize ===")
    test_deserialize()
    
    print("\n=== Testing Schedule Event (XML) ===")
    test_schedule()
    
    print("\n=== Testing Admin Endpoint ===")
    test_admin()
    
    print("\n=== Testing Components Warning ===")
    test_components()
    
    print("\n=== Testing Attack Simulation ===")
    test_attack()
