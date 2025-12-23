"""
Flask app de test minimal pour les alertes email
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Server works!"})

@app.route('/api/alertes/TEST', methods=['POST'])
def test_alerte():
    """Route de test pour l'envoi d'email"""
    try:
        data = request.json
        email_dest = data.get('email', 'perfumeshabibi10@gmail.com')
        
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            return jsonify({"error": "Email non configuré"}), 500
        
        # Créer message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email_dest
        msg['Subject'] = "TEST - Alerte Étudiant"
        
        body = "Ceci est un test d'envoi d'email depuis le système."
        msg.attach(MIMEText(body, 'plain'))
        
        # Envoyer
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return jsonify({"message": f"Email TEST envoyé à {email_dest}"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Démarrage serveur de test...")
    print(f"Email configuré: {os.getenv('SENDER_EMAIL')}")
    app.run(debug=True, port=5001)  # Port différent pour tester
