from openai import OpenAI
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
import difflib
import tkinter as tk
from tkinter import scrolledtext



RED = '\033[91m'
GREEN = '\033[92m'
CROSS_OUT = '\033[9m'
END = '\033[0m'


def highlight_differences(original, corrected):
    original_words = original.split()
    corrected_words = corrected.split()
    matcher = difflib.SequenceMatcher(None, original_words, corrected_words)
    highlighted = ''

    for opcode in matcher.get_opcodes():
        tag, i1, i2, j1, j2 = opcode
        if tag == 'equal':
            highlighted += ' '.join(original_words[i1:i2]) + ' '
        elif tag == 'replace':
            highlighted += RED + CROSS_OUT + ' '.join(original_words[i1:i2]) + END + ' ' + GREEN + ' '.join(corrected_words[j1:j2]) + END + ' '
        elif tag == 'delete':
            highlighted += RED + CROSS_OUT + ' '.join(original_words[i1:i2]) + END + ' '
        elif tag == 'insert':
            highlighted += GREEN + ' '.join(corrected_words[j1:j2]) + END + ' '

    return highlighted.strip()



def load_settings():
    """ Charge les paramètres depuis le fichier settings.json. """
    with open('config/settings.json') as settings_file:
        return json.load(settings_file)

def authenticate_google_api(service_account_file):
    """ Authentifie l'utilisateur pour l'API Google avec un compte de service. """
    creds = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/presentations']
    )
    return creds

def get_presentation_text(service, presentation_id):
    """ Récupère tout le texte et les styles de chaque élément de texte des diapositives. """
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    text_elements = {}
    for slide in presentation.get('slides', []):
        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                element_id = element['objectId']
                text_content = ''
                for text_run in element['shape']['text']['textElements']:
                    if 'textRun' in text_run:
                        text_content += text_run['textRun']['content']
                text_elements[element_id] = text_content
    return text_elements

def find_text_differences(original_text, corrected_text):
    from difflib import ndiff

    diff = list(ndiff(original_text.split(), corrected_text.split()))
    changes = []
    for i, token in enumerate(diff):
        if token.startswith("- "):
            changes.append(("Supprimé", token[2:], i))
        elif token.startswith("+ "):
            changes.append(("Ajouté", token[2:], i))
    return changes



def correct_text_with_openai(text, api_key):
    """ Utilise OpenAI pour corriger le texte. """
    client = OpenAI(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": f"Réécris cette phrase, sans fautes, sans guillemet, sans introduction ou quelconque intervention de ta part, garde mes intentions de présentations (retour à la ligne, majuscules par exemple, mais corrige ls fautes d'orthographes): {text}"}
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content  # Modifié ici


def update_slide_text(service, presentation_id, element_id, new_text):
    """ Met à jour le texte d'un élément de diapositive spécifique. """
    requests = [
        {
            'deleteText': {
                'objectId': element_id,
                'textRange': {
                    'type': 'ALL'
                }
            }
        },
        {
            'insertText': {
                'objectId': element_id,
                'insertionIndex': 0,
                'text': new_text
            }
        }
    ]

    body = {'requests': requests}
    service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()

def on_submit():
    presentation_id = entry_presentation_id.get()
    text_elements = get_presentation_text(service, presentation_id)

    for element_id, full_text in text_elements.items():
        if full_text.strip():
            corrected_text = correct_text_with_openai(full_text, settings['openai_api_key'])
            highlighted_diff = highlight_differences(full_text, corrected_text)
            update_slide_text(service, presentation_id, element_id, corrected_text)
            text_area.insert(tk.INSERT, f"Correction apportée :\n{highlighted_diff}\n\n")

# Configuration de l'interface graphique
root = tk.Tk()
root.title("Correcteur de Présentation")
root.geometry("800x300")  # Largeur x Hauteur

# Création des widgets
label = tk.Label(root, text="Entrez l'ID de la présentation Google Slides :")
entry_presentation_id = tk.Entry(root)
submit_button = tk.Button(root, text="Corriger", command=on_submit)
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)

# Mise en page
label.pack(fill='x', padx=10, pady=5)
entry_presentation_id.pack(fill='x', padx=10, pady=5)
submit_button.pack(fill='x', padx=10, pady=5)
text_area.pack(expand=True, fill='both', padx=10, pady=5)


# Initialisation de service dans le scope global
settings = load_settings()
creds = authenticate_google_api('config/credentials.json')
service = build('slides', 'v1', credentials=creds)

# Démarrage de l'application
root.mainloop()

def main():
    presentation_id = input("Entrez l'ID de la présentation Google Slides : ")
    text_elements = get_presentation_text(service, presentation_id)

    for element_id, full_text in text_elements.items():
        if full_text.strip():  # Vérifiez si le texte n'est pas seulement des espaces blancs
            corrected_text = correct_text_with_openai(full_text, settings['openai_api_key'])
            highlighted_diff = highlight_differences(full_text, corrected_text)
            
            # Mise à jour du texte dans Google Slides
            update_slide_text(service, presentation_id, element_id, corrected_text)

            # Afficher les différences
            print(f"Correction apportée :\n{highlighted_diff}\n")

if __name__ == '__main__':
    main()

