# 🧀 Cheese Shop API – Security Testing Lab

A Flask-based REST API designed for **learning API security testing and OWASP Top 10 vulnerabilities**.

This project simulates a real-world inventory management system with intentional security flaws for educational and penetration testing practice.

---

# 🎯 Purpose of This Project

This project was built to practice:

- API security testing
- JWT authentication analysis
- Input validation testing
- Broken access control detection
- Real-world penetration testing workflow

---

# ⚙️ Tech Stack

- Python
- Flask
- SQLite
- JWT (PyJWT)
- Flasgger (Swagger UI)
- Postman (for testing)

---

# 🚀 How to Run

## 1. Install dependencies
```bash
pip install -r requirements.txt
2. Run the server
python app.py
3. Open in browser
http://127.0.0.1:5107/apidocs
```

# 🔐Features
```
User Registration & Login
JWT Authentication
Cheese Inventory Management
Add / Update / Sell Cheese
Swagger API Documentation
```
# ⚠️Security Disclaimer
```
⚠️ This application is intentionally vulnerable.

It is designed ONLY for:

Educational purposes
Cybersecurity learning
Penetration testing practice
```

# 🧪Identified Vulnerabilities
```
🔴 Critical Issues
Plaintext password storage
Hardcoded JWT secret key
No role-based access control (RBAC)
🟠 High Risk Issues
No input validation (negative price/stock allowed)
No data type validation
No rate limiting (brute force possible)
Weak authentication design
🟡 Medium Issues
Stored XSS risk (unsanitized input)
Verbose error messages
No logging or monitoring system
```

# 🧪Example API Endpoints
```
Register User
POST /register
Login
POST /login
Add Cheese
POST /cheeses
Authorization: Bearer <token>
Get Cheese List
GET /cheeses
Update Cheese
PUT /cheeses/<id>
Sell Cheese
POST /cheeses/<id>/sell
```
# 🧪Testing Tools Used
```
Postman
Swagger UI
Manual API testing
JWT decoder (jwt.io)
```
# 📸Screenshots




# 📊Learning Outcome
```
This project demonstrates:

How insecure APIs behave
How attackers exploit input validation flaws
JWT authentication weaknesses
Real-world API penetration testing workflow
```
