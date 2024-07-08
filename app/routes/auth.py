# app/routes/auth.py
from flask import Blueprint, request, jsonify
from app.models import User, Organisation
from app import db, bcrypt
from flask_jwt_extended import create_access_token
from app.utils import validate_registration, validate_login

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    errors = validate_registration(data)
    if errors:
        return jsonify({"errors": errors}), 422
    
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"errors": [{"field": "email", "message": "Email already exists"}]}), 422

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    try:
        new_user = User(
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email'],
            password=hashed_password,
            phone=data.get('phone')
        )

        org_name = f"{new_user.firstName}'s Organisation"
        new_org = Organisation(name=org_name)
        new_user.organisations.append(new_org)

        db.session.add(new_user)
        db.session.add(new_org)
        db.session.commit()

        access_token = create_access_token(identity=str(new_user.userId))

        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": access_token,
                "user": {
                    "userId": str(new_user.userId),
                    "firstName": new_user.firstName,
                    "lastName": new_user.lastName,
                    "email": new_user.email,
                    "phone": new_user.phone
                }
            }
        }), 201
    
    except:
        db.session.rollback()
        return jsonify({
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    errors = validate_login(data)
    if errors:
        return jsonify({"errors": errors}), 422

    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.userId))
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "data": {
                "accessToken": access_token,
                "user": {
                    "userId": str(user.userId),
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "email": user.email,
                    "phone": user.phone
                }
            }
        }), 200
    else:
        return jsonify({
            "status": "Bad request",
            "message": "Authentication failed",
            "statusCode": 401
        }), 401
