import tkinter as tk
import difflib

def validate_correction(original_text, corrected_text):
    user_decision = {"approved": False, "text": corrected_text}

    def on_approve():
        user_decision["approved"] = True
        user_decision["text"] = corrected_textbox.get("1.0", tk.END).strip()
        root.destroy()

    def on_reject():
        user_decision["approved"] = False
        root.destroy()

    root = tk.Tk()
    root.title("Validate Correction")

    # Créer un cadre pour organiser les zones de texte
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    # Zone de texte pour le texte original
    original_textbox = tk.Text(frame, height=10, width=50)
    original_textbox.grid(row=0, column=0, padx=(0, 10), pady=(0, 10))
    original_textbox.insert(tk.END, original_text)

    # Zone de texte pour le texte corrigé
    corrected_textbox = tk.Text(frame, height=10, width=50)
    corrected_textbox.grid(row=0, column=1, padx=(10, 0), pady=(0, 10))
    corrected_textbox.insert(tk.END, corrected_text)

    # Configurer les tags pour le style
    original_textbox.tag_config("incorrect", foreground="red", font=("Helvetica", "10", "bold"))
    corrected_textbox.tag_config("corrected", foreground="green", font=("Helvetica", "10", "bold"))

    # Appliquer les tags pour mettre en évidence les différences
    highlight_differences(original_text, corrected_text, original_textbox, corrected_textbox)

    # Bouton pour approuver la modification
    approve_button = tk.Button(root, text="Approuver", command=on_approve)
    approve_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Bouton pour rejeter la modification
    reject_button = tk.Button(root, text="Rejeter", command=on_reject)
    reject_button.pack(side=tk.RIGHT, padx=5, pady=5)

    root.mainloop()

    return user_decision

def highlight_differences(original, corrected, original_text_widget, corrected_text_widget):
    # Diviser les textes en mots pour la comparaison
    original_words = original.split()
    corrected_words = corrected.split()
    s = difflib.SequenceMatcher(None, original_words, corrected_words)

    original_index = corrected_index = 0
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'replace' or tag == 'delete':
            start = f"1.0 + {original_index} chars"
            original_index += sum(len(word) + 1 for word in original_words[i1:i2])  # +1 pour les espaces
            end = f"1.0 + {original_index} chars"
            original_text_widget.tag_add("incorrect", start, end)
        
        if tag == 'replace' or tag == 'insert':
            start = f"1.0 + {corrected_index} chars"
            corrected_index += sum(len(word) + 1 for word in corrected_words[j1:j2])  # +1 pour les espaces
            end = f"1.0 + {corrected_index} chars"
            corrected_text_widget.tag_add("corrected", start, end)

        if tag == 'equal':
            n_chars = sum(len(word) + 1 for word in original_words[i1:i2])
            original_index += n_chars
            corrected_index += n_chars

