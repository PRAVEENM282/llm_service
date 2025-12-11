# Containerized LLM Inference Service

A production-ready, containerized REST API for serving Large Language Models (LLMs). This service uses **FastAPI** for high-performance handling, **Docker** for containerization, and **Hugging Face Transformers** for the model backend.

## 🚀 Quick Start

### Prerequisites
* Docker
* Docker Compose

### Installation & Running
1.  **Clone the repository** (if applicable):
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Launch the service**:
    This command builds the optimized image and starts the container.
    ```bash
    docker-compose up --build
    ```

3.  **Verify Status**:
    The service will be available at `http://localhost:8000`.
    
    * **Health Check**:
        ```bash
        curl http://localhost:8000/health
        ```
    * **Swagger UI**: Visit `http://localhost:8000/docs` in your browser for interactive testing.

---

## 📖 API Documentation

### Authentication
All requests to the `/generate` endpoint must include the `X-API-Key` header.
* **Header**: `X-API-Key`
* **Default Value**: `mysecurekey123` (Configurable via `docker-compose.yml`)

### Endpoints

#### 1. `GET /health`
Checks if the service is operational.
* **Auth Required**: No
* **Response**:
    ```json
    {
      "status": "ok", 
      "message": "Service is running"
    }
    ```

#### 2. `POST /generate`
Generates text based on a provided prompt.
* **Auth Required**: Yes
* **Request Body** (JSON):
    ```json
    {
      "prompt": "The future of AI is",
      "max_new_tokens": 50,    // Optional: Defaults to 50 (1-200)
      "temperature": 0.7       // Optional: Defaults to 0.7 (0.1-2.0)
    }
    ```
* **Response** (JSON):
    ```json
    {
      "generated_text": "The future of AI is looking bright..."
    }
    ```
* **Error Responses**:
    * `403 Forbidden`: Invalid or missing API Key.
    * `422 Validation Error`: Invalid input parameters (e.g., negative tokens).

---

## 🏗 Architecture & Concurrency Strategy

### 1. Technology Stack
* **FastAPI**: Chosen for its native asynchronous support and speed.
* **Uvicorn**: An ASGI server to serve the application.
* **Hugging Face Transformers**: Used to load the `GPT-2 medium` model (lightweight, ~300MB).
* **PyTorch (CPU)**: We specifically use the CPU-only build of PyTorch to keep the Docker image size under 1.5GB.

### 2. Concurrency Handling Strategy


Handling blocking code in an async framework is a critical engineering challenge.
* **The Problem**: Neural network inference is a CPU-bound operation. If we ran the model directly in a standard FastAPI `async def` function, the Python Global Interpreter Lock (GIL) would block the entire event loop. This means the server would freeze and be unable to answer simple requests (like `/health`) while generating text.
* **The Solution**: We use a `ThreadPoolExecutor`.
    * The API endpoints are defined as `async def`.
    * The heavy inference task is offloaded to a separate thread using `asyncio.get_running_loop().run_in_executor()`.
    * This allows the main event loop to remain responsive, accepting new connections and handling heartbeat requests while the background thread processes the LLM generation.

### 3. Container Optimization
We utilize a **Multi-Stage Docker Build**:
1.  **Builder Stage**: Installs heavy build tools (GCC, etc.) and compiles dependencies.
2.  **Runtime Stage**: Copies only the necessary artifacts from the builder. This keeps the final production image clean and small, stripping out cached files and build tools.