
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "VOTRE_TOKEN_ICI")

PORT = int(os.environ.get("PORT", 10000))

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
