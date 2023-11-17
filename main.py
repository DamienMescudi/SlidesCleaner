import argparse
from google_slides import get_presentation_text, update_slide_text, authenticate_google_api
from openai_correction import correct_text_with_openai
from settings import load_settings
from text_validation import validate_correction

def main(args):
    settings = load_settings()
    service = authenticate_google_api(settings['google_service_account_file'])

    presentation_id = args.presentation_id
    model = args.model
    auto_correct = args.auto_correct

    text_elements = get_presentation_text(service, presentation_id)

    for element_id, full_text in text_elements.items():
        if full_text.strip():
            corrected_text = correct_text_with_openai(full_text, settings['openai_api_key'], model)

            if auto_correct:
                update_slide_text(service, presentation_id, element_id, corrected_text)
            else:
                user_decision = validate_correction(full_text, corrected_text)
                if user_decision["approved"]:
                    update_slide_text(service, presentation_id, element_id, user_decision["text"])
                else:
                    print("Correction rejetée par l'utilisateur.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up Google Slides text.")
    parser.add_argument("presentation_id", help="Google Slides presentation ID")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="OpenAI model to use for correction")
    parser.add_argument("--auto-correct", action='store_true', help="Apply corrections automatically without validation")
    args = parser.parse_args()
    main(args)
