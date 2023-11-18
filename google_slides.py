from googleapiclient.discovery import build
from google.oauth2 import service_account

def authenticate_google_api(service_account_file):
    creds = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/presentations']
    )
    service = build('slides', 'v1', credentials=creds)
    return service

def get_presentation_text(service, presentation_id):
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    text_elements = []
    slide_number = 0  # Initialiser le compteur de slides

    for slide in presentation.get('slides', []):
        slide_number += 1  # Incrémenter le numéro de la slide
        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                element_id = element['objectId']
                text_content = ''
                for text_run in element['shape']['text']['textElements']:
                    if 'textRun' in text_run:
                        text_content += text_run['textRun']['content']
                text_elements.append((element_id, text_content, slide_number))  # Utiliser slide_number ici
    return text_elements



def update_slide_text(service, presentation_id, element_id, new_text):
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
