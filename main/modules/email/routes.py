from flask import Blueprint, request
import os
from .services import send_status_email


emails = Blueprint("emails", __name__, url_prefix="/emails")


def request_has_valid_api_key_header():
    """Check if the API key header is valid"""
    return os.environ.get("API_KEY") == request.headers.get("X-API-KEY")


@emails.route("/status", methods=["GET"])
def status():
    if not request_has_valid_api_key_header():
        return "Invalid token", 401

    try:
        send_status_email()
        return "done", 200
    except Exception as e:
        return str(e), 500
