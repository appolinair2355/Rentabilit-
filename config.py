import os
import json
from os import path

# Nom du fichier de persistance pour les configurations de canaux
CONFIG_FILE = "canaux_config.json"

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PORT = int(os.environ.get("PORT", 5000))

# Configuration multi-canaux : dictionnaire par chat_id
canaux_config = {}

stats = {
    "messages_recus": 0,
    "messages_traites": 0,
    "messages_en_attente": 0,
    "dernier_canal": None,
    "dernier_message_date": None
}

HELP_MESSAGE = """
🤖 BOT DE RENTABILITÉ (VERSION PRO)

/start → Afficher les commandes
/banque 6000 → Définir banque
/mise 500 → Définir mise
/cote 1.9 → Définir cote
/reset → Réinitialiser bot
/st → Afficher les statistiques du bot
/deploy → Télécharger fichiers de déploiement
"""

# ========= FONCTIONS DE PERSISTANCE JSON =========

def load_config():
    """Charge la configuration des canaux depuis le fichier JSON."""
    global canaux_config
    if path.exists(CONFIG_FILE):
        print(f"Chargement de la configuration depuis {CONFIG_FILE}...")
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convertit les clés string en int (car les IDs de chat sont des nombres)
                canaux_config.update({int(k) if str(k).lstrip('-').isdigit() else k: v for k, v in data.items()})
            print("Configuration chargée avec succès.")
        except Exception as e:
            print(f"❌ Erreur lors du chargement de la configuration: {e}")
            # En cas d'erreur de lecture (ex: JSON invalide), démarre avec une config vide
            canaux_config = {}
    else:
        print(f"⚠️ Fichier {CONFIG_FILE} non trouvé. Démarrage avec une configuration vide.")


def save_config():
    """Sauvegarde la configuration des canaux dans le fichier JSON."""
    try:
        # Convertit les clés int en string pour l'écriture JSON
        data_to_save = {str(k): v for k, v in canaux_config.items()}
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        print(f"Configuration sauvegardée dans {CONFIG_FILE}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde de la configuration: {e}")

# ========= GESTION DE LA CONFIGURATION EN MÉMOIRE =========

def get_canal_config(chat_id):
    """Récupère ou crée la configuration pour un canal"""
    if chat_id not in canaux_config:
        canaux_config[chat_id] = {
            "banque": 0,
            "mise": 0,
            "cote": 0,
            "etat_du_bot": False,
            "nom_canal": "Canal inconnu"
        }
    return canaux_config[chat_id]

# Charge la configuration au démarrage
load_config()
        
