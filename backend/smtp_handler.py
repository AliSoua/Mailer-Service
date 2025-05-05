# smtp_handler.py
import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import socket # <--- ADD THIS LINE

load_dotenv() # Load variables from .env file

# --- Configuration ---
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587)) # Default to 587 if not set
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
# --- End Configuration ---

def send_email(recipient_email, subject, body, content_type='plain'):
    """
    Sends an email using configured SMTP settings.

    Args:
        recipient_email (str): The recipient's email address.
        subject (str): The email subject.
        body (str): The email body content (plain text or HTML).
        content_type (str): 'plain' for text/plain, 'html' for text/html.

    Returns:
        bool: True if email was sent successfully, False otherwise.
        str: An error message if sending failed, otherwise None.
    """
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_LOGIN, SMTP_PASSWORD, SENDER_EMAIL]):
        return False, "Erreur: Configuration SMTP incomplète dans le fichier .env."

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    # Set content based on type
    if content_type == 'html':
        msg.set_content("Veuillez activer l'affichage HTML pour voir ce message.") # Fallback for non-HTML clients
        msg.add_alternative(body, subtype='html')
    else:
        msg.set_content(body) # Defaults to text/plain

    context = ssl.create_default_context()
    server = None
    try:
        print(f"Tentative de connexion à {SMTP_SERVER}:{SMTP_PORT}...")
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=15)
            server.login(SMTP_LOGIN, SMTP_PASSWORD)
        else: # Assuming STARTTLS for other ports like 587
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SMTP_LOGIN, SMTP_PASSWORD)

        print(f"Connexion réussie. Envoi de l'email à {recipient_email}...")
        server.send_message(msg)
        print(f"Email envoyé avec succès à {recipient_email}")
        return True, None

    except smtplib.SMTPAuthenticationError:
        error_msg = "Erreur: Authentification SMTP échouée. Vérifiez login/mot de passe."
        print(error_msg)
        return False, error_msg
    except smtplib.SMTPConnectError:
        error_msg = f"Erreur: Impossible de se connecter au serveur SMTP {SMTP_SERVER}:{SMTP_PORT}."
        print(error_msg)
        return False, error_msg
    except smtplib.SMTPServerDisconnected:
        error_msg = "Erreur: Déconnecté du serveur SMTP de manière inattendue."
        print(error_msg)
        return False, error_msg
    except socket.gaierror: # Handle DNS resolution errors
         error_msg = f"Erreur: Impossible de résoudre l'adresse du serveur SMTP {SMTP_SERVER}."
         print(error_msg)
         return False, error_msg
    except TimeoutError:
         error_msg = f"Erreur: Timeout lors de la connexion ou de l'envoi à {SMTP_SERVER}:{SMTP_PORT}."
         print(error_msg)
         return False, error_msg
    except Exception as e:
        error_msg = f"Erreur inattendue lors de l'envoi de l'email: {e}"
        print(error_msg)
        return False, error_msg
    finally:
        if server:
            try:
                server.quit()
                print("Connexion SMTP fermée.")
            except Exception as e_quit:
                 print(f"Erreur lors de la fermeture de la connexion SMTP: {e_quit}")