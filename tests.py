import requests

headers = {
    "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzc2NjgzMDg1fQ.NRTbAGyCGWepNOZcLOfq6PQEPZ_PD7VoXWA8D1JlTA4'
}

req = requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers)

print(req)
print(req.json())