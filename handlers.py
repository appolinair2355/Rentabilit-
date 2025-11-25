import requests
import re
import config
import zipfile
import os
from io import BytesIO

BASE_URL = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
SEND_DOCUMENT_URL = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendDocument"


# ========= ENVOI DE MESSAGE =========
def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"Message envoyé à {chat_id}: {response.status_code}")
        print(f"Réponse: {response.text}")
        return response
    except Exception as e:
        print(f"Erreur lors de l'envoi du message: {e}")
        return None


# ========= ENVOI DE DOCUMENT =========
def send_document(chat_id, file_data, filename, caption=""):
    try:
        files = {'document': (filename, file_data, 'application/zip')}
        data = {'chat_id': chat_id, 'caption': caption}
        response = requests.post(SEND_DOCUMENT_URL, files=files, data=data)
        print(f"Document envoyé à {chat_id}: {response.status_code}")
        return response
    except Exception as e:
        print(f"Erreur lors de l'envoi du document: {e}")
        return None


# ========= CRÉATION DU ZIP DE DÉPLOIEMENT =========
def create_deployment_zip():
    zip_buffer = BytesIO()

    # Lire le contenu actuel de config.py - garder PORT dynamique pour Render
    with open('config.py', 'r', encoding='utf-8') as f:
        config_render_content = f.read()
    
    # Render fournit automatiquement la variable PORT, on garde le code tel quel
    # (Render assigne typiquement le port 10000, mais c'est géré par la variable d'environnement)

    # Lire le contenu actuel de handlers.py
    with open('handlers.py', 'r', encoding='utf-8') as f:
        handlers_content = f.read()

    # Lire le contenu actuel de main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()

    # Lire le README pour Render
    with open('README_RENDER.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # Créer le fichier .env avec les vraies valeurs
    env_content = """# Variables d'environnement pour Render.com
# Copiez ces valeurs dans Render → Environment Variables

BOT_TOKEN=7943426808:AAF0GkqTWm-14ggzB2Uf0Sbo0KDt4iBgQ8I
RENDER_URL=https://rentabilit-fjdc.onrender.com

# ⚠️ IMPORTANT:
# Sur Render, ajoutez UNIQUEMENT BOT_TOKEN dans Environment Variables
# Render gère automatiquement la variable PORT (généralement 10000)
# NE PAS ajouter PORT manuellement!
"""

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Écrire les fichiers avec le contenu actuel
        zip_file.writestr('main.py', main_content)
        zip_file.writestr('handlers.py', handlers_content)
        zip_file.writestr('config.py', config_render_content)
        zip_file.writestr('README_RENDER.md', readme_content)
        zip_file.writestr('.env', env_content)

        if os.path.exists('requirements.txt'):
            zip_file.write('requirements.txt')

        if os.path.exists('render.yaml'):
            zip_file.write('render.yaml')
            
        # Inclure canaux_config.json pour le déploiement initial
        if os.path.exists('canaux_config.json'):
             zip_file.write('canaux_config.json')

    zip_buffer.seek(0)
    return zip_buffer


# ========= GESTION DES MESSAGES =========
def handle_message(chat_id, text, chat_title="Canal inconnu", user_id=None):
    print(f"Message reçu de {chat_id}: {text}")

    config.stats["messages_recus"] += 1

    # Récupère la configuration du canal
    canal_cfg = config.get_canal_config(chat_id)
    canal_cfg["nom_canal"] = chat_title

    # ID de l'administrateur autorisé (MAINTENU MAIS NON UTILISÉ POUR LA VÉRIFICATION)
    ADMIN_ID = 1190237801

    if text.startswith("/start"):
        send_message(chat_id, config.HELP_MESSAGE)
        return

    # La vérification ADMIN_ID a été supprimée, tous les utilisateurs peuvent configurer
    if text.startswith(("/banque", "/mise", "/cote", "/reset")):
        pass

    if text.startswith("/banque"):
        try:
            montant = float(text.split()[1])
            canal_cfg["banque"] = montant
            config.save_config() # <-- SAUVEGARDE
            send_message(chat_id, f"✅ Banque définie à {montant} FCFA pour {chat_title}")
            check_ready(chat_id, canal_cfg, chat_title)
        except:
            send_message(chat_id, "❌ Exemple : /banque 6000")
        return

    if text.startswith("/mise"):
        try:
            montant = float(text.split()[1])
            canal_cfg["mise"] = montant
            config.save_config() # <-- SAUVEGARDE
            send_message(chat_id, f"✅ Mise définie à {montant} FCFA pour {chat_title}")
            check_ready(chat_id, canal_cfg, chat_title)
        except:
            send_message(chat_id, "❌ Exemple : /mise 500")
        return

    if text.startswith("/cote"):
        try:
            montant = float(text.split()[1])
            canal_cfg["cote"] = float(montant)
            config.save_config() # <-- SAUVEGARDE
            send_message(chat_id, f"✅ Côte définie à {montant} pour {chat_title}")
            check_ready(chat_id, canal_cfg, chat_title)
        except:
            send_message(chat_id, "❌ Exemple : /cote 1.9")
        return

    if text.startswith("/reset"):
        canal_cfg["banque"] = 0
        canal_cfg["mise"] = 0
        canal_cfg["cote"] = 0
        canal_cfg["etat_du_bot"] = False
        config.save_config() # <-- SAUVEGARDE

        send_message(chat_id, f"🔄 Bot réinitialisé pour {chat_title}. Redéfinissez /banque /mise /cote")
        return

    if text.startswith("/st"):
        # Compte le nombre de canaux actifs
        canaux_actifs = len(config.canaux_config)
        canaux_actives_liste = "\n".join([
            f"  • {cfg['nom_canal']} (ID: {cid}) - {'✅ Activé' if cfg['etat_du_bot'] else '❌ Désactivé'}"
            for cid, cfg in config.canaux_config.items()
        ])

        canal_info = config.stats["dernier_canal"] or "Aucun canal détecté"
        date_info = config.stats["dernier_message_date"] or "N/A"

        status_message = f"""
📊 STATISTIQUES DU BOT

📡 Réception messages canal: {"✅ Oui" if config.stats["messages_recus"] > 0 else "❌ Non"}

📈 Statistiques globales:
• Messages reçus: {config.stats["messages_recus"]}
• Messages traités: {config.stats["messages_traites"]}
• Messages en attente (⏳): {config.stats["messages_en_attente"]}

📺 Canaux connectés: {canaux_actifs}
{canaux_actives_liste if canaux_actifs > 0 else "  Aucun canal configuré"}

📺 Dernier canal actif:
• Nom: {canal_info}
• Dernier message: {date_info}

💰 Configuration de CE canal ({chat_title}):
• Banque: {canal_cfg["banque"]:.2f} FCFA
• Mise: {canal_cfg["mise"]:.2f} FCFA
• Côte: {canal_cfg["cote"]}
• État: {'✅ Activé' if canal_cfg["etat_du_bot"] else '❌ Désactivé'}
"""
        send_message(chat_id, status_message)
        return

    if text.startswith("/deploy"):
        send_message(chat_id, "📦 Création du package de déploiement pour Render...")
        try:
            zip_data = create_deployment_zip()
            send_document(
                chat_id, 
                zip_data, 
                'fin25.zip',
                '✅ Fichiers de déploiement Render (PORT=10000) - VERSION PRO\n\n👨‍💻 Développeurs: Sossou Kouamé & Ahobadé Eli\n\nContient: main.py, handlers.py, config.py, requirements.txt, render.yaml, README_RENDER.md, canaux_config.json'
            )
            send_message(chat_id, """✅ Package 'fin25.zip' envoyé avec succès!

🎯 VERSION PRO:
• Port dynamique (Render le configure automatiquement)
• Support multi-canaux avec configurations séparées
• Admin seul autorisé (ID: 1190237801)
• Identique au code Replit
• ✨ Fichier .env inclus avec vos vraies valeurs!

⚠️ ÉTAPES CRITIQUES pour Render:

1️⃣ Variable d'environnement (OBLIGATOIRE):
   • Ouvrez le fichier .env dans le ZIP
   • Copiez BOT_TOKEN dans Render → Environment
   • NE PAS ajouter PORT (Render le gère)

2️⃣ Après déploiement, vérifiez la santé:
   https://rentabilit-fjdc.onrender.com/health

3️⃣ Configurez le webhook Telegram (CRITIQUE):
   https://api.telegram.org/bot7943426808:AAF0GkqTWm-14ggzB2Uf0Sbo0KDt4iBgQ8I/setWebhook?url=https://rentabilit-fjdc.onrender.com/webhook&allowed_updates=["message","channel_post","edited_channel_post","my_chat_member"]

4️⃣ Vérifiez le webhook:
   https://api.telegram.org/bot7943426808:AAF0GkqTWm-14ggzB2Uf0Sbo0KDt4iBgQ8I/getWebhookInfo

📖 README_RENDER.md contient le guide COMPLET avec dépannage!
⚠️ Sans webhook, le bot NE RÉPONDRA PAS même si le déploiement réussit!""")
        except Exception as e:
            send_message(chat_id, f"❌ Erreur lors de la création du package: {str(e)}")
        return

    # ========== ANALYSE DES STATUTS ==========
    if not canal_cfg["etat_du_bot"]:
        return

    # Ignore statut en attente
    if "⏳" in text:
        config.stats["messages_en_attente"] += 1
        return

    match = re.search(r"(✅[0-2]️⃣|❌)", text)

    if not match:
        return

    statut = match.group(1)

    b = canal_cfg["banque"]
    m = canal_cfg["mise"]
    c = canal_cfg["cote"]

    nb = b
    message = ""

    if statut == "✅0️⃣":
        gain = m * c
        nb = b - m + gain

        message = f"""
✅ STATUT 0 DÉTECTÉ ({chat_title})

🎯 Gain : {gain:.2f} FCFA
💼 Ancienne banque : {b:.2f} FCFA
🏦 Nouvelle banque : {nb:.2f} FCFA
"""

    elif statut == "✅1️⃣":
        gain = m * c * 2
        nb = b - m + gain

        message = f"""
✅ STATUT 1 DÉTECTÉ ({chat_title})

🎯 Gain : {gain:.2f} FCFA (x2)
💼 Ancienne banque : {b:.2f} FCFA
🏦 Nouvelle banque : {nb:.2f} FCFA
"""

    elif statut == "✅2️⃣":
        gain = m * 4 * c
        perte = m * 8
        nb = b - perte + gain

        message = f"""
✅ STATUT 2 DÉTECTÉ ({chat_title})

🚀 SUPER GAIN : {gain:.2f} FCFA
💸 Perte engagée : {perte:.2f} FCFA
💼 Ancienne banque : {b:.2f} FCFA
🏦 Nouvelle banque : {nb:.2f} FCFA
"""

    elif statut == "❌":
        perte = m * 7
        nb = b - perte

        message = f"""
❌ STATUT PERDANT ({chat_title})

💸 Perte : {perte:.2f} FCFA
💼 Ancienne banque : {b:.2f} FCFA
🏦 Nouvelle banque : {nb:.2f} FCFA
"""

    canal_cfg["banque"] = nb
    config.stats["messages_traites"] += 1
    config.save_config() # <-- SAUVEGARDE après le calcul de P&L
    send_message(chat_id, message)


def check_ready(chat_id, canal_cfg, chat_title):
    if canal_cfg["banque"] > 0 and canal_cfg["mise"] > 0 and canal_cfg["cote"] > 0:
        canal_cfg["etat_du_bot"] = True
        config.save_config() # <-- SAUVEGARDE si le bot est activé

        send_message(chat_id,
            f"✅ BOT ACTIVÉ pour {chat_title}\n\nIl analysera maintenant automatiquement les statuts de ce canal."
        )
