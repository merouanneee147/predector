"""
Script de Test - Envoi d'Email Réel
Teste l'envoi d'emails avec la configuration Gmail
"""
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Charger les variables d'environnement
load_dotenv()

def test_email():
    """Teste l'envoi d'un email"""
    
    # Configuration depuis .env
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    email_service = os.getenv('EMAIL_SERVICE', 'gmail')
    
    print("=" * 60)
    print("TEST D'ENVOI D'EMAIL")
    print("=" * 60)
    print(f"Service: {email_service}")
    print(f"From: {sender_email}")
    print(f"Password configuré: {'Oui' if sender_password else 'Non'}")
    print()
    
    if not sender_email or not sender_password:
        print("❌ Configuration email manquante dans .env")
        return False
    
    # Demander l'email de test
    test_recipient = input("Email destinataire pour le test (ou Enter pour envoyer à l'expéditeur): ").strip()
    if not test_recipient:
        test_recipient = sender_email
    
    print(f"\n📧 Envoi d'un email de test à: {test_recipient}")
    print("-" * 60)
    
    try:
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Soutien Pédagogique <{sender_email}>"
        msg['To'] = test_recipient
        msg['Subject'] = "🎓 Test - Système de Soutien Pédagogique"
        
        # Corps HTML
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center;">
                    <h1 style="color: white; margin: 0;">✅ Email de Test Réussi !</h1>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; margin-top: 20px; border-radius: 10px;">
                    <h2 style="color: #667eea;">Système de Soutien Pédagogique</h2>
                    <p>Ceci est un email de test pour confirmer que le système d'envoi d'alertes fonctionne correctement.</p>
                    
                    <div style="background: white; padding: 20px; border-left: 4px solid #667eea; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #667eea;">📊 Configuration</h3>
                        <ul>
                            <li><strong>Service:</strong> Gmail</li>
                            <li><strong>Expéditeur:</strong> """ + sender_email + """</li>
                            <li><strong>Status:</strong> ✅ Opérationnel</li>
                        </ul>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0;"><strong>💡 Note:</strong> Les emails réels sont maintenant activés. Les alertes pour les étudiants à risque seront envoyées automatiquement.</p>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                        Ce message a été envoyé via le système de soutien pédagogique.<br>
                        Si vous recevez cet email, la configuration fonctionne parfaitement ! 🎉
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Configuration SMTP Gmail
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        
        print("Connexion au serveur SMTP...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        print("Authentification...")
        server.login(sender_email, sender_password)
        
        print("Envoi de l'email...")
        server.send_message(msg)
        server.quit()
        
        print("\n" + "=" * 60)
        print("✅ EMAIL ENVOYÉ AVEC SUCCÈS !")
        print("=" * 60)
        print(f"📬 Vérifiez la boîte de réception de: {test_recipient}")
        print("💡 Vérifiez aussi les spams si vous ne le voyez pas.")
        print()
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ ERREUR D'AUTHENTIFICATION")
        print("Vérifiez:")
        print("1. Adresse email correcte")
        print("2. Mot de passe d'application valide (pas le mot de passe Gmail normal)")
        print("3. Validation en 2 étapes activée sur Gmail")
        return False
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    test_email()
