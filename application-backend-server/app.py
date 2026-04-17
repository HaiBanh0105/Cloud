from flask import Flask, jsonify, request, Response, render_template
import time, requests, os, json
import mysql.connector
from jose import jwt
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge, Counter

# --- Cấu hình OIDC/Keycloak ---
ISSUER   = os.getenv("OIDC_ISSUER", "http://authentication-identity-server:8080/auth/realms/master")
AUDIENCE = os.getenv("OIDC_AUDIENCE", "myapp")
JWKS_URL = f"{ISSUER}/protocol/openid-connect/certs"

# --- Cấu hình MariaDB ---
DB_CONFIG = {
    'host':     os.getenv("DB_HOST", "relational-database-server"),
    'user':     os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASS", "root"),
    'database': os.getenv("DB_NAME", "studentdb"),
    'connect_timeout': 5
}

_JWKS = None; _TS = 0
def get_jwks():
    global _JWKS, _TS
    now = time.time()
    if not _JWKS or now - _TS > 600:
        _JWKS = requests.get(JWKS_URL, timeout=5).json()
        _TS = now
    return _JWKS

app = Flask(__name__)

# --- Prometheus Metrics ---
REQUEST_COUNT = Counter('app_requests_total', 'Tong so request vao API', ['method', 'endpoint'])
UP_METRIC = Gauge('web_status', 'Trang thai hoat dong cua App Server (1 la UP)')
UP_METRIC.set(1) 

@app.before_request
def before_request():
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.get("/hello")
def hello(): 
    return jsonify(message="Hello from App Server!")

@app.get("/secure")
def secure():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "):
        return jsonify(error="Missing Bearer token"), 401
    
    parts = auth.split(" ", 1)
    if len(parts) < 2:
        return jsonify(error="Invalid token format"), 401
    token = parts[1]

    try:
        payload = jwt.decode(token, get_jwks(), algorithms=["RS256"], audience=AUDIENCE, issuer=ISSUER)
        return jsonify(message="Secure resource OK", preferred_username=payload.get("preferred_username"))
    except Exception as e:
        return jsonify(error=str(e)), 401

@app.get("/student")
def student_json_view():
    try:
        with open("students.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return render_template("student_json.html", students=data)
    except Exception as e:
        return f"Lỗi đọc file JSON: {str(e)}", 404

@app.get("/students-db")
def student_db_view():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students")
        data = cursor.fetchall()
        return render_template("student_db.html", students=data)
    except Exception as e:
        return f"Lỗi Database: {str(e)}", 500
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
