# app/routes/organisation.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Organisation
from app import db, bcrypt
import uuid

organisation_bp = Blueprint('organisation', __name__, url_prefix='/api')


@organisation_bp.route('/users/<userId>', methods=['GET'])
@jwt_required()
def get_user(userId):
    user_uuid = uuid.UUID(userId)
    user = User.query.filter_by(userId=user_uuid).first_or_404()
    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400
    
    return jsonify({
        "status": "success",
        "message": "User retrieved successfully",
        "data": {
            "userId": str(user.userId),
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
            "phone": user.phone
        }
    }), 200


@organisation_bp.route('/organisations', methods=['GET'])
@jwt_required()
def get_organisations():
    userId = get_jwt_identity()
    user = User.query.filter_by(userId=userId).first()

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400

    organisation = user.organisations
    return jsonify({
        'status': 'success',
        'message': 'Organisations retrieved successfully',
        'data': {
            'organisations': [{'orgId': str(org.orgId), 'name': org.name, 'description': org.description} for org in organisation]
        }
    }), 200


@organisation_bp.route('/organisations/<orgId>', methods=['GET'])
@jwt_required()
def get_organisation(orgId):
    userId = get_jwt_identity()
    user = User.query.filter_by(userId=userId).first()

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400
    org_uuid = uuid.UUID(orgId)
    org = Organisation.query.filter_by(orgId=org_uuid).first()
    if org not in user.organisations:
        return jsonify({'status': 'Bad request', 'message': 'Organisation not found or access denied'}), 400

    return jsonify({
        'status': 'success',
        'message': 'Organisation retrieved successfully',
        'data': {
            'orgId': str(org.orgId),
            'name': org.name,
            'description': org.description
        }
    }), 200


@organisation_bp.route('/organisations', methods=['POST'])
@jwt_required()
def create_organisation():
    userId = get_jwt_identity()
    user = User.query.filter_by(userId=userId).first()

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400

    data = request.get_json()

    if not data.get('name'):
        return jsonify({'errors': [{'field': 'name', 'message': 'Name is required'}]}), 422

    try:
        new_org = Organisation(
            name=data['name'],
            description=data.get('description', '')
        )
        new_org.users.append(user)

        db.session.add(new_org)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Organisation created successfully',
            'data': {
                'orgId': new_org.orgId,
                'name': new_org.name,
                'description': new_org.description
            }
        }), 201
    except:
        db.session.rollback()
        return jsonify({
            "status": "Bad Request",
            "message": "Client error",
            "statusCode": 400
        }), 400


@organisation_bp.route('/organisations/<orgId>/users', methods=['POST'])
@jwt_required()
def add_user_to_organisation(orgId):
    org_uuid = uuid.UUID(orgId)
    org = Organisation.query.filter_by(orgId=org_uuid).first()
    if not org:
        return jsonify({'status': 'Bad request', 'message': 'Organisation not found or access denied'}), 400

    data = request.get_json()
    new_user = User.query.filter_by(userId=data['userId']).first()

    if not new_user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400

    org.users.append(new_user)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'User added to organisation successfully'}), 200
