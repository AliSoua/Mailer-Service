# Mailer Microservice - Backend

This backend service provides an API endpoint to receive email sending requests. It queues these requests using Celery, optionally enhances the email content using the Google Gemini API, and sends the emails via a configured SMTP server.

## Features

*   **Flask API:** Exposes an endpoint (`/message`) to accept email details.
*   **Celery Task Queue:** Asynchronously processes email sending requests using Redis as a broker.
*   **Gemini Content Enhancement:** Optionally transforms plain text email bodies into formatted HTML using the Gemini API.
*   **SMTP Sending:** Sends emails using standard SMTP protocols (supports SSL/TLS).
*   **Configuration:** Uses environment variables (`.env` file) for sensitive settings.
*   **CORS Enabled:** Allows requests from different origins (e.g., the frontend application).
*   **Health Check:** Provides a `/` endpoint to verify service status.
*   **Logging:** Logs Gemini API interactions (request/response) to the `gemini_logs/` directory.

## Technology Stack

*   **Language:** Python 3.x
*   **Framework:** Flask
*   **Task Queue:** Celery
*   **Message Broker/Result Backend:** Redis
*   **AI Content Enhancement:** Google Generative AI (Gemini)
*   **Environment Variables:** python-dotenv
*   **WSGI Server:** Waitress (for production)

## Setup

1.  **Prerequisites:**
    *   Python 3.x installed.
    *   Redis server installed and running.

2.  **Clone Repository:** (If applicable)
    ```bash
    git clone <your-repo-url>
    cd <your-repo-url>/backend
    ```

3.  **Create Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # Activate the environment
    # Windows:
    .\venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables:**
    Create a file named `.env` in the `backend` directory and add the following variables, replacing the placeholder values with your actual configuration:

    ```dotenv
    # Celery Configuration (Defaults to local Redis if not set)
    # CELERY_BROKER_URL=redis://localhost:6379/0
    # CELERY_RESULT_BACKEND=redis://localhost:6379/0

    # Google Gemini API Key
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY

    # SMTP Server Configuration
    SMTP_SERVER=smtp.example.com
    SMTP_PORT=587 # Or 465 for SMTP_SSL
    SMTP_LOGIN=your_smtp_username
    SMTP_PASSWORD=your_smtp_password
    SENDER_EMAIL=sender@example.com # The "From" address for emails
    ```

## Running the Application

Ensure your Redis server is running before starting the backend components.

1.  **Start the Celery Worker:**
    Open a terminal in the `backend` directory (with the virtual environment activated) and run:
    ```bash
    python run_worker.py
    ```
    This starts the worker process that listens for and executes email tasks from the queue.

2.  **Start the Flask API Server:**
    Open another terminal in the `backend` directory (with the virtual environment activated) and run:
    ```bash
    waitress-serve --host 127.0.0.1 --port 5001 app:app
    ```
    This starts the Flask application using the Waitress WSGI server, listening on port 5001.

The backend is now running and ready to accept requests.

## API Endpoint

### Send Email

*   **URL:** `/message`
*   **Method:** `POST`
*   **Content-Type:** `application/json`
*   **Payload:**
    ```json
    {
      "destinataire": "recipient@example.com",
      "sujet": "Your Email Subject",
      "message": "This is the plain text body of the email.",
      "enhance_content": true // Optional: set to true to use Gemini enhancement, false or omit otherwise
    }
    ```
*   **Success Response (202 Accepted):** Indicates the task has been queued.
    ```json
    {
      "status": "queued",
      "message": "La demande d'envoi d'email a été mise en file d'attente.",
      "task_id": "some-celery-task-id"
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request`: If the request is not JSON or required fields (`destinataire`, `sujet`, `message`) are missing.
    *   `500 Internal Server Error`: If there's an issue queuing the task (e.g., cannot connect to Redis).

### Health Check

*   **URL:** `/`
*   **Method:** `GET`
*   **Success Response (200 OK):**
    ```json
    {
      "status": "ok",
      "message": "Mailing service is running"
    }
    ```

## Logging

Details about Gemini API requests and responses (including the generated HTML) are logged to timestamped files in the `backend/gemini_logs/` directory. This is useful for debugging the content enhancement feature.
