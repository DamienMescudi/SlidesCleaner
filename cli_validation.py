from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

# Codes ANSI pour les couleurs
RED = "\033[31m"   # Rouge
GREEN = "\033[32m" # Vert
RESET = "\033[0m"  # Réinitialiser la couleur

def highlight_text_in_cli(original_text, corrected_text):
    original_words = original_text.split()
    corrected_words = corrected_text.split()
    highlighted_original = ""
    highlighted_corrected = ""
    difference_found = False

    for original, corrected in zip(original_words, corrected_words):
        if original != corrected:
            highlighted_original += RED + original + RESET + " "
            highlighted_corrected += GREEN + corrected + RESET + " "
            difference_found = True
        else:
            highlighted_original += original + " "
            highlighted_corrected += corrected + " "

    return highlighted_original, highlighted_corrected, difference_found

def validate_correction_cli(original_text, corrected_text):
    highlighted_original, highlighted_corrected, difference_found = highlight_text_in_cli(original_text, corrected_text)

    if difference_found:
        print("Texte original: " + highlighted_original)
        print("Texte corrigé: " + highlighted_corrected)

        session = PromptSession(history=InMemoryHistory())
        user_input = session.prompt("Accepter la correction? (y/n/edit): ").strip().lower()

        if user_input == 'y':
            return True, corrected_text, True  # Correction appliquée
        elif user_input == 'edit':
            print("Texte actuel corrigé: " + corrected_text)
            new_text = session.prompt("Modifiez le texte ci-dessous :\n", default=corrected_text).strip()
            return True, new_text, True  # Correction appliquée
        else:
            return False, original_text, False  # Correction rejetée
    else:
        return True, original_text, False  # Pas de correction nécessaire
