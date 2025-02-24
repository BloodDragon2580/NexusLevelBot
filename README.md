# 🎮 Discord XP & Level Bot (Nextcord)

Ein Discord-Bot auf **Python-Basis mit nextcord**, der XP und Level für Nachrichten und Sprachaktivitäten vergibt.  
✅ **XP für Nachrichten & Sprachchat**  
✅ **Level-Up mit Benachrichtigung**  
✅ **Slash-Commands (`/level` & `/info`)**  
✅ **XP-Verlust nach 7 Tagen Inaktivität**  
✅ **Maximales Level von 100**  
✅ **Copyright: `© Nexus Gaming`**  

---

## 📌 1. Bot im Discord Developer Portal erstellen  

1. Gehe auf [Discord Developer Portal](https://discord.com/developers/applications)  
2. Klicke auf **"New Application"** und gib einen Namen ein  
3. Gehe zum Tab **"Bot"** und klicke auf **"Add Bot"**  
4. **Kopiere den Token** (brauchen wir später für den Code)  
5. **Aktiviere diese Intents:**  
   - ✅ `MESSAGE CONTENT INTENT`  
   - ✅ `SERVER MEMBERS INTENT`  
   - ✅ `PRESENCE INTENT`  

6. Gehe zum Tab **OAuth2 > URL Generator**  
   - Wähle **"bot"** und **"applications.commands"**  
   - Setze diese Berechtigungen:  
     ✅ `Send Messages`  
     ✅ `Read Messages`  
     ✅ `Use Slash Commands`  
     ✅ `Connect` & `Speak` (für Voice-Tracking)  
   - Kopiere die generierte URL und füge den Bot zu deinem Server hinzu  

---

## 📌 2. Benötigte Pakete installieren  

Öffne das Terminal oder die Eingabeaufforderung und installiere die notwendigen Python-Bibliotheken:  

```sh
pip install nextcord pynacl
```

Falls `pip` nicht erkannt wird, versuche:  
```sh
python -m pip install nextcord pynacl
```
---

## 📌 3. Bot starten  
Öffne das Terminal im Verzeichnis, wo sich `bot.py` befindet, und starte den Bot mit:  
```sh
python bot.py
```

Falls du Fragen hast oder Erweiterungen möchtest, sag einfach Bescheid!
