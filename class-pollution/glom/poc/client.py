import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def register_user(user_data):
  url = f"{BASE_URL}/register"
  requests.post(url, data=json.dumps(user_data), headers={"Content-Type": "application/json"})

def update_user(key, value):
  url = f"{BASE_URL}/update"
  payload = {"key": key, "value": value}
  requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})

if __name__ == "__main__":
  user_data = {
      "id": "1",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "age": 30
  }

  register_user(user_data)
  update_user("userInfo.name", "jack")
  # update_user("__init__.__globals__.__name__", "polluted")

