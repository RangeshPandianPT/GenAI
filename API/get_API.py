import requests
import json
url = "https://api.restful-api.dev/objects"

payload = {
   "name": "Apple MacBook Pro 16",
   "data": {
      "year": 2019,
      "price": 1849.99,
      "CPU model": "Intel Core i9",
      "Hard disk size": "1 TB"
      }
}

headers = {
    "Content-Type":"application/json"}
response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200 or response.status_code == 201:
    print("Object created successfully.")
    print("Response JSON:")
    print (response.json())
else:
    print(f"Failed to create object. Status code: {response.status_code}")
    print(response.text)