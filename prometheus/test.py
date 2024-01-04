import requests
import time

while True:
    try:
        response = requests.get("http://host.docker.internal/predictions")
        print(response.text)
    except requests.RequestException as e:
        print(f"Error making request: {e}")
    time.sleep(3)
