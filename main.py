import argparse
from google_slides import get_presentation_text, update_slide_text, authenticate_google_api
from openai_correction import correct_text_with_openai
from settings import load_settings
from text_validation import validate_correction
import cli_validation

def main(args):
    settings = load_settings()
    service = authenticate_google_api(settings['google_service_account_file'])
    presentation_id = args.presentation_id
    model = args.model
    auto_correct = args.auto_correct
    use_gui_validation = args.guivalid

    text_elements = get_presentation_text(service, presentation_id)
    current_slide_number = 0

    for element_id, full_text, slide_number in text_elements:
        if slide_number != current_slide_number:
            if current_slide_number != 0:
                print(f"Slide {current_slide_number} entièrement corrigée.")
            current_slide_number = slide_number
            print(f"Correction de la slide {slide_number}...")

        if full_text.strip():
            corrected_text = correct_text_with_openai(full_text, settings['openai_api_key'], model)

            if auto_correct:
                if full_text.strip() != corrected_text.strip():
                    update_slide_text(service, presentation_id, element_id, corrected_text)
                    print("Correction appliquée.")
                else:
                    print("Pas d'erreur détectée.")
            elif use_gui_validation:
                user_decision = validate_correction(full_text, corrected_text)
                if user_decision["approved"]:
                    update_slide_text(service, presentation_id, element_id, user_decision["text"])
                    print("Correction appliquée.")
                else:
                    print("Correction rejetée par l'utilisateur.")
            else:
                user_approved, final_text, correction_made = cli_validation.validate_correction_cli(full_text, corrected_text)
                if user_approved:
                    update_slide_text(service, presentation_id, element_id, final_text)
                    if correction_made:
                        print("Correction appliquée.")
                    else:
                        print("Pas d'erreur détectée.")
                else:
                    print("Correction rejetée par l'utilisateur.")

    if current_slide_number != 0:
        print(f"Slide {current_slide_number} entièrement corrigée.")

    print("La présentation a été entièrement corrigée.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up Google Slides text.")
    parser.add_argument("presentation_id", help="Google Slides presentation ID")
    parser.add_argument("--model", default="gpt-3.5-turbo", help="OpenAI model to use for correction")
    parser.add_argument("--auto-correct", action='store_true', help="Apply corrections automatically without validation")
    parser.add_argument("--guivalid", action='store_true', help="Use GUI pop-ups for validation even in CLI mode")
    args = parser.parse_args()
    main(args)
