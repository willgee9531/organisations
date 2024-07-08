from flask import jsonify
from werkzeug.exceptions import HTTPException
import re

def validate_registration(data):
    errors = []
    required_fields = ['firstName', 'lastName', 'email', 'password', 'phone']
    for field in required_fields:
        if not data.get(field):
            errors.append({"field": field, "message": f"{field} is required"})
    
    if data.get('email') and not is_valid_email(data['email']):
        errors.append({"field": "email", "message": "Invalid email format"})
    
    return errors

def validate_login(data):
    errors = []
    required_fields = ['email', 'password']
    for field in required_fields:
        if not data.get(field):
            errors.append({"field": field, "message": f"{field} is required"})
    return errors

def is_valid_email(email):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return email_regex.match(email)

def handle_error(e):
    if isinstance(e, HTTPException):
        return jsonify({
            "status": "error",
            "message": e.description,
            "statusCode": e.code
        }), e.code
    
    return jsonify({
        "status": "error",
        "message": "An unexpected error occurred",
        "statusCode": 500
    }), 500

def validate_uuid(uuid_string):
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    return uuid_pattern.match(uuid_string)