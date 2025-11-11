import requests

def create_workspace():
    url = f"{ANYTHING_API_BASE}/workspace/lawyer1_workspace/update"

    payload = {
        "chatProvider": "ollama",
        "chatModel": "qwen3:8b"
    }

    HEADERS_JSON = {
        "Authorization": f"Bearer {ANYTHING_API_KEY}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    response = requests.post(url, json=payload, headers=HEADERS_JSON)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to create workspace: {response.status_code} - {response.text}")

# Thử tạo workspace
workspace_info = create_workspace()
print(workspace_info)
