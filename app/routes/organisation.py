# app/routes/organisation.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Organisation, User

organisation_bp = Blueprint('organisation', __name__, url_prefix='/api')

@organisation_bp.route('/', methods=['GET'])
@jwt_required()
def get_organisations():
    userId = get_jwt_identity()
    user = User.query.filter_by(userId=userId).first()

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400

    orgs = user.organisations
    return jsonify({
        'status': 'success',
        'message': 'Organisations retrieved successfully',
        'data': {
            'organisations': [{'orgId': org.orgId, 'name': org.name, 'description': org.description} for org in orgs]
        }
    }), 200

@organisation_bp.route('/<orgId>', methods=['GET'])
@jwt_required()
def get_organisation(orgId):
    userId = get_jwt_identity()
    user = User.query.filter_by(userId=userId).first()

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400

    org = Organisation.query.filter_by(orgId=orgId).first()
    if org not in user.organisations:
        return jsonify({'status': 'Bad request', 'message': 'Organisation not found or access denied'}), 400

    return jsonify({
        'status': 'success',
        'message': 'Organisation retrieved successfully',
        'data': {
            'orgId': org.orgId,
            'name': org.name,
            'description': org.description
        }
    }), 200

@organisation_bp.route('/', methods=['POST'])
@jwt_required()
def create_organisation():
    userId = get_jwt_identity()
    user = User.query.filter_by(userId=userId).first()

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400

    data = request.get_json()

    if not data.get('name'):
        return jsonify({'errors': [{'field': 'name', 'message': 'Name is required'}]}), 422

    new_org = Organisation(
        orgId=f"{user.userId}_org_{len(user.organisations) + 1}",
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

@organisation_bp.route('/<orgId>/users', methods=['POST'])
@jwt_required()
def add_user_to_organisation(orgId):
    userId = get_jwt_identity()
    user = User.query.filter_by(userId=userId).first()

    if not user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400

    org = Organisation.query.filter_by(orgId=orgId).first()
    if org not in user.organisations:
        return jsonify({'status': 'Bad request', 'message': 'Organisation not found or access denied'}), 400

    data = request.get_json()
    new_user = User.query.filter_by(userId=data['userId']).first()

    if not new_user:
        return jsonify({'status': 'Bad request', 'message': 'User not found'}), 400

    org.users.append(new_user)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'User added to organisation successfully'}), 200
