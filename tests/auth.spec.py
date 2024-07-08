# tests/auth.spec.py
import unittest
from app import create_app, db
from app.models import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        response = self.client.post('/auth/register', json={
            'userId': 'testuser',
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'testuser@example.com',
            'password': 'password123',
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')

    def test_login(self):
        self.client.post('/auth/register', json={
            'userId': 'testuser',
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'testuser@example.com',
            'password': 'password123',
            'phone': '1234567890'
        })

        response = self.client.post('/auth/login', json={
            'email': 'testuser@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')

if __name__ == '__main__':
    unittest.main()
