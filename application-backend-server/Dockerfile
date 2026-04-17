FROM python:3.11-alpine

WORKDIR /app

# Cài đặt các gói hệ thống cần thiết cho cryptography (python-jose) và mysql
RUN apk add --no-cache gcc musl-dev libffi-dev

# Cài đặt đầy đủ các thư viện Python
RUN pip install --no-cache-dir \
    flask \
    requests \
    python-jose[cryptography] \
    prometheus_client \
    mysql-connector-python

# Copy toàn bộ file code, dữ liệu và THƯ MỤC GIAO DIỆN vào container
COPY . .

EXPOSE 8081

CMD ["python", "app.py"]
