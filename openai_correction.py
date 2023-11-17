from openai import OpenAI

def correct_text_with_openai(text, api_key, model):
    client = OpenAI(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": f"Réécris cette phrase, sans fautes, sans guillemet, sans introduction ou quelconque intervention de ta part, garde mes intentions de présentations (retour à la ligne, majuscules par exemple, mais corrige ls fautes d'orthographes): {text}"}
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content.strip()
