import pytest
import json
from flask_jwt_extended import decode_token  # Import function to decode JWT tokens
from datetime import datetime, timedelta
from app import db  # Import the SQLAlchemy database instance
from app.models import User, Organisation  # Import the User and Organisation models

# Fixture to provide authentication headers for the tests
@pytest.fixture
def auth_headers(client):
    user_data = {
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    response = client.post('/auth/register', json=user_data)  # Register a new user
    data = json.loads(response.data)
    token = data.get('accessToken')  # Extract the access token from the response
    return {'Authorization': f'Bearer {token}'}  # Return the headers with the token

# Test to verify token expiration
def test_token_expiration(app, client):
    with app.app_context():  # Ensure the test runs within the application context
        user_data = {
            "firstName": "Test",
            "lastName": "User",
            "email": "test_exp@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = client.post('/auth/register', json=user_data)  # Register a new user
        data = json.loads(response.data)
        token = data.get('accessToken')  # Extract the access token from the response
        
        decoded_token = decode_token(token)  # Decode the JWT token
        exp_time = datetime.fromtimestamp(decoded_token['exp'])  # Get expiration time
        now = datetime.utcnow()  # Get current UTC time
        
        # Assert that the token expires in roughly one hour
        assert (exp_time - now) < timedelta(hours=1, minutes=1)
        assert (exp_time - now) > timedelta(minutes=59)
        assert decoded_token['sub'] == str(data['user']['userId'])  # Check token's subject

# Test to verify user access to organisations
def test_organisation_access(app, client, auth_headers):
    with app.app_context():  # Ensure the test runs within the application context
        org1 = Organisation(name="Org1")  # Create Organisation 1
        org2 = Organisation(name="Org2")  # Create Organisation 2
        db.session.add_all([org1, org2])  # Add organisations to the session
        db.session.commit()  # Commit the session to save to the database

        user = User.query.filter_by(email="test@example.com").first()  # Get the registered user
        user.organisation_id = org1.id  # Assign Organisation 1 to the user
        db.session.commit()  # Commit the session to save to the database

        response = client.get(f'/organisations/{org1.id}', headers=auth_headers)  # Access Org 1
        assert response.status_code == 200  # User should have access to Org 1

        response = client.get(f'/organisations/{org2.id}', headers=auth_headers)  # Access Org 2
        assert response.status_code == 403  # User should not have access to Org 2

# Test to register a user with a default organisation
def test_register_user_with_default_organisation(client):
    user_data = {
        "firstName": "Jane",
        "lastName": "Doe",
        "email": "jane@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    response = client.post('/auth/register', json=user_data)  # Register a new user
    assert response.status_code == 201  # Check for successful registration
    data = json.loads(response.data)
    assert data['user']['firstName'] == "Jane"  # Verify user details
    assert data['user']['lastName'] == "Doe"
    assert data['user']['email'] == "jane@example.com"
    assert 'accessToken' in data  # Ensure access token is included in response
    assert data['organisation']['name'] == "Jane's Organisation"  # Check default organisation name

# Test to verify successful login
def test_login_success(client):
    user_data = {
        "firstName": "Alice",
        "lastName": "Wonder",
        "email": "alice@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    client.post('/auth/register', json=user_data)  # Register a new user

    login_data = {
        "email": "alice@example.com",
        "password": "password123"
    }
    response = client.post('/auth/login', json=login_data)  # Attempt to login
    assert response.status_code == 200  # Check for successful login
    data = json.loads(response.data)
    assert data['status'] == 'success'  # Verify success status
    assert 'accessToken' in data  # Ensure access token is included in response
    assert data['user']['email'] == "alice@example.com"  # Check user email in response

# Test to verify login failure with incorrect credentials
def test_login_failure(client):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post('/auth/login', json=login_data)  # Attempt to login with incorrect credentials
    assert response.status_code == 401  # Check for authentication failure

# Parametrized test to verify registration with missing fields
@pytest.mark.parametrize("missing_field", ["firstName", "lastName", "email", "password", "phone"])
def test_register_missing_fields(client, missing_field):
    user_data = {
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    del user_data[missing_field]  # Remove the specified field from user data
    response = client.post('/auth/register', json=user_data)  # Attempt to register
    assert response.status_code == 422  # Check for validation error
    data = json.loads(response.data)
    assert any(error['field'] == missing_field for error in data['errors'])  # Verify the missing field in errors

# Test to verify registration with a duplicate email
def test_register_duplicate_email(client):
    user_data = {
        "firstName": "Test",
        "lastName": "User",
        "email": "duplicate@example.com",
        "password": "password123",
        "phone": "1234567890"
    }
    client.post('/auth/register', json=user_data)  # Register a new user with email

    response = client.post('/auth/register', json=user_data)  # Attempt to register again with the same email
    assert response.status_code == 422  # Check for validation error due to duplicate email
    data = json.loads(response.data)
    assert any("Email already exists" in error['message'] for error in data['errors'])  # Verify the duplicate email error
