import requests
import os
from dotenv import load_dotenv

load_dotenv() 

API_URL = "https://server-cjqd.onrender.com/api/send-all"
API_KEY = os.getenv("API_KEY")  # .env dosyasından al

def send_push_to_all(title, message):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
    }

    payload = {
        "title": title,
        "message": message,
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        print("✅ Bildirim gönderildi:", response.json())
    except requests.RequestException as e:
        print("❌ Hata oluştu:", e)

if __name__ == "__main__":
    print("Kullanılan API KEY:", API_KEY)
    print("🔥 Push Bildirimi Gönderici")
    title = "Haydi!!"
    message = "Bugunki görevini tamamla ve puan kazan!"
    send_push_to_all(title, message)
