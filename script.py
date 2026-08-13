
import requests

endpoint = f"https://viacep.com.br/ws/01001000/json/"

response = requests.get(endpoint)

print(response.json())