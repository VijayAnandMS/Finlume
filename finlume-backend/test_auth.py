import sys
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
res = client.post('/api/auth/register', json={'full_name': 'Test', 'username': 'demouser123', 'password': 'password123', 'email': 'test_demouser123@test.com'})
print('REGISTER:', res.status_code, res.json())

token_res = client.post('/api/auth/login', data={'username': 'demouser123', 'password': 'password123'})
print('LOGIN:', token_res.status_code, token_res.json())
