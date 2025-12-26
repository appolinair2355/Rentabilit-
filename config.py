
import os
import json

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PORT = int(os.environ.get("PORT", 5000))

CONFIG_FILE = "canaux_config.json"

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

def load_config():
    """Charge la configuration depuis le fichier JSON"""
    global canaux_config
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convertir les clés en int (JSON les sauvegarde en string)
                canaux_config = {int(k): v for k, v in data.items()}
            print(f"✅ Configuration chargée: {len(canaux_config)} canaux")
        else:
            print("ℹ️ Aucune configuration existante, démarrage avec config vide")
    except Exception as e:
        print(f"⚠️ Erreur lors du chargement de la config: {e}")
        canaux_config = {}

def save_config():
    """Sauvegarde la configuration dans le fichier JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(canaux_config, f, ensure_ascii=False, indent=2)
        print(f"💾 Configuration sauvegardée: {len(canaux_config)} canaux")
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde de la config: {e}")

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
        save_config()
    return canaux_config[chat_id]

# Charger la configuration au démarrage
load_config()
