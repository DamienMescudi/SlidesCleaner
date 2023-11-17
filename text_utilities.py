import difflib

def highlight_differences(original, corrected):
    original_words = original.split()
    corrected_words = corrected.split()
    matcher = difflib.SequenceMatcher(None, original_words, corrected_words)
    highlighted_diff = ""
    for opcode in matcher.get_opcodes():
        tag, i1, i2, j1, j2 = opcode
        if tag == 'equal':
            highlighted_diff += " ".join(original_words[i1:i2]) + " "
        elif tag in ['replace', 'insert']:
            highlighted_diff += "\033[92m" + " ".join(corrected_words[j1:j2]) + "\033[0m" + " "
        elif tag == 'delete':
            highlighted_diff += "\033[91m" + " ".join(original_words[i1:i2]) + "\033[0m" + " "
    return highlighted_diff
