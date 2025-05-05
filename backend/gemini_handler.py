# gemini_handler.py
import google.generativeai as genai
import os
from dotenv import load_dotenv
import datetime # To create timestamped log files

load_dotenv()

# --- Log Directory ---
LOG_DIR = "gemini_logs"
os.makedirs(LOG_DIR, exist_ok=True) # Create log directory if it doesn't exist

# --- Configuration ---
API_KEY = os.getenv('GEMINI_API_KEY')
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Avertissement: Clé API Gemini non trouvée dans .env. La fonction d'amélioration sera désactivée.")
# --- End Configuration ---

# Choose a model - Use the latest flash model for speed and capability
MODEL_NAME = "gemini-2.5-flash-preview-04-17"

def enhance_email_content(raw_message, subject):
    """
    Uses Gemini API to transform raw text into a visually appealing HTML email body.

    Args:
        raw_message (str): The original plain text message.
        subject (str): The subject of the email (for context).

    Returns:
        str: The generated HTML email body, or None if enhancement fails or API key is missing.
        str: An error message if generation failed, otherwise None.
    """
    if not API_KEY:
        return None, "Clé API Gemini manquante."
    if not raw_message:
        return None, "Message brut vide fourni pour l'amélioration."

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        # --- Prompt Engineering ---
        # Revised prompt to include basic inline styling for visual appeal
        prompt = f"""
        Tâche : Convertis le message texte brut suivant en un corps d'email HTML bien structuré, professionnel, facile à lire et **visuellement amélioré avec des styles inline**.
        Contexte : L'objet de l'email est "{subject}".
        Instructions :
        1.  Structure le contenu en utilisant des balises HTML sémantiques appropriées : paragraphes `<p>`, titres `<h2>` ou `<h3>`, listes `<ol><li>` ou `<ul><li>`. Utilise `<code>` pour les identifiants techniques ou noms de code.
        2.  **Détection et Style des Tableaux :** Identifie les données tabulaires et utilise `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`. **Applique un style de base directement sur les balises en utilisant des attributs `style` inline :**
            *   Ajoute une bordure simple et grise au tableau et à ses cellules (par ex., `style="border: 1px solid #cccccc;"`).
            *   Applique `border-collapse: collapse;` au tableau (`<table style="border-collapse: collapse; border: 1px solid #cccccc;">`) pour des bordures nettes.
            *   Ajoute un peu de padding interne aux cellules pour l'espacement (par ex., `style="border: 1px solid #cccccc; padding: 5px 8px;"` pour `<th>` et `<td>`).
        3.  Utilise `<strong>` pour mettre en évidence les informations importantes ou les points clés (y compris dans les `<th>`). Fais ressortir les en-têtes de section (comme "Section 1: ...").
        4.  Utilise `<br>` *uniquement si strictement nécessaire* pour les sauts de ligne au sein d'un paragraphe ou d'une cellule de tableau (`<td>`). Préfère les éléments de bloc distincts (`<p>`, `<h2>`, `<table>`) pour la structure principale.
        5.  **Style Général (Inline CSS) :** Applique des styles inline *simples et professionnels* pour améliorer la lisibilité globale. Par exemple :
            *   Ajoute un peu d'espace en dessous des titres (`<h2 style="margin-bottom: 10px;">`).
            *   Assure une taille de police lisible (pas besoin de spécifier sauf si nécessaire pour la hiérarchie).
            *   Maintiens un aspect général propre et moderne, sans couleurs excessives ni mises en page trop complexes. L'objectif principal est la **clarté** et la **professionnalisme**.
        6.  Préserve intégralement le sens et les informations du message original. Ne rajoute pas d'informations qui n'étaient pas présentes.
        7.  Génère UNIQUEMENT le fragment HTML destiné à être inséré dans la balise `<body>`. N'inclus PAS les balises `<html>`, `<head>`, `<body>` ou `<!DOCTYPE>`.
        8.  Si le message brut est très simple (par exemple, une seule phrase), enveloppe-le simplement dans `<p>`.
        9.  Assure-toi que le HTML généré est valide et que les styles inline sont correctement formatés (par ex., `style="property: value; property2: value2;"`).

        Message brut :
        ---
        {raw_message}
        ---

        Fragment HTML pour le corps de l'email :
        """

        print(f"Envoi de la requête à Gemini (modèle {MODEL_NAME})...")
        response = model.generate_content(prompt)

        # Check for safety flags or empty response
        if not response.parts:
             if response.prompt_feedback.block_reason:
                 error_msg = f"Génération bloquée par Gemini. Raison: {response.prompt_feedback.block_reason}"
                 print(error_msg)
                 return None, error_msg
             else:
                 error_msg = "Réponse vide de Gemini sans raison de blocage spécifiée."
                 print(error_msg)
                 return None, error_msg

        raw_response_text = response.text
        print("Réponse brute de Gemini reçue.")

        # --- Strip Markdown code block fences if present ---
        generated_html = raw_response_text.strip()
        if generated_html.startswith("```html"):
            generated_html = generated_html[7:] # Remove ```html
        if generated_html.endswith("```"):
            generated_html = generated_html[:-3] # Remove ```
        generated_html = generated_html.strip() # Strip again after removing fences

        # --- Log the raw response and the processed HTML ---
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            log_filename = os.path.join(LOG_DIR, f"gemini_response_{timestamp}.txt")
            with open(log_filename, "w", encoding="utf-8") as f:
                f.write(f"--- Prompt ---\n{prompt}\n\n--- Raw Response ---\n{raw_response_text}\n\n--- Processed HTML ---\n{generated_html}")
            print(f"Réponse brute et HTML traité enregistrés dans {log_filename}")
        except Exception as log_e:
            print(f"Erreur lors de l'enregistrement du log Gemini: {log_e}")
        # --- End Logging ---

        # Basic check if the *processed* content looks like HTML
        if not generated_html.startswith(('<', '<div>', '<p>', '<h2>', '<h3>', '<ul>', '<li>')):
            print("Avertissement: La réponse traitée de Gemini ne semble pas être du HTML valide. Utilisation du texte brut comme fallback.")
            # Return the fallback HTML, but also the error message
            return f"<p>{raw_message}</p>", "Réponse traitée non-HTML de Gemini"

        # Return the successfully generated and processed HTML and no error
        return generated_html, None

    except Exception as e:
        error_msg = f"Erreur lors de l'appel à l'API Gemini: {e}"
        print(error_msg)
        return None, error_msg
