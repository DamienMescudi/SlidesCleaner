
# SlidesCleaner (avec l'API ChatGPT)
SlidesCleaner est un outil conçu pour simplifier la révision des textes dans vos présentations Google Slides. Utilisant l'API OpenAI, ce script Python corrige automatiquement les erreurs d'orthographe et de grammaire, vous permettant de vous concentrer sur le fond de votre présentation plutôt que sur la forme.


## Fonctionnalités
- Correction automatique des fautes d'orthographe et de grammaire dans Google Slides.
- Intégration transparente avec l'API OpenAI pour des corrections intelligentes et contextuelles.
- Option de correction automatique sans validation manuelle via l'interface de ligne de commande (CLI).

## Pré-requis
- Python
- Token OpenAI
- Compte Google Cloud Platform (L'utilisation de l'API Google Slides étant gratuite)

## Installation
Clonez le dépôt :

```bash
git clone https://github.com/DamienMescudi/SlidesCleaner
```

Installez les dépendances nécessaires :

```bash
pip install -r requirements.txt
```

## Configuration

### Création d'un Compte de Service Google
Pour utiliser SlidesCleaner, vous devez configurer un compte de service Google :

1. Visitez [Google Cloud Console](https://console.cloud.google.com/) et créez ou sélectionnez un projet.
2. Activez Google Slides API pour votre projet.
3. Créez un compte de service et téléchargez le fichier de clé JSON.
4. Placez le fichier de clé JSON dans le dossier config du projet et renommez-le en `credentials.json`.

### Configuration de l'API Key OpenAI
Obtenez une clé API d'OpenAI et ajoutez-la à un fichier `config/settings.json` sous la forme :

```json
{
    "openai_api_key": "VOTRE_CLÉ_API"
}
```

## Utilisation
Exécutez le script via l'interface de ligne de commande (CLI) en utilisant :

```bash
python main.py [ID_PRÉSENTATION]
```

`--auto-correct` - Pour corriger automatiquement (Risque d'incompréhenssion - Exemple : "Salut les copins" peut devenir "Salut les copains" au lieu de "Salut les copines".)
`--guivalid` - Pour valider avec une interface graphique (Sinon validation en CLI)
`--model` - Pour sélectionner un model parmi ceux proposé par [OpenAi](https://console.cloud.google.com/)


