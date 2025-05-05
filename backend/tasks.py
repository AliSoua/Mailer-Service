import os
# import eventlet # Removed - will be handled in run_worker.py
# eventlet.monkey_patch() # Removed - will be handled in run_worker.py
from celery import Celery
from dotenv import load_dotenv

# Import your handlers
import smtp_handler
import gemini_handler

load_dotenv()

# --- Celery Configuration ---
# Use environment variables for broker and backend URLs
# Default to local Redis if not set
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery(
    'mailer_tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['tasks'] # Point to this module to find tasks
)

# Optional Celery configuration settings
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Accept json content
    result_serializer='json',
    timezone='Europe/London', # Match your timezone if needed
    enable_utc=True,
    # Add task tracking settings if needed later
    # task_track_started=True,
)

# --- Celery Task Definition ---
@celery_app.task(bind=True, name='tasks.process_and_send_email')
def process_and_send_email(self, recipient, subject, raw_message, enhance):
    """
    Celery task to enhance (optional) and send an email.
    'bind=True' allows accessing task instance via 'self'.
    """
    task_id = self.request.id
    print(f"[Task {task_id}] Received: Enhance={enhance} for {recipient}")

    # --- Content Preparation ---
    final_body = raw_message
    content_type = 'plain'
    enhancement_status = "non tentée"
    enhancement_error = None

    if enhance:
        print(f"[Task {task_id}] Tentative d'amélioration du contenu via Gemini...")
        try:
            html_body, gemini_error = gemini_handler.enhance_email_content(raw_message, subject)

            # Check if enhancement succeeded *without* errors/fallbacks from the handler
            if html_body and not gemini_error:
                final_body = html_body
                content_type = 'html'
                enhancement_status = "réussie"
                print(f"[Task {task_id}] Amélioration Gemini réussie.")
            else:
                # Enhancement failed or handler returned fallback HTML
                enhancement_status = "échouée"
                # Use the specific error from gemini_handler if available
                enhancement_error = gemini_error or "Erreur inconnue lors de l'amélioration Gemini."
                print(f"[Task {task_id}] Échec/Fallback de l'amélioration Gemini: {enhancement_error}. Utilisation du message brut ou fallback.")
                # If html_body exists, it's the fallback. Use it but mark as failed enhancement.
                if html_body:
                    final_body = html_body
                    content_type = 'html' # Still send as HTML if fallback exists
                # else: final_body remains raw_message, content_type remains 'plain'

        except Exception as e_gemini:
            enhancement_status = "échouée (exception)"
            enhancement_error = f"Exception lors de l'appel Gemini: {e_gemini}"
            print(f"[Task {task_id}] {enhancement_error}. Utilisation du message brut.")
            # Fallback to plain text

    # --- Email Sending ---
    print(f"[Task {task_id}] Préparation de l'envoi via SMTP ({content_type})...")
    try:
        success, smtp_error = smtp_handler.send_email(
            recipient_email=recipient,
            subject=subject,
            body=final_body,
            content_type=content_type
        )

        if success:
            print(f"[Task {task_id}] Email envoyé avec succès à {recipient}.")
            result = {
                "status": "success",
                "recipient": recipient,
                "enhancement_status": enhancement_status,
            }
            if enhancement_error:
                result["enhancement_error"] = enhancement_error
            return result # Task succeeded
        else:
            error_msg = f"Échec de l'envoi SMTP: {smtp_error}"
            print(f"[Task {task_id}] {error_msg}")
            # You might want to retry the task here using self.retry()
            # For now, just report failure
            raise Exception(f"SMTP Error: {smtp_error}") # Raise exception to mark task as failed

    except Exception as e_smtp:
        error_msg = f"Exception lors de l'envoi SMTP: {e_smtp}"
        print(f"[Task {task_id}] {error_msg}")
        # Raise exception to mark task as failed, Celery will handle it
        raise Exception(f"SMTP Exception: {e_smtp}")

# Example of how to run a worker (do not include in the script itself):
# celery -A tasks worker --loglevel=info
