# 🚀 AnythingLLM Deployment and Application Setup

This repository provides a reproducible and portable setup for deploying the **AnythingLLM** platform using **Docker**, as well as running the associated **FastAPI backend** with **Uvicorn**.  
The setup ensures seamless integration between backend services, frontend interfaces, and external model providers such as **Ollama** or **OpenAI**.

---

## 📦 1. Setup of AnythingLLM Using Docker

To efficiently deploy the **AnythingLLM** platform and guarantee environment consistency, **Docker** and **Docker Compose** are used as the primary containerization tools.

Docker encapsulates the entire application—including dependencies, configurations, and services—into isolated containers.  
This minimizes compatibility issues across different systems and simplifies deployment.

### 🧩 Steps

1. **Install Docker and Docker Compose** on the host machine  
   - [Docker Installation Guide](https://docs.docker.com/get-docker/)  
   - [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

2. **Clone the official AnythingLLM repository**
   ```bash
   git clone https://github.com/Mintplex-Labs/anything-llm.git
   cd anything-llm
Configure environment variables
Modify the .env file to suit your setup:

bash
Copy code
PORT=3001
LLM_PROVIDER=ollama
OLLAMA_BASE_PATH=http://localhost:11434
OLLAMA_MODEL_PREF=qwen3:8b
STORAGE_DIR=/app/server/storage
JWT_SECRET="your-random-secret-key"
Start the application using Docker Compose

bash
Copy code
docker compose up -d
This command builds and launches all containers in detached mode, running the backend, frontend, and any related services.

Access the web interface

Local access: http://localhost:3001

Remote access: http://<HOST_IP>:3001

💡 Using Docker ensures a robust, scalable, and cross-platform setup that simplifies updates and guarantees consistent deployment across environments.

🧠 2. Cloning the Application Repository from GitHub and Environment Setup
The application source code is hosted on GitHub to ensure version control, collaboration, and reproducibility.

🧩 Steps
Clone the repository

bash
Copy code
git clone https://github.com/ThienNguyenMinh1311/TMA_Lab2.git
cd app
Install dependencies

bash
Copy code
pip install -r requirements.txt
This ensures that all required Python packages are installed in the environment, matching the development configuration.

(Optional) Configure environment variables
If the application requires specific configuration, create a .env file and define:

bash
Copy code
DATABASE_URL=sqlite:///data.db
API_KEY=your-api-key
MODEL_PATH=/models/qwen3
These parameters ensure smooth communication between the backend services and other integrated systems.

⚙️ 3. Execution
Once all dependencies are installed, the application can be launched using Uvicorn, a high-performance ASGI server for FastAPI.

🧩 Run in Development Mode
bash
Copy code
cd ..
uvicorn app.main:app --reload
Default access: http://127.0.0.1:8000

The --reload flag automatically restarts the server whenever changes are made to the code, ideal for development.

🧩 Enable Remote Access
If you want other devices on the same network to access the backend:

bash
Copy code
uvicorn app.main:app --host 0.0.0.0 --port 8000
Now, the backend can be accessed through:

cpp
Copy code
http://<HOST_IP>:8000
⚙️ This allows the FastAPI backend to integrate seamlessly with the frontend or other services (e.g., the AnythingLLM interface).

🧾 4. Summary
Component	Description
Docker Compose	Orchestrates AnythingLLM services (backend, frontend, and storage)
.env File	Centralized configuration for environment variables and API keys
FastAPI + Uvicorn	Lightweight Python backend for APIs and ML model serving
Ollama / OpenAI	Supported LLM providers for natural language processing
Port 3001 / 8000	Default ports for AnythingLLM UI and FastAPI backend

🛠️ 5. Troubleshooting
⚠️ 401 Unauthorized Error
If you see:

arduino
Copy code
401 You have insufficient permissions for this operation. Missing scopes: api.responses.write
Check that your API key or token has the correct scopes and roles.
Then restart the service:

bash
Copy code
docker compose up -d
⚠️ Port Conflict
If port 3001 or 8000 is already in use, modify the PORT value in .env or the Uvicorn command.

⚠️ Model Connection Issues
If AnythingLLM cannot connect to your model provider:

Ensure Ollama or OpenAI endpoints are reachable.

Verify the OLLAMA_BASE_PATH and LLM_PROVIDER values in .env.

📚 6. References
AnythingLLM GitHub Repository

FastAPI Documentation

Uvicorn Documentation

Docker Documentation

🧩 Author: ThienNguyenMinh1311
📅 Last Updated: October 2025
⚡ License: MIT
