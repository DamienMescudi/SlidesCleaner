# SlidesCleaner
SlidesCleaner est un outil conçu pour simplifier la révision des textes dans vos présentations Google Slides. Utilisant l'API OpenAI, ce script Python corrige automatiquement les erreurs d'orthographe et de grammaire, vous permettant de vous concentrer sur le fond de votre présentation plutôt que sur la forme.

# Fonctionnalités
Correction automatique des fautes d'orthographe et de grammaire dans Google Slides.
Intégration transparente avec l'API OpenAI pour des corrections intelligentes et contextuelles.

# Technologies Utilisées
Python
Google Slides API
OpenAI API
Tkinter pour l'interface graphique

# Installation
Clonez le dépôt :
bash
Copy code
git clone https://github.com/DamienMescudi/SlidesCleaner
Installez les dépendances nécessaires :
bash
Copy code
pip install -r requirements.txt

# Configuration
_ Création d'un Compte de Service Google
Pour utiliser SlidesCleaner, vous devez configurer un compte de service Google :

_ Visitez Google Cloud Console et créez ou sélectionnez un projet.
Activez Google Slides API pour votre projet.
Créez un compte de service et téléchargez le fichier de clé JSON.
Placez le fichier de clé JSON dans le dossier du projet et renommez-le en credentials.json.
Configuration de l'API Key OpenAI
Obtenez une clé API d'OpenAI et ajoutez-la à un fichier config/settings.json sous la forme :
json
Copy code
{
    "openai_api_key": "VOTRE_CLÉ_API"
}

# Utilisation
Exécutez l'application via l'interface graphique en lançant le script :

bash
Copy code
python script.py

Ou executez SlidesCleaner.bat

Entrez l'ID de votre présentation Google Slides et le script corrigera le texte des diapositives.
