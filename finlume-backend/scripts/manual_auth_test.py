import requests

print('--- REGISTER ---')
r1 = requests.post('http://localhost:8000/api/auth/register', json={'username':'live_test3','password':'mypassword'})
print(r1.status_code, r1.text)

print('--- LOGIN ---')
r2 = requests.post('http://localhost:8000/api/auth/login', json={'username':'live_test3','password':'mypassword'})
print(r2.status_code, r2.text)

if r2.status_code == 200:
    r3 = requests.get('http://localhost:8000/api/auth/me', headers={'Authorization': 'Bearer ' + r2.json()['access_token']})
    print('--- ME ---')
    print(r3.status_code, r3.text)
