#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging
import difflib
import os
from openai import OpenAI
from diff_match_patch import diff_match_patch
from diff import POSIXDiffer, pdiff, compare_text_files


def authenticate_google_api(service_account_file):
    """ Authentifie l'utilisateur pour l'API Google avec un compte de service. """
    creds = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/presentations']
    )
    return creds


def get_presentation_text(service, presentation_id):
    """ Récupère tout le texte et les styles de chaque élément de texte des diapositives. """
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
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


def get_patches(original_text, corrected_text):
    dmp = diff_match_patch()
    patches = dmp.patch_make(original_text, corrected_text)
    return patches


def correct_text_with_openai(text, api_key, model, prompt):
    """ Utilise OpenAI pour corriger le texte. """
    client = OpenAI(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user",
                "content": f"{prompt}: {text}"}
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content  # Modifié ici


class SlideCleaner:
    def __init__(self, args):
        self.args = args
        self.presentation_id = args.id
        logging.info(f"Authenticating with Google API using {args.service_account}...")
        credentials = authenticate_google_api(args.service_account)
        self.service = build('slides', 'v1', credentials=credentials)
        logging.info("Successfully authenticated with Google API")
        self.model = args.model
        logging.info(
            f"Retrieving slides content for presentation {args.id}...")
        self.text_elements = get_presentation_text(
            self.service, self.presentation_id)
        logging.info("Successfully retrieved slides content")
        logging.debug(f"Text elements: {self.text_elements}")
        dotenv.load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise Exception("You must set the OPENAI_API_KEY environment variable to use OpenAI API")
        self.prompt = args.prompt_override

    def clean(self):
        logging.info("Starting cleaning process...")
        for element_id, full_text in self.text_elements.items():
            if full_text.strip():
                corrected_text = correct_text_with_openai(
                    full_text, self.openai_api_key, self.model, self.prompt)
                # save both to temp files and use diff tool
                with open('original.txt', 'w') as f:
                    f.write(full_text)
                with open('corrected.txt', 'w') as f:
                    f.write(corrected_text)
                difftool = os.getenv('DIFFTOOL', 'diff')
                subprocess.run([difftool, 'corrected.txt', 'original.txt'])
                patches = get_patches(full_text, corrected_text)
                # reread the file so that any changes made by the diff tool are taken into account
                with open('original.txt', 'r') as f:
                    full_text = f.read()
                if self.args.apply:
                    self.update_slide(element_id, full_text)
        logging.info("Cleaning process finished")

    def update_slide(self, element_id, new_text):
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
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id, body=body).execute()

DEFAULT_PROMPT="Réécris cette phrase, sans fautes, sans guillemet, sans introduction ou quelconque intervention de ta part, garde mes intentions de présentations (retour à la ligne, majuscules par exemple, mais corrige ls fautes d'orthographes):"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=str, help="ID of the Google Slide")
    parser.add_argument('--apply', '-a', action='store_true',
                        help="Apply the changes to the Google Slide (otherwise, just print the changes)")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Print verbose output")
    parser.add_argument('--service-account', '-s', type=str,
                        default='config/credentials.json', help="Path to the service account file")
    parser.add_argument('--model', '-m', type=str, default='gpt-3.5-turbo',
                        help="The model to use for OpenAI (default: gpt-3.5-turbo)")
    parser.add_argument('--prompt-override', '-p', type=str, default=DEFAULT_PROMPT,
                        help="Override the prompt to use for OpenAI")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    cleaner = SlideCleaner(args)
    cleaner.clean()
