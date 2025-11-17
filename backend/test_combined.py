import threading
import time
import requests
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8004, log_level="info")

def test_request():
    time.sleep(2)  # Wait for server to start
    try:
        response = requests.get("http://127.0.0.1:8004/")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Start server in a thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Make request
    test_request()

    # Wait a bit
    time.sleep(5)