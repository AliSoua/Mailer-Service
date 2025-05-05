# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
import os
from dotenv import load_dotenv

# Import the Celery task
from tasks import process_and_send_email

load_dotenv() # Load environment variables from .env

app = Flask(__name__)
CORS(app) # Enable CORS for all routes by default

# --- Health Check Endpoint ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Mailing service is running"}), 200

# --- Main Email Sending Endpoint ---
@app.route('/message', methods=['POST'])
def handle_message():
    """
    Endpoint to receive email details and send the email.
    Optionally enhances content using Gemini.
    """
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.get_json()

    # --- Input Validation ---
    recipient = data.get('destinataire')
    subject = data.get('sujet')
    raw_message = data.get('message')
    enhance = data.get('enhance_content', False) # Default to False if not provided

    if not all([recipient, subject, raw_message]):
        missing = [k for k, v in {'destinataire': recipient, 'sujet': subject, 'message': raw_message}.items() if not v]
        return jsonify({"status": "error", "message": f"Champs manquants: {', '.join(missing)}"}), 400

    # --- Content Preparation ---
    final_body = raw_message
    content_type = 'plain'
    enhancement_status = "non tentée"
    # --- Queue Task ---
    try:
        # Queue the task with the necessary arguments
        task = process_and_send_email.delay(
            recipient=recipient,
            subject=subject,
            raw_message=raw_message,
            enhance=enhance
        )
        print(f"Tâche {task.id} mise en file d'attente pour {recipient}")

        # --- Response ---
        # Return 202 Accepted status indicating the task is queued
        return jsonify({
            "status": "queued",
            "message": "La demande d'envoi d'email a été mise en file d'attente.",
            "task_id": task.id
        }), 202

    except Exception as e:
        # Handle potential errors during task queuing (e.g., broker connection issue)
        print(f"Erreur lors de la mise en file d'attente de la tâche: {e}")
        return jsonify({
            "status": "error",
            "message": "Échec de la mise en file d'attente de la tâche.",
            "error_details": str(e)
        }), 500 # Internal Server Error

# Note: The if __name__ == '__main__': block with app.run() is removed.
# Use a WSGI server like Gunicorn for production.
# Example: gunicorn -w 4 -b 127.0.0.1:5001 app:app
