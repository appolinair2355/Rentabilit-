from flask import Flask, request
import requests
from handlers import handle_message, send_message
from config import PORT, BOT_TOKEN

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot de rentabilité actif - Version PRO"

@app.route("/health", methods=["GET"])
def health():
    """Endpoint de santé pour vérifier l'état du bot"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=5)
        if response.status_code == 200:
            bot_info = response.json()
            return {
                "status": "healthy",
                "bot_username": bot_info['result']['username'],
                "bot_id": bot_info['result']['id'],
                "port": PORT
            }
        else:
            return {"status": "unhealthy", "error": "Invalid token"}, 500
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print(f"📨 Webhook reçu: {list(data.keys())}")
    except Exception as e:
        print(f"❌ Erreur parsing JSON webhook: {e}")
        return {"status": "error", "message": "Invalid JSON"}, 400

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        chat_title = message["chat"].get("title", message["chat"].get("first_name", "Utilisateur"))
        text = message.get("text", "")
        user_id = message["from"]["id"]
        handle_message(chat_id, text, chat_title, user_id)
    
    if "channel_post" in data:
        channel_post = data["channel_post"]
        chat_id = channel_post["chat"]["id"]
        chat_title = channel_post["chat"].get("title", "Canal inconnu")
        text = channel_post.get("text", "")
        user_id = channel_post.get("from", {}).get("id")
        
        import config
        from datetime import datetime
        config.stats["dernier_canal"] = chat_title
        config.stats["dernier_message_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        handle_message(chat_id, text, chat_title, user_id)
    
    if "edited_channel_post" in data:
        edited_post = data["edited_channel_post"]
        chat_id = edited_post["chat"]["id"]
        chat_title = edited_post["chat"].get("title", "Canal inconnu")
        text = edited_post.get("text", "")
        user_id = edited_post.get("from", {}).get("id")
        
        import config
        from datetime import datetime
        config.stats["dernier_canal"] = chat_title
        config.stats["dernier_message_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Message édité dans {chat_title}: {text}")
        handle_message(chat_id, text, chat_title, user_id)
    
    if "my_chat_member" in data:
        from handlers import send_message
        chat_member = data["my_chat_member"]
        chat = chat_member["chat"]
        new_status = chat_member["new_chat_member"]["status"]
        
        if new_status in ["member", "administrator"]:
            chat_id = chat["id"]
            chat_title = chat.get("title", "ce canal")
            
            welcome_message = f"""
✅ Bot de Rentabilité VERSION PRO activé dans {chat_title}!

🤖 Je suis maintenant connecté et prêt à analyser les messages du canal.

📊 Je vais lire automatiquement tous les messages et analyser les statuts de paris pour calculer votre rentabilité.

👨‍💻 **Développeurs :**
• Sossou Kouamé
• Ahobadé Eli

⚙️ **Configuration (ADMIN uniquement) :**
Seul l'administrateur autorisé peut configurer les canaux avec :
/banque - Définir votre banque
/mise - Définir votre mise
/cote - Définir la cote

📌 **VERSION PRO** - Multi-canaux avec configurations séparées

Le bot est maintenant en écoute! 👂
"""
            send_message(chat_id, welcome_message)

    return {"status": "ok"}


if __name__ == "__main__":
    print("=" * 60)
    print(f"🚀 Démarrage du bot sur le port {PORT}")
    print("=" * 60)
    
    # VÉRIFICATION CRITIQUE: Token valide AVANT de démarrer Flask
    if not BOT_TOKEN or len(BOT_TOKEN) < 20:
        print("\n❌ ERREUR FATALE: BOT_TOKEN invalide ou manquant!")
        print(f"Token actuel: '{BOT_TOKEN[:10]}...' (longueur: {len(BOT_TOKEN)})")
        print("\n🔧 Configuration requise:")
        print("   • Sur Render: Ajoutez BOT_TOKEN dans Environment Variables")
        print("   • Sur Replit: Ajoutez BOT_TOKEN dans Secrets")
        print("\n📖 Consultez README_RENDER.md pour les instructions détaillées")
        print("=" * 60)
        import sys
        sys.exit(1)
    
    print(f"🔑 Token détecté: {BOT_TOKEN[:15]}...{BOT_TOKEN[-10:]}")
    
    # Vérifier la connexion avec l'API Telegram
    try:
        print("🔄 Vérification de la connexion à Telegram...")
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                print(f"✅ Bot connecté avec succès: @{bot_info['result']['username']}")
                print(f"   ID: {bot_info['result']['id']}")
                print(f"   Nom: {bot_info['result']['first_name']}")
            else:
                print(f"❌ Réponse invalide de Telegram: {bot_info}")
                import sys
                sys.exit(1)
        elif response.status_code == 401:
            print(f"\n❌ ERREUR: Token non autorisé (401)")
            print(f"   Le BOT_TOKEN '{BOT_TOKEN[:15]}...' est invalide")
            print(f"   Obtenez un nouveau token avec @BotFather sur Telegram")
            import sys
            sys.exit(1)
        else:
            print(f"❌ Erreur API Telegram ({response.status_code}): {response.text}")
            import sys
            sys.exit(1)
            
    except requests.exceptions.Timeout:
        print("⚠️ Timeout lors de la connexion à Telegram (réseau lent?)")
        print("   Le bot va démarrer mais vérifiez votre connexion réseau")
    except Exception as e:
        print(f"⚠️ Impossible de vérifier le bot: {e}")
        print("   Le bot va démarrer quand même, mais vérifiez votre configuration")
    
    print(f"\n⚠️ IMPORTANT: Configurez le webhook après déploiement!")
    print(f"📖 Consultez README_RENDER.md pour les instructions")
    print("=" * 60)
    print(f"\n🌐 Démarrage du serveur Flask sur 0.0.0.0:{PORT}...\n")
    
    app.run(host="0.0.0.0", port=PORT)
