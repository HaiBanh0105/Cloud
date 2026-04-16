from flask import Flask, jsonify, request, Response
import time, requests, os, json
from jose import jwt
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge, Counter

# Cấu hình các biến môi trường cho OIDC/Keycloak 
ISSUER   = os.getenv("OIDC_ISSUER",   "http://authentication-identity-server:8080/realms/master")
AUDIENCE = os.getenv("OIDC_AUDIENCE", "myapp")
JWKS_URL = f"{ISSUER}/protocol/openid-connect/certs"

_JWKS = None; _TS = 0
def get_jwks():
    global _JWKS, _TS
    now = time.time()
    if not _JWKS or now - _TS > 600:
        _JWKS = requests.get(JWKS_URL, timeout=5).json()
        _TS = now
    return _JWKS

app = Flask(__name__)

# Khởi tạo Prometheus Metrics 
# Counter: Đếm số lượng request vào API
REQUEST_COUNT = Counter('app_requests_total', 'Tong so request vao API', ['method', 'endpoint'])
# Gauge: Giám sát trạng thái hoạt động (1 là UP)
UP_METRIC = Gauge('web_status', 'Trang thai hoat dong cua App Server (1 la UP)')
UP_METRIC.set(1) 

@app.before_request
def before_request():
    # Tăng số đếm request tự động mỗi khi có truy cập [cite: 504]
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()

# Endpoint /metrics cho Prometheus Scrape 
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.get("/hello")
def hello(): 
    return jsonify(message="Hello from App Server!")

# Endpoint bảo mật yêu cầu Token từ Keycloak
@app.get("/secure")
def secure():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "):
        return jsonify(error="Missing Bearer token"), 401
    token = auth.split(" ",1)[1]
    try:
        payload = jwt.decode(token, get_jwks(), algorithms=["RS256"], audience=AUDIENCE, issuer=ISSUER)
        return jsonify(message="Secure resource OK", preferred_username=payload.get("preferred_username"))
    except Exception as e:
        return jsonify(error=str(e)), 401

# hần mở rộng: API đọc danh sách sinh viên từ file JSON
@app.get("/student")
def student():
    try:
        with open("students.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify(error="File students.json khong ton tai"), 404

if __name__ == "__main__":
    # Chạy trên cổng 8081 nội bộ của container 
    app.run(host="0.0.0.0", port=8081)