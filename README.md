# Local AI Chat Interface

## Description

This project provides a web-based chat interface using Streamlit to interact with Large Language Models (LLMs) hosted locally on your machine via LM Studio or a compatible backend like Ollama. It allows for private, network-accessible AI interactions, including text and optional image uploads (for multimodal models). The front-end is designed to be run as a Docker container.

## Features

* **Web Interface:** Clean chat UI built with Streamlit.
* **Local LLM Backend:** Connects to AI models running locally (LM Studio default).
* **Chat History:** Remembers the conversation context within a session.
* **Image Upload:** Supports uploading images to potentially use with multimodal models.
* **Dockerized:** Easy deployment and dependency management using Docker.
* **Private & Local:** Runs entirely within your local network on your hardware.
* **Configurable:** Backend host/port can be set via environment variables.

## Prerequisites

* **Docker:** Docker Desktop installed and running. ([https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/))
* **AI Backend Server:**
    * **LM Studio:** Installed, with desired models downloaded. Server must be started and configured to listen on `0.0.0.0` (or the host's specific IP) and a specific port (default 1234). ([https://lmstudio.ai/](https://lmstudio.ai/))
    * **OR Ollama:** Installed, with desired models pulled. Ollama service must be running. ([https://ollama.com/](https://ollama.com/))
* **Models:** Appropriate text or multimodal models available within your chosen backend.
* **Local Network:** A functioning local network where the host machine (running the AI backend) and client devices can communicate.

## Setup and Usage

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd <repository-folder-name>
    ```

2.  **Start AI Backend Server:**
    * Ensure your LM Studio server or Ollama service is running on your host machine.
    * Make note of the host machine's **local IP address** (e.g., `192.168.1.15`) or its `.local` hostname (e.g., `mymac.local`).
    * Make note of the **port** the backend server is listening on (e.g., `1234` for LM Studio, `11434` for Ollama by default).

3.  **Build the Docker Image:**
    ```bash
    docker build -t local-ai-ui .
    ```
    *(You can replace `local-ai-ui` with your preferred image name)*

4.  **Run the Docker Container:**
    * You **must** provide the host and port of your AI backend server using environment variables (`-e` flag).

    ```bash
    docker run -d \
      -p 8501:8501 \
      -e BACKEND_HOST="<YOUR_BACKEND_HOST_IP_OR_HOSTNAME>" \
      -e BACKEND_PORT="<YOUR_BACKEND_PORT>" \
      --name my-ai-app \
      --restart unless-stopped \
      local-ai-ui
    ```
    * **Replace `<YOUR_BACKEND_HOST_IP_OR_HOSTNAME>`** with the actual IP address or `.local` hostname of the machine running LM Studio/Ollama (e.g., `192.168.1.15` or `mymac.local`).
    * **Replace `<YOUR_BACKEND_PORT>`** with the port number your AI backend is listening on (e.g., `1234` or `11434`).
    * `-d`: Run detached (in the background).
    * `-p 8501:8501`: Map port 8501 on your host to port 8501 in the container.
    * `--name my-ai-app`: Assign a name to the container.
    * `--restart unless-stopped`: Set the restart policy.

5.  **Access the Application:**
    * Open a web browser on any device on your local network.
    * Navigate to `http://<IP_ADDRESS_OF_MACHINE_RUNNING_DOCKER>:8501`
    * (e.g., `http://192.168.1.15:8501` if Docker is running on the same machine as the backend).

## Configuration via Environment Variables

The Docker container uses these environment variables:

* `BACKEND_HOST`: (Required) The IP address or hostname of the machine running the AI backend server (LM Studio/Ollama).
* `BACKEND_PORT`: (Optional) The port number of the AI backend server. Defaults to `1234`.

## Technologies Used

* Python 3.10
* Streamlit
* Requests
* Docker
* LM Studio / Ollama (as backend)

## License

[Specify your license here, e.g., MIT License]
