import requests
payload = {
"user": "mohamadassi173@gmail.com",
"password": "astmamsh123",
"op": "basic"
}

res = requests.post('https://brokencrystals.com/api/auth/login', data=payload)

print(str(res.status_code))