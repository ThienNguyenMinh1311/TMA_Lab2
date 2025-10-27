🚀 AnythingLLM Deployment and Application Setup

This repository provides a reproducible and portable setup for deploying the AnythingLLM platform using Docker and running the associated FastAPI backend with Uvicorn.
The setup ensures seamless integration between backend services, frontend interfaces, and external model providers such as Ollama or OpenAI.

📦 1. Setup of AnythingLLM Using Docker

To efficiently deploy the AnythingLLM platform and guarantee environment consistency, Docker and Docker Compose are used as the primary containerization tools.

Docker encapsulates the entire application—including dependencies, configurations, and services—into isolated containers.
This minimizes compatibility issues across different systems and simplifies deployment.

🧩 Steps:

Install Docker and Docker Compose on the host machine.

Docker Installation Guide

Docker Compose Installation Guide

Clone the official AnythingLLM repository:

git clone https://github.com/Mintplex-Labs/anything-llm.git
cd anything-llm


Configure environment variables
Modify the .env file to match your environment:

PORT=3001
LLM_PROVIDER=ollama
OLLAMA_BASE_PATH=http://localhost:11434
OLLAMA_MODEL_PREF=qwen3:8b
STORAGE_DIR=/app/server/storage
JWT_SECRET="your-random-secret-key"


Launch the application:

docker compose up -d


This command builds and starts all services (backend, frontend, and databases) in detached mode.

Access the web interface:

Local access: http://localhost:3001

Remote access: http://<HOST_IP>:3001

Using Docker for deployment ensures a robust, scalable, and cross-platform setup, enabling easy updates and consistent operation across environments.

🧠 2. Cloning the Application Repository from GitHub and Environment Setup

The application source code is hosted on GitHub to ensure version control, collaboration, and reproducibility.

Steps:

Clone the repository:

git clone https://github.com/ThienNguyenMinh1311/TMA_Lab2.git
cd app


Install dependencies:

pip install -r requirements.txt


This ensures all necessary Python libraries and versions are installed for the application to run correctly.

(Optional) Configure environment variables:
Create a .env file if your application requires additional parameters such as:

DATABASE_URL=sqlite:///data.db
API_KEY=your-api-key
MODEL_PATH=/models/qwen3

⚙️ 3. Execution

After completing the environment setup, the backend can be started using Uvicorn, a high-performance ASGI server for FastAPI.

Run in Development Mode:
cd ..
uvicorn app.main:app --reload


Default URL: http://127.0.0.1:8000

The --reload flag automatically restarts the server when code changes, which is useful during development.

Enable Remote Access:

If you want other devices on the same network to access the server:

uvicorn app.main:app --host 0.0.0.0 --port 8000


Access via:

http://<HOST_IP>:8000

🧾 4. Summary
Component	Description
Docker Compose	Container orchestration for AnythingLLM backend, frontend, and storage services
.env File	Centralized environment configuration (keys, model provider, ports, etc.)
FastAPI + Uvicorn	Lightweight Python backend framework for serving APIs
Ollama / OpenAI	Supported model providers for LLM interaction
Port 3001 / 8000	Default ports for AnythingLLM and FastAPI backend
🛠️ Troubleshooting

401 Unauthorized Error:
Check if your API key or access token has the proper scopes (e.g., api.responses.write).
Update .env accordingly and restart with docker compose up -d.

Port Conflict:
Modify the PORT in .env if 3001 or 8000 are already in use.

Model Connection Issues:
Ensure your Ollama or OpenAI endpoint is reachable and properly configured.

📚 References

AnythingLLM GitHub Repository

FastAPI Documentation

Uvicorn Documentation

Docker Documentation
