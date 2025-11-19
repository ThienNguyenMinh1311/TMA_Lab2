import requests
import json

ANYTHING_API_KEY="GY8Z6GC-4KYMGNY-QSKHRAC-C4SSVZ5"
ANYTHING_API_BASE="http://finixai.mywire.org:5151/api/v1"

def get_document_name(folder_name: str, document_name: str) -> list:
    url = f"{ANYTHING_API_BASE}/documents/folder/{folder_name}"
    HEADERS_UPLOAD = {
            "Authorization": f"Bearer {ANYTHING_API_KEY}",
            "accept": "application/json",
        }
    response = requests.get(url, headers=HEADERS_UPLOAD)
    if response.status_code != 200:
        raise Exception(f"Error fetching documents: {response.text}")
    data = response.json()
    for doc in data.get("documents", []):
        if document_name in doc.get("name", ""):
            return doc["name"]
    
    return "Not found"

