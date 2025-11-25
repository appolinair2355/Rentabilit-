from flask import Flask, request
import requests
from handlers import handle_message, send_message
from config import PORT, BOT_TOKEN

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot de rentabilité actif - Version PRO"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

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
        
        import config
        from datetime import datetime
        config.stats["dernier_canal"] = chat_title
        config.stats["dernier_message_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        handle_message(chat_id, text, chat_title)
    
    if "edited_channel_post" in data:
        edited_post = data["edited_channel_post"]
        chat_id = edited_post["chat"]["id"]
        chat_title = edited_post["chat"].get("title", "Canal inconnu")
        text = edited_post.get("text", "")
        
        import config
        from datetime import datetime
        config.stats["dernier_canal"] = chat_title
        config.stats["dernier_message_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Message édité dans {chat_title}: {text}")
        handle_message(chat_id, text, chat_title)
    
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
    print(f"Bot lancé sur le port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
