from flask import request, g, jsonify, make_response
import json
import base64
import hmac
import hashlib
import time
from functools import wraps

SECRET_KEY = "your-very-secret-key"  # Used to sign the JWT


def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=')


def base64url_decode(data):
    padding = b'=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)


def create_jwt(user_id: str, admin: bool) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    # Token expires in 1 hour
    payload = {"id": user_id, "admin": admin, "exp": int(time.time()) + 3600}

    encoded_header = base64url_encode(json.dumps(header).encode('utf-8'))
    encoded_payload = base64url_encode(json.dumps(payload).encode('utf-8'))

    message = encoded_header + b"." + encoded_payload
    signature = hmac.new(SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)

    return (message + b"." + encoded_signature).decode('utf-8')


def verify_jwt(token: str):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        message = (parts[0] + '.' + parts[1]).encode('utf-8')
        signature = base64url_decode(parts[2].encode('utf-8'))

        expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), message, hashlib.sha256).digest()

        # Check if signature matches
        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload: dict = json.loads(base64url_decode(parts[1].encode('utf-8')))

        # Check if expired
        if payload.get('exp', 0) < time.time():
            return None

        return payload
    except Exception:
        return None


def token_required(admin_req=False):
    def decorat(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]

            if not token:
                return make_response(jsonify({"error": "Authentication Token is missing"}), 401)

            payload = verify_jwt(token)
            if not payload:
                return make_response(jsonify({"error": "Token is invalid or expired"}), 401)

            g.admin = payload["admin"]
            if admin_req and not g.admin:
                return make_response(jsonify({"error": "Admin rights required"}), 401)

            g.user_id = payload["id"]

            return f(*args, **kwargs)
        return wrapper
    return decorat
