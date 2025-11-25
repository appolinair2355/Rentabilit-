

# 🚀 Guide de Déploiement sur Render.com

## ⚠️ PROBLÈME COURANT: Bot ne répond pas

Si votre bot est déployé avec succès mais ne répond pas, c'est probablement parce que:
1. ❌ Le `BOT_TOKEN` n'est pas configuré dans les variables d'environnement
2. ❌ Le webhook Telegram n'est pas configuré

**Suivez ce guide étape par étape pour corriger cela!**

---

## 📋 Étapes de déploiement

### 1️⃣ Créer un nouveau Web Service sur Render

1. Allez sur [render.com](https://render.com) et connectez-vous
2. Cliquez sur **"New"** → **"Web Service"**
3. Connectez votre repository GitHub ou uploadez le fichier ZIP

### 2️⃣ Configuration du Service

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python main.py
```

**Environment:**
- Sélectionnez **Python 3**

### 3️⃣ ⚠️ VARIABLES D'ENVIRONNEMENT (OBLIGATOIRE!)

**C'est l'étape la plus importante!**

Dans la section **"Environment"** de Render, cliquez sur **"Add Environment Variable"** et ajoutez:

| Key | Value | Exemple |
|-----|-------|---------|
| `BOT_TOKEN` | Votre token Telegram | `7943426808:AAF0GkqTWm-...` |

⚠️ **ATTENTION:** Render définit automatiquement la variable `PORT`. **NE L'AJOUTEZ PAS MANUELLEMENT!**

**Comment obtenir votre BOT_TOKEN:**

1. Ouvrez Telegram
2. Cherchez **@BotFather**
3. Envoyez `/mybots`
4. Sélectionnez votre bot
5. Cliquez sur **"API Token"**
6. **Copiez le token** (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
7. **Collez-le dans Render** comme valeur de `BOT_TOKEN`

**Vérification:**
- Seule variable à ajouter : `BOT_TOKEN`
- Render gère automatiquement : `PORT` (généralement 10000)

### 4️⃣ Déployer et récupérer l'URL

1. Cliquez sur **"Create Web Service"**
2. Attendez que le déploiement se termine (5-10 minutes)
3. Une fois terminé, **copiez votre URL Render** (ex: `https://votre-app.onrender.com`)

### 5️⃣ Configurer le Webhook Telegram (ÉTAPE CRITIQUE!)

**Sans cette étape, le bot ne recevra AUCUN message!**

#### Option A: Utiliser votre navigateur (RECOMMANDÉ)

Remplacez `<VOTRE_TOKEN>` et `<VOTRE_URL>` puis **ouvrez ce lien dans votre navigateur**:

```
https://api.telegram.org/bot<VOTRE_TOKEN>/setWebhook?url=<VOTRE_URL>/webhook&allowed_updates=["message","channel_post","edited_channel_post","my_chat_member"]
```

**Exemple concret:**
```
https://api.telegram.org/bot7943426808:AAF0GkqTWm-14ggzB2Uf0Sbo0KDt4iBgQ8I/setWebhook?url=https://mon-bot.onrender.com/webhook&allowed_updates=["message","channel_post","edited_channel_post","my_chat_member"]
```

**Réponse attendue:**
```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

#### Option B: Utiliser curl (pour utilisateurs avancés)

```bash
curl "https://api.telegram.org/bot<VOTRE_TOKEN>/setWebhook?url=<VOTRE_URL>/webhook&allowed_updates=[\"message\",\"channel_post\",\"edited_channel_post\",\"my_chat_member\"]"
```

### 6️⃣ Vérifier que le bot est en ligne

**Étape A: Vérifier la santé du bot**

Ouvrez cette URL dans votre navigateur (remplacez `<VOTRE_URL>`):

```
https://<VOTRE_URL>.onrender.com/health
```

**Vous devriez voir:**
```json
{
  "status": "healthy",
  "bot_username": "@votre_bot",
  "bot_id": 7943426808,
  "port": 10000
}
```

**Étape B: Vérifier le webhook Telegram**

Ouvrez ce lien dans votre navigateur (remplacez `<VOTRE_TOKEN>`):

```
https://api.telegram.org/bot<VOTRE_TOKEN>/getWebhookInfo
```

**Vous devriez voir:**
```json
{
  "ok": true,
  "result": {
    "url": "https://votre-app.onrender.com/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": 0
  }
}
```

**Si vous voyez `"pending_update_count": 0`** → ✅ **Tout fonctionne!**

---

## ✅ Test final

1. **Ajoutez le bot à un canal Telegram:**
   - Ouvrez votre canal
   - Cliquez sur le nom du canal → "Administrators"
   - "Add Administrator" → Cherchez votre bot → Ajoutez-le

2. **Le bot devrait envoyer un message de bienvenue automatiquement**

3. **Configurez le bot** (uniquement avec l'admin ID: 1190237801):
   ```
   /banque 5000
   /mise 500
   /cote 1.9
   ```

4. **Le bot devrait répondre et s'activer!** ✅

5. **Vérifiez les statistiques:**
   ```
   /st
   ```

---

## 🐛 Dépannage

### ❌ Le bot ne répond toujours pas

**Vérifiez dans l'ordre:**

1. **Endpoint de santé (NOUVEAU!):**
   - Ouvrez: `https://votre-app.onrender.com/health`
   - Si erreur 404 → Le bot n'a pas démarré
   - Si "unhealthy" → Problème avec BOT_TOKEN
   - Si "healthy" → ✅ Le bot fonctionne, passez à l'étape 3

2. **Variable d'environnement:**
   - Render → Votre service → "Environment"
   - Vérifiez que `BOT_TOKEN` est défini (et uniquement BOT_TOKEN!)
   - Si manquant, ajoutez-le et **Manual Deploy → Clear build cache & deploy**

3. **Logs du service:**
   - Render → Votre service → "Logs"
   - Cherchez `✅ Bot connecté avec succès: @votre_bot`
   - Si vous voyez `❌ ERREUR FATALE: BOT_TOKEN invalide` → Corrigez le token
   - Si le service redémarre en boucle → Vérifiez les logs pour l'erreur exacte

4. **Webhook (CRITIQUE!):**
   - Ouvrez: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
   - Vérifiez que `url` = `https://votre-app.onrender.com/webhook`
   - Si `url` est vide ou différent → Refaites l'étape 5️⃣
   - Si `last_error_date` > 0 → Cliquez sur le lien pour voir l'erreur

5. **Permissions du bot:**
   - Le bot doit être **administrateur** du canal
   - Permissions requises: "Post messages", "Delete messages", "Read messages"

6. **Test final:**
   - Ajoutez le bot à un canal → Il devrait envoyer un message de bienvenue
   - Envoyez `/start` en privé → Il devrait répondre
   - Si rien ne se passe → Retour à l'étape 1

### ❌ Erreur "Unauthorized" (401)

→ Votre `BOT_TOKEN` est **incorrect ou manquant**
- Vérifiez la variable d'environnement sur Render
- Obtenez un nouveau token avec @BotFather si nécessaire

### ❌ Erreur "Bad Request: wrong webhook URL"

→ Votre URL Render est incorrecte
- Vérifiez que l'URL se termine par `/webhook`
- Format correct: `https://votre-app.onrender.com/webhook`

---

## 📊 Commandes disponibles

Une fois le bot configuré:

- `/start` → Afficher les commandes
- `/banque 6000` → Définir banque (admin uniquement)
- `/mise 500` → Définir mise (admin uniquement)
- `/cote 1.9` → Définir cote (admin uniquement)
- `/reset` → Réinitialiser bot (admin uniquement)
- `/st` → Afficher statistiques
- `/deploy` → Télécharger fichiers de déploiement

---

## 👨‍💻 Développeurs

- **Sossou Kouamé**
- **Ahobadé Eli**

**VERSION PRO** - Support multi-canaux avec configurations séparées par canal

---

## 📞 Besoin d'aide?

Si le bot ne fonctionne toujours pas après avoir suivi ce guide:

1. Vérifiez les logs Render pour voir les erreurs exactes
2. Testez le webhook avec `getWebhookInfo`
3. Assurez-vous que le BOT_TOKEN est bien défini dans les variables d'environnement

**Le problème est TOUJOURS l'un de ces trois points!**

