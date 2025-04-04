from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///push_tokens.db'
db = SQLAlchemy(app)

# Basit API key koruması
API_KEY = 'SECRET123'

@app.before_request
def check_api_key():
    if request.path.startswith('/api/'):  # sadece API route'larını kontrol et
        key = request.headers.get('x-api-key')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401

# Token modeli
class PushToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(200), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PushToken {self.user_id} - {self.token}>'

# Veritabanını oluştur
with app.app_context():
    db.create_all()

# Token kayıt endpointi
@app.route('/api/push-token', methods=['POST'])
def save_token():
    data = request.json
    user_id = data.get('userId')
    token = data.get('token')

    if not user_id or not token:
        return jsonify({'error': 'userId ve token gerekli'}), 400

    # Mevcut kullanıcı varsa güncelle
    existing = PushToken.query.filter_by(user_id=user_id).first()
    if existing:
        existing.token = token
        existing.updated_at = datetime.utcnow()
    else:
        new_token = PushToken(user_id=user_id, token=token)
        db.session.add(new_token)

    db.session.commit()
    return jsonify({'success': True}), 200

# Tüm tokenlara bildirim gönder
@app.route('/api/send-all', methods=['POST'])
def send_push_all():
    data = request.json
    title = data.get('title', '📣 Bildirim')
    message = data.get('message', 'Mesaj içeriği yok.')

    tokens = PushToken.query.all()
    for t in tokens:
        send_push(t.token, title, message)

    return jsonify({'sent': len(tokens)}), 200

# Expo push gönderici fonksiyon
def send_push(token, title, body):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "to": token,
        "sound": "default",
        "title": title,
        "body": body,
    }

    response = requests.post("https://exp.host/--/api/v2/push/send", json=payload, headers=headers)
    print(f"Sent to {token}: {response.status_code}")

# Anasayfa
@app.route('/')
def home():
    return '✅ Flask push notification backend is running.'

if __name__ == '__main__':
    app.run(debug=True)
