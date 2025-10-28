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
3. **Configure environment variables**
- Edit the docker-compose.yml in anything-llm/docker
- Modify the .env file in antything-llm/server to suit your setup:
   ```bash
   #Adding this to the end of your .env file
   ENABLE_ADMIN_API=true
   ADMIN_API_KEY=<your_api_key>

4. **Start the application using Docker Compose**

   ```bash
   docker compose up -d
This command builds and launches all containers in detached mode, running the backend, frontend, and any related services.

5. **Access the web interface**

   - Local access: http://localhost:3001
   - Remote access: http://<HOST_IP>:3001

💡 Using Docker ensures a robust, scalable, and cross-platform setup that simplifies updates and guarantees consistent deployment across environments.

## 🧠 2. Cloning the Application Repository from GitHub and Environment Setup
The application source code is hosted on GitHub to ensure version control, collaboration, and reproducibility.

### 🧩 Steps
1. **Clone the repository**

   ```bash
   git clone https://github.com/ThienNguyenMinh1311/TMA_Lab2.git
   cd app
   
2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   
This ensures that all required Python packages are installed in the environment, matching the development configuration.

3. **(Optional) Configure environment variables**
If the application requires specific configuration, create a .env file and define:

   ```bash
   DATABASE_URL=sqlite:///data.db
   API_KEY=your-api-key
   MODEL_PATH=/models/qwen3
   
These parameters ensure smooth communication between the backend services and other integrated systems.

## ⚙️ 3. Execution
The FastAPI backend is powered by Uvicorn, a high-performance ASGI server, enabling integration with the AnythingLLM frontend and other services.
### 🧩 Run in Development Mode
To start the backend locally with auto-reload:
   ```bash
   cd TMA_Lab2
   uvicorn app.main:app --reload

Access: http://127.0.0.1:8000


   
