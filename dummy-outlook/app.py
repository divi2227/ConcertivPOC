"""Dummy Outlook Service — Simulates a Concertiv Outlook mailbox for POC demo."""

import secrets
from functools import wraps
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from mock_data import VENDORS, CLIENTS, VALID_PAIRS, THREAD_DATA, INBOX_EMAILS

app = Flask(__name__)
CORS(app)

# ── API Key Authentication ───────────────────────────────────────────────────
# Generate a unique API key on each startup (simulates a real API service).
# In production, this would be Microsoft Graph's OAuth token / client secret.

API_KEY = f"outlook-{secrets.token_hex(16)}"


def require_api_key(f):
    """Decorator that enforces Bearer token auth on API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing Authorization header. Use: Bearer <api-key>"}), 401
        token = auth_header[7:]  # strip "Bearer "
        if token != API_KEY:
            return jsonify({"error": "Invalid API key. Access denied."}), 401
        return f(*args, **kwargs)
    return decorated


# ── Web UI (no auth required — this is the "Outlook app" itself) ─────────────

@app.route("/")
def inbox():
    """Render Outlook-style inbox page."""
    return render_template("inbox.html", emails=INBOX_EMAILS)


# ── API Endpoints (require API key authentication) ───────────────────────────

@app.route("/api/vendors", methods=["GET"])
@require_api_key
def get_vendors():
    return jsonify({"vendors": VENDORS})


@app.route("/api/clients", methods=["GET"])
@require_api_key
def get_clients():
    return jsonify({"clients": CLIENTS})


@app.route("/api/fetch", methods=["POST"])
@require_api_key
def fetch_thread():
    data = request.get_json()
    vendor = data.get("vendor", "")
    client = data.get("client", "")

    conversation_id = VALID_PAIRS.get((vendor, client))
    if not conversation_id:
        return jsonify({
            "error": f"No negotiation thread found between {vendor} and {client}. Please verify your selection."
        }), 404

    thread = THREAD_DATA.get(conversation_id)
    if not thread:
        return jsonify({"error": "Thread data not found."}), 404

    return jsonify(thread)


if __name__ == "__main__":
    print("=" * 60)
    print("  Dummy Outlook Service — POC Demo Environment")
    print("  Web UI:  http://localhost:8001")
    print("  API:     http://localhost:8001/api/")
    print(f"  API Key: {API_KEY}")
    print("=" * 60)
    print()
    print("  Add this to your Concertiv .env file:")
    print(f"  OUTLOOK_API_KEY={API_KEY}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=8001, debug=False)
