# -*- coding: utf-8 -*-
"""
🚀 API Flask - Système de Recommandation de Soutien Pédagogique
================================================================
Backend API pour l'interface React
Avec Base de Données SQLite + Assistant IA OpenAI
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import secrets
import json
from functools import wraps
from io import BytesIO

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importer le module de base de données
from database import Database

# Importer l'assistant IA OpenAI
from openai_assistant import AssistantIA

app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin depuis React

# =============================================================================
# INITIALISATION DE LA BASE DE DONNÉES SQLite
# =============================================================================
db = Database()
print("✅ Base de données SQLite initialisée")

# Créer les utilisateurs par défaut s'ils n'existent pas
def init_default_users():
    """Initialise les utilisateurs par défaut dans la base de données"""
    users = [
        ('admin', 'admin123', 'admin@universite.ma', 'admin', 'Administrateur', 'Système'),
        ('enseignant', 'prof123', 'prof@universite.ma', 'enseignant', 'Test', 'Professeur'),
        ('tuteur', 'tuteur123', 'tuteur@universite.ma', 'tuteur', 'Pédagogique', 'Tuteur')
    ]
    
    for username, password, email, role, nom, prenom in users:
        existing = db.get_user_by_username(username)
        if not existing:
            db.create_user(username, password, email, role, nom, prenom)
            print(f"   👤 Utilisateur créé: {username} ({role})")
        else:
            print(f"   👤 Utilisateur existant: {username}")

init_default_users()

# =============================================================================
# CONFIGURATION EMAIL - MULTIPLE SERVICES SUPPORTÉS
# =============================================================================
# Services supportés: Gmail, Outlook, Yahoo, Brevo, Mailtrap, ou simulation

EMAIL_SERVICES = {
    'gmail': {'server': 'smtp.gmail.com', 'port': 587},
    'outlook': {'server': 'smtp-mail.outlook.com', 'port': 587},
    'yahoo': {'server': 'smtp.mail.yahoo.com', 'port': 587},
    'brevo': {'server': 'smtp-relay.brevo.com', 'port': 587},
    'mailtrap': {'server': 'sandbox.smtp.mailtrap.io', 'port': 587},
}

# Mode simulation activé par défaut (pas besoin de credentials)
EMAIL_SIMULATION_MODE = os.environ.get('EMAIL_SIMULATION', 'true').lower() == 'true'

EMAIL_CONFIG = {
    'service': os.environ.get('EMAIL_SERVICE', 'gmail'),
    'sender_email': os.environ.get('SENDER_EMAIL', 'noreply@soutien-pedagogique.ma'),
    'sender_password': os.environ.get('SENDER_PASSWORD', ''),
    'sender_name': 'Système de Soutien Pédagogique'
}

# =============================================================================
# SYSTÈME D'AUTHENTIFICATION JWT AVEC SQLite
# =============================================================================
# Clé secrète pour JWT (en production, utiliser une variable d'environnement)
JWT_SECRET = os.environ.get('JWT_SECRET', 'soutien-pedagogique-secret-key-2025')
JWT_EXPIRATION_HOURS = 24

def generate_token(username: str) -> str:
    """Génère un token d'authentification et le stocke dans la BDD"""
    token = secrets.token_urlsafe(32)
    expiration = datetime.now() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    # Récupérer l'ID utilisateur
    user = db.get_user_by_username(username)
    if user:
        db.create_session(user['id'], token, expiration.isoformat())
    
    return token

def verify_token(token: str) -> dict:
    """Vérifie et retourne les infos du token depuis la BDD"""
    session = db.validate_session(token)
    if not session:
        return None
    
    # Récupérer l'utilisateur
    user = db.get_user_by_id(session['user_id'])
    if not user:
        return None
    
    return {
        'username': user['username'],
        'user': user,
        'expires': session['expires_at'],
        'created': session['created_at']
    }

def require_auth(f):
    """Décorateur pour protéger les routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token manquant'}), 401
        
        token = auth_header.replace('Bearer ', '')
        session = verify_token(token)
        
        if not session:
            return jsonify({'error': 'Token invalide ou expiré'}), 401
        
        request.current_user = session['user']
        request.username = session['username']
        return f(*args, **kwargs)
    return decorated

def require_role(*roles):
    """Décorateur pour vérifier le rôle"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Non authentifié'}), 401
            if request.current_user['role'] not in roles and 'admin' not in roles:
                if request.current_user['role'] != 'admin':
                    return jsonify({'error': 'Permission insuffisante'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def send_email(to_email: str, subject: str, html_content: str) -> dict:
    """
    Envoie un email via SMTP ou simule l'envoi
    Retourne un dict avec status et détails
    """
    email_record = {
        'id': 0,
        'to': to_email,
        'subject': subject,
        'timestamp': datetime.now().isoformat(),
        'status': 'pending'
    }
    
    # Mode simulation - enregistre l'email sans l'envoyer réellement
    if EMAIL_SIMULATION_MODE or not EMAIL_CONFIG['sender_password']:
        email_record['status'] = 'simulated'
        email_record['message'] = f"📧 Email simulé vers {to_email}"
        # Logger dans la BDD
        db.log_email(to_email, subject, 'simulated', 'simulation', email_record['message'])
        print(f"📧 [SIMULATION] Email vers {to_email}: {subject}")
        return {'success': True, 'mode': 'simulation', 'record': email_record}
    
    # Mode réel - envoi SMTP
    try:
        service = EMAIL_SERVICES.get(EMAIL_CONFIG['service'], EMAIL_SERVICES['gmail'])
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['sender_email']}>"
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        with smtplib.SMTP(service['server'], service['port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.sendmail(EMAIL_CONFIG['sender_email'], to_email, msg.as_string())
        
        email_record['status'] = 'sent'
        email_record['message'] = f"✅ Email envoyé à {to_email}"
        db.log_email(to_email, subject, 'sent', 'smtp', email_record['message'])
        print(f"✅ Email envoyé à {to_email}")
        return {'success': True, 'mode': 'smtp', 'record': email_record}
        
    except smtplib.SMTPAuthenticationError:
        email_record['status'] = 'auth_error'
        email_record['message'] = "Erreur d'authentification SMTP"
        db.log_email(to_email, subject, 'auth_error', 'smtp', email_record['message'])
        print(f"❌ Erreur d'authentification SMTP")
        return {'success': False, 'mode': 'smtp', 'error': 'auth_error'}
        
    except Exception as e:
        email_record['status'] = 'error'
        email_record['message'] = str(e)
        db.log_email(to_email, subject, 'error', 'smtp', str(e))
        print(f"❌ Erreur envoi email: {e}")
        return {'success': False, 'mode': 'smtp', 'error': str(e)}


# =============================================================================
# ENDPOINT POUR VOIR LES EMAILS ENVOYÉS
# =============================================================================
@app.route('/api/emails/log', methods=['GET'])
def get_email_log():
    """Retourne l'historique des emails envoyés/simulés depuis SQLite"""
    emails = db.get_emails_log(50)
    return jsonify({
        'mode': 'simulation' if EMAIL_SIMULATION_MODE else 'smtp',
        'total': len(emails),
        'emails': emails
    })


@app.route('/api/emails/test', methods=['POST'])
def test_email():
    """Endpoint de test pour vérifier l'envoi d'email"""
    data = request.get_json() or {}
    email = data.get('email', 'test@example.com')
    
    result = send_email(
        to_email=email,
        subject="🧪 Test - Système de Soutien Pédagogique",
        html_content="""
        <div style="font-family: Arial, sans-serif; padding: 20px; background: #f0f9ff; border-radius: 10px;">
            <h1 style="color: #1e40af;">✅ Test Email Réussi!</h1>
            <p>Si vous voyez ce message, le système d'envoi d'emails fonctionne correctement.</p>
            <p><strong>Mode:</strong> {mode}</p>
            <p><strong>Date:</strong> {date}</p>
        </div>
        """.format(
            mode='Simulation' if EMAIL_SIMULATION_MODE else 'SMTP Réel',
            date=datetime.now().strftime('%d/%m/%Y %H:%M')
        )
    )
    
    return jsonify({
        'success': result['success'],
        'mode': result['mode'],
        'message': f"Email {'simulé' if result['mode'] == 'simulation' else 'envoyé'} vers {email}",
        'simulation_note': "Mode simulation actif - les emails sont enregistrés mais pas envoyés réellement" if EMAIL_SIMULATION_MODE else None
    })


# Chemins
BASE_PATH = Path(__file__).parent.parent
RAW_PATH = BASE_PATH / "raw"
OUTPUT_PATH = BASE_PATH / "output_projet4"
MODEL_PATH = OUTPUT_PATH / "model_soutien_pedagogique.joblib"

# Variables globales
df = None
model_data = None

# Dictionnaire de traduction
TRADUCTION_MODULES = {
    'الكيمياء الصناعية': 'Chimie Industrielle',
    'مبادئ حواسيب': 'Principes Informatiques',
    'لغة انكليزية 2': 'Anglais 2',
    'لغة انكليزية 1': 'Anglais 1',
    'رياضيات 2': 'Mathematiques 2',
    'رياضيات 1': 'Mathematiques 1',
    'رياضيات 3': 'Mathematiques 3',
    'رياضيات 4': 'Mathematiques 4',
    'الفيزياء الحديثة': 'Physique Moderne',
    'الفيزياء العامة': 'Physique Generale',
    'اللغة العربية': 'Langue Arabe',
    'الورش الكهربائية والالكترونية': 'Ateliers Electriques et Electroniques',
    'تحكم حديث': 'Controle Moderne',
    'التحليل الرياضي': 'Analyse Mathematique',
    'التحليل العددي': 'Analyse Numerique',
    'نظرية الدارات الكهربائية': 'Theorie des Circuits Electriques',
    'الخوارزميات وبنى المعطيات': 'Algorithmes et Structures de Donnees',
    'هندسة الكترونية': 'Genie Electronique',
    'الجبر الخطي': 'Algebre Lineaire',
    'برمجة': 'Programmation',
    'الآلات الكهربائية': 'Machines Electriques',
    'الدارات الالكترونية': 'Circuits Electroniques',
    'الرسم الهندسي': 'Dessin Technique',
    'إشارات ونظم': 'Signaux et Systemes',
    'مبادئ الاتصالات': 'Principes Telecommunications',
    'Unknown': 'Inconnu'
}

def traduire_module(nom):
    """Traduit le nom du module"""
    for ar, fr in TRADUCTION_MODULES.items():
        if ar in str(nom):
            return fr
    return nom

def load_data():
    """Charge les données et le modèle"""
    global df, model_data
    
    print("📊 Chargement des données...")
    df1 = pd.read_csv(RAW_PATH / "1- one_clean.csv", encoding='utf-8')
    df2 = pd.read_csv(RAW_PATH / "2- two_clean.csv", encoding='utf-8')
    df = pd.concat([df1, df2], ignore_index=True)
    
    # Nettoyage complet - supprimer tous les Unknown et null
    taille_avant = len(df)
    
    # Supprimer les lignes avec ID null ou Unknown
    df['ID'] = df['ID'].astype(str)
    df = df[~df['ID'].isin(['Unknown', 'unknown', 'nan', 'None', ''])].copy()
    
    # Supprimer les lignes avec Major Unknown
    df = df[~df['Major'].astype(str).str.lower().str.contains('unknown', na=False)].copy()
    
    # Supprimer les lignes avec Subject Unknown
    df = df[~df['Subject'].astype(str).str.lower().str.contains('unknown', na=False)].copy()
    
    print(f"   • Enregistrements nettoyés: {taille_avant - len(df):,} supprimés")
    
    # Renommer colonnes
    df = df.rename(columns={
        'Major': 'Filiere', 
        'Subject': 'Module', 
        'MajorYear': 'Annee', 
        'OfficalYear': 'AnneUniversitaire'
    })
    
    df['Practical'] = pd.to_numeric(df['Practical'], errors='coerce').fillna(0)
    df['Theoretical'] = pd.to_numeric(df['Theoretical'], errors='coerce').fillna(0)
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(df['Practical'] + df['Theoretical'])
    df['Note_sur_20'] = df['Total'] / 5
    df['Annee'] = pd.to_numeric(df['Annee'], errors='coerce').fillna(1).astype(int)
    df['Semester'] = pd.to_numeric(df['Semester'], errors='coerce').fillna(1).astype(int)
    
    df['Needs_Support'] = ((df['Status'] == 'Fail') | 
                           (df['Total'] < 50) | 
                           (df['Status'].isin(['Absent', 'Debarred', 'Withdrawal']))).astype(int)
    
    print(f"✅ {len(df):,} enregistrements chargés")
    
    # Charger le modèle ML
    global model_data
    if MODEL_PATH.exists():
        model_data = joblib.load(MODEL_PATH)
        print("✅ Modèle chargé")
    else:
        model_data = None
        print("⚠️ Modèle non trouvé")
    
    # Initialiser l'assistant IA avec les données
    global assistant_ia
    
    # Utiliser la version simulée (gratuite et fonctionnelle)
    try:
        from openai_assistant_simule import AssistantIASimule
        assistant_ia = AssistantIASimule(df=df)
        print("✅ Assistant IA Simulé activé (gratuit - aucune API requise)")
    except Exception as e:
        print(f"❌ Assistant IA non disponible: {e}")
        assistant_ia = None
    
    # Si vous avez une clé OpenAI valide, décommentez ci-dessous:
    # try:
    #     from openai_assistant import AssistantIA
    #     assistant_ia = AssistantIA(df=df)
    #     print("🤖 Assistant IA OpenAI initialisé")
    # except Exception as e:
    #     print(f"⚠️ OpenAI non disponible ({e})")
    #     from openai_assistant_simule import AssistantIASimule
    #     assistant_ia = AssistantIASimule(df=df)
    #     print("✅ Assistant IA Simulé activé (gratuit)")

def get_profil(moyenne):
    """Retourne le profil basé sur la moyenne"""
    if moyenne >= 14:
        return {"nom": "Excellence", "emoji": "⭐", "color": "gold", "level": 5}
    elif moyenne >= 12:
        return {"nom": "Régulier", "emoji": "🟢", "color": "green", "level": 4}
    elif moyenne >= 10:
        return {"nom": "En Progression", "emoji": "🟡", "color": "yellow", "level": 3}
    elif moyenne >= 7:
        return {"nom": "En Difficulté", "emoji": "🟠", "color": "orange", "level": 2}
    else:
        return {"nom": "À Risque", "emoji": "🔴", "color": "red", "level": 1}

def get_recommandation(profil_nom):
    """Retourne la recommandation basée sur le profil"""
    recommandations = {
        "Excellence": "Encourager vers les programmes d'excellence et le mentorat",
        "Régulier": "Consolidation des acquis et projets avancés",
        "En Progression": "Sessions de révision et TD supplémentaires recommandés",
        "En Difficulté": "Inscription aux TD de soutien obligatoire",
        "À Risque": "Intervention urgente - Tutorat individuel requis"
    }
    return recommandations.get(profil_nom, "Suivi personnalisé recommandé")


def predict_with_ml_model(student_data_df, module_name=None):
    """
    🧠 VRAIE PRÉDICTION ML avec le modèle XGBoost entraîné
    
    Utilise le modèle chargé pour prédire le risque d'échec
    basé sur l'historique de l'étudiant et la difficulté du module.
    """
    global model_data, df
    
    if model_data is None:
        return None, "Modèle ML non chargé"
    
    try:
        # Extraire les composants du modèle
        calibrated_model = model_data['model']
        scaler = model_data['scaler']
        feature_columns = model_data['feature_columns']
        le_filiere = model_data['le_filiere']
        kmeans = model_data['kmeans']
        profil_mapping = model_data['profil_mapping']
        SEUIL_VALIDATION = model_data['seuil_validation']
        
        # Calculer les stats de l'étudiant à partir de son historique
        student_id = student_data_df['ID'].iloc[0]
        filiere = student_data_df['Filiere'].iloc[0]
        
        # Stats de l'étudiant
        moyenne_total = student_data_df['Total'].mean()
        std_total = student_data_df['Total'].std() if len(student_data_df) > 1 else 0
        min_total = student_data_df['Total'].min()
        max_total = student_data_df['Total'].max()
        nb_modules = len(student_data_df)
        moyenne_note20 = student_data_df['Note_sur_20'].mean()
        min_note20 = student_data_df['Note_sur_20'].min()
        moyenne_practical = student_data_df['Practical'].mean()
        moyenne_theoretical = student_data_df['Theoretical'].mean()
        taux_echec_etudiant = student_data_df['Needs_Support'].mean()
        
        # Stats du module cible (si spécifié)
        if module_name and df is not None:
            module_data = df[df['Module'].str.contains(module_name, case=False, na=False, regex=False)]
            if len(module_data) > 0:
                module_avg_total = module_data['Total'].mean()
                module_avg_note20 = module_data['Note_sur_20'].mean()
                module_taux_echec = module_data['Needs_Support'].mean()
                module_effectif = len(module_data)
                
                # Stats filière-module combo
                combo_data = module_data[module_data['Filiere'] == filiere]
                combo_taux_echec = combo_data['Needs_Support'].mean() if len(combo_data) > 0 else module_taux_echec
            else:
                module_avg_total = 50
                module_avg_note20 = 10
                module_taux_echec = 0.5
                module_effectif = 100
                combo_taux_echec = 0.5
        else:
            module_avg_total = 50
            module_avg_note20 = 10
            module_taux_echec = 0.5
            module_effectif = 100
            combo_taux_echec = 0.5
        
        # Peer group stats (étudiants de la même filière)
        peer_data = df[df['Filiere'] == filiere] if df is not None else student_data_df
        peer_avg_total = peer_data['Total'].mean()
        peer_avg_note20 = peer_data['Note_sur_20'].mean()
        peer_avg_practical = peer_data['Practical'].mean()
        peer_support_rate = peer_data['Needs_Support'].mean()
        
        # Construire le vecteur de features
        features = {
            'Practical': moyenne_practical,
            'Theoretical': moyenne_theoretical,
            'Total': moyenne_total,
            'Note_sur_20': moyenne_note20,
            'Semester': 1,
            'Annee': student_data_df['Annee'].mode().iloc[0] if len(student_data_df) > 0 else 1,
            
            # Peer group features
            'peer_group_avg_total': peer_avg_total,
            'peer_group_avg_note20': peer_avg_note20,
            'peer_group_avg_practical': peer_avg_practical,
            'peer_group_support_rate': peer_support_rate,
            'deviation_from_peer': moyenne_total - peer_avg_total,
            'deviation_note20': moyenne_note20 - peer_avg_note20,
            
            # Student profile features
            'student_avg_total': moyenne_total,
            'student_std_total': std_total if not np.isnan(std_total) else 0,
            'student_min_total': min_total,
            'student_max_total': max_total,
            'student_module_count': nb_modules,
            'student_avg_note20': moyenne_note20,
            'student_min_note20': min_note20,
            'student_avg_practical': moyenne_practical,
            'student_avg_theoretical': moyenne_theoretical,
            'student_support_rate': taux_echec_etudiant,
            
            # Module features
            'module_avg_total': module_avg_total,
            'module_avg_note20': module_avg_note20,
            'module_taux_echec': module_taux_echec,
            'module_effectif': module_effectif,
            
            # Combo features
            'combo_taux_echec': combo_taux_echec,
            'combo_haut_risque': 1 if combo_taux_echec > 0.5 else 0,
            
            # Other features
            'charge_semestre': nb_modules,
            'taux_absenteisme': 0,
            'ratio_pratique': moyenne_practical / (moyenne_total + 1),
            'ecart_theorie_pratique': moyenne_theoretical - moyenne_practical,
            'modules_rattrapage': (student_data_df['Needs_Support'] == 1).sum(),
            'distance_seuil': moyenne_note20 - SEUIL_VALIDATION,
        }
        
        # Encoder la filière
        try:
            features['Filiere_encoded'] = le_filiere.transform([filiere])[0]
        except:
            features['Filiere_encoded'] = 0
        
        # Ajouter pole_encoded
        features['pole_encoded'] = 0
        
        # Ajouter les features manquantes (force_* etc.)
        for col in feature_columns:
            if col not in features:
                if col.startswith('force_'):
                    features[col] = moyenne_note20
                else:
                    features[col] = 0
        
        # Créer le DataFrame
        X_new = pd.DataFrame([features])
        
        # Réordonner les colonnes selon le modèle
        X_new = X_new.reindex(columns=feature_columns, fill_value=0)
        
        # Normaliser
        X_new_scaled = scaler.transform(X_new)
        
        # 🎯 PRÉDICTION ML !
        prediction = calibrated_model.predict(X_new_scaled)[0]
        probabilite = calibrated_model.predict_proba(X_new_scaled)[0, 1]
        
        # Clustering pour déterminer le profil
        try:
            cluster = kmeans.predict(X_new_scaled)[0]
            profil_ml = profil_mapping.get(cluster, 'Inconnu')
        except:
            profil_ml = 'Inconnu'
        
        return {
            'probabilite': float(probabilite),
            'prediction': int(prediction),
            'profil_ml': profil_ml,
            'features_used': len(feature_columns)
        }, None
        
    except Exception as e:
        return None, str(e)


# =============================================================================
# ROUTES API
# =============================================================================

# =============================================================================
# ROUTES AUTHENTIFICATION
# =============================================================================
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Connexion utilisateur avec SQLite"""
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Identifiants requis'}), 400
    
    # Authentifier via la base de données
    user = db.authenticate_user(username, password)
    
    if not user:
        return jsonify({'error': 'Identifiants incorrects'}), 401
    
    token = generate_token(username)
    
    # Logger dans l'audit
    db.add_audit_log(user['id'], 'login', f"Connexion réussie pour {username}")
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'username': user['username'],
            'role': user['role'],
            'nom': user['nom'],
            'prenom': user['prenom'],
            'email': user['email']
        },
        'expires_in': JWT_EXPIRATION_HOURS * 3600
    })


@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Déconnexion utilisateur"""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    
    # Invalider la session dans la BDD
    db.invalidate_session(token)
    
    return jsonify({'success': True, 'message': 'Déconnexion réussie'})


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Retourne l'utilisateur courant"""
    user = request.current_user
    return jsonify({
        'user': {
            'username': user['username'],
            'role': user['role'],
            'nom': user['nom'],
            'prenom': user['prenom'],
            'email': user['email']
        }
    })


@app.route('/api/auth/users', methods=['GET'])
@require_auth
@require_role('admin')
def get_users():
    """Liste des utilisateurs (admin seulement)"""
    users = db.get_all_users()
    return jsonify({
        'users': [{
            'id': u['id'],
            'username': u['username'],
            'role': u['role'],
            'nom': u['nom'],
            'prenom': u['prenom'],
            'email': u['email'],
            'active': u['active'],
            'created_at': u['created_at']
        } for u in users]
    })


@app.route('/api/auth/register', methods=['POST'])
@require_auth
@require_role('admin')
def register_user():
    """Enregistrer un nouvel utilisateur (admin seulement)"""
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    role = data.get('role', 'tuteur')
    nom = data.get('nom', '')
    prenom = data.get('prenom', '')
    email = data.get('email', '')
    
    if not username or not password:
        return jsonify({'error': 'Username et password requis'}), 400
    
    # Vérifier si l'utilisateur existe
    existing = db.get_user_by_username(username)
    if existing:
        return jsonify({'error': 'Utilisateur existe déjà'}), 400
    
    # Créer l'utilisateur dans la BDD
    user_id = db.create_user(username, password, email, role, nom, prenom)
    
    if user_id:
        # Logger dans l'audit
        db.add_audit_log(request.current_user['id'], 'create_user', f"Nouvel utilisateur créé: {username}")
        
        return jsonify({
            'success': True,
            'message': f'Utilisateur {username} créé avec succès',
            'user_id': user_id
        })
    else:
        return jsonify({'error': 'Erreur lors de la création'}), 500


# =============================================================================
# ROUTES INTERVENTIONS (SUIVI DES ACTIONS) - AVEC SQLite
# =============================================================================
@app.route('/api/interventions', methods=['GET'])
@require_auth
def get_interventions():
    """Liste des interventions avec filtres depuis SQLite"""
    filters = {
        'etudiant_id': request.args.get('etudiant_id', ''),
        'type': request.args.get('type', ''),
        'statut': request.args.get('statut', ''),
        'date_debut': request.args.get('date_debut', ''),
        'date_fin': request.args.get('date_fin', '')
    }
    limit = request.args.get('limit', 100, type=int)
    
    interventions = db.get_interventions(filters)
    
    return jsonify({
        'interventions': interventions[:limit],
        'total': len(interventions)
    })


@app.route('/api/interventions', methods=['POST'])
@require_auth
def create_intervention():
    """Créer une nouvelle intervention dans SQLite"""
    data = request.get_json() or {}
    
    intervention_id = db.create_intervention(
        etudiant_id=data.get('etudiant_id'),
        etudiant_nom=data.get('etudiant_nom', ''),
        type_intervention=data.get('type', 'autre'),
        titre=data.get('titre', ''),
        description=data.get('description', ''),
        statut=data.get('statut', 'planifié'),
        priorite=data.get('priorite', 'normale'),
        created_by=request.username,
        resultat=data.get('resultat', '')
    )
    
    if intervention_id:
        # Logger dans l'audit
        db.add_audit_log(
            request.current_user['id'], 
            'create_intervention', 
            f"Intervention créée pour étudiant {data.get('etudiant_id')}"
        )
        
        intervention = db.get_intervention_by_id(intervention_id)
        
        return jsonify({
            'success': True,
            'intervention': intervention,
            'message': 'Intervention créée avec succès'
        })
    else:
        return jsonify({'error': 'Erreur lors de la création'}), 500


@app.route('/api/interventions/<int:intervention_id>', methods=['GET'])
@require_auth
def get_intervention(intervention_id):
    """Détails d'une intervention depuis SQLite"""
    intervention = db.get_intervention_by_id(intervention_id)
    if intervention:
        return jsonify({'intervention': intervention})
    return jsonify({'error': 'Intervention non trouvée'}), 404


@app.route('/api/interventions/<int:intervention_id>', methods=['PUT'])
@require_auth
def update_intervention(intervention_id):
    """Mettre à jour une intervention dans SQLite"""
    data = request.get_json() or {}
    
    # Récupérer l'intervention existante
    existing = db.get_intervention_by_id(intervention_id)
    if not existing:
        return jsonify({'error': 'Intervention non trouvée'}), 404
    
    # Mettre à jour les champs autorisés
    updates = {}
    for key in ['type', 'titre', 'description', 'statut', 'priorite', 'resultat']:
        if key in data:
            updates[key] = data[key]
    
    success = db.update_intervention(intervention_id, request.username, **updates)
    
    if success:
        # Logger dans l'audit
        db.add_audit_log(
            request.current_user['id'],
            'update_intervention',
            f"Intervention {intervention_id} mise à jour"
        )
        
        intervention = db.get_intervention_by_id(intervention_id)
        return jsonify({
            'success': True,
            'intervention': intervention,
            'message': 'Intervention mise à jour'
        })
    
    return jsonify({'error': 'Erreur lors de la mise à jour'}), 500


@app.route('/api/interventions/<int:intervention_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_intervention(intervention_id):
    """Supprimer une intervention (admin seulement)"""
    success = db.delete_intervention(intervention_id)
    
    if success:
        db.add_audit_log(
            request.current_user['id'],
            'delete_intervention',
            f"Intervention {intervention_id} supprimée"
        )
        return jsonify({'success': True, 'message': 'Intervention supprimée'})
    
    return jsonify({'error': 'Intervention non trouvée'}), 404


@app.route('/api/interventions/stats', methods=['GET'])
@require_auth
def get_interventions_stats():
    """Statistiques des interventions depuis SQLite"""
    stats = db.get_intervention_stats()
    return jsonify(stats)


@app.route('/api/interventions/etudiant/<etudiant_id>', methods=['GET'])
@require_auth
def get_interventions_etudiant(etudiant_id):
    """Historique des interventions pour un étudiant depuis SQLite"""
    interventions = db.get_interventions_by_student(etudiant_id)
    
    return jsonify({
        'etudiant_id': etudiant_id,
        'interventions': interventions,
        'total': len(interventions)
    })


# =============================================================================
# ROUTES EXPORT EXCEL
# =============================================================================
@app.route('/api/export/etudiants', methods=['GET'])
@require_auth
def export_etudiants_excel():
    """Exporter la liste des étudiants en Excel"""
    if df is None:
        return jsonify({'error': 'Données non chargées'}), 500
    
    try:
        # Préparer les données
        etudiants = df.groupby('ID').agg({
            'Filiere': 'first',
            'Note_sur_20': 'mean',
            'Needs_Support': 'sum',
            'Module': 'count',
            'Annee': 'max'
        }).reset_index()
        
        etudiants.columns = ['Code Étudiant', 'Filière', 'Moyenne', 'Modules en Échec', 'Nb Modules', 'Année']
        etudiants['Moyenne'] = etudiants['Moyenne'].round(2)
        etudiants['Taux Échec (%)'] = (etudiants['Modules en Échec'] / etudiants['Nb Modules'] * 100).round(1)
        etudiants['Profil'] = etudiants['Moyenne'].apply(lambda x: get_profil(x)['nom'])
        
        # Trier par moyenne
        etudiants = etudiants.sort_values('Moyenne', ascending=True)
        
        # Créer le fichier Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            etudiants.to_excel(writer, sheet_name='Étudiants', index=False)
            
            # Ajuster la largeur des colonnes
            worksheet = writer.sheets['Étudiants']
            for idx, col in enumerate(etudiants.columns):
                max_length = max(
                    etudiants[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 30)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'etudiants_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
        
    except ImportError:
        return jsonify({'error': 'Module openpyxl non installé. Exécutez: pip install openpyxl'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/etudiants-risque', methods=['GET'])
@require_auth
def export_etudiants_risque_excel():
    """Exporter les étudiants à risque en Excel"""
    if df is None:
        return jsonify({'error': 'Données non chargées'}), 500
    
    try:
        etudiants = df.groupby('ID').agg({
            'Filiere': 'first',
            'Note_sur_20': 'mean',
            'Needs_Support': 'sum',
            'Module': 'count'
        }).reset_index()
        
        etudiants.columns = ['Code Étudiant', 'Filière', 'Moyenne', 'Modules Échec', 'Nb Modules']
        etudiants['Taux Échec (%)'] = (etudiants['Modules Échec'] / etudiants['Nb Modules'] * 100).round(1)
        etudiants['Score Risque'] = etudiants.apply(
            lambda x: min(0.99, x['Taux Échec (%)'] / 100 + (10 - x['Moyenne']) / 20), axis=1
        ).round(2)
        etudiants['Profil'] = etudiants['Moyenne'].apply(lambda x: get_profil(x)['nom'])
        
        # Filtrer les étudiants à risque
        etudiants_risque = etudiants[etudiants['Score Risque'] > 0.5].copy()
        etudiants_risque = etudiants_risque.sort_values('Score Risque', ascending=False)
        etudiants_risque['Moyenne'] = etudiants_risque['Moyenne'].round(2)
        
        # Ajouter recommandation
        etudiants_risque['Recommandation'] = etudiants_risque['Profil'].apply(get_recommandation)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            etudiants_risque.to_excel(writer, sheet_name='Étudiants à Risque', index=False)
            
            worksheet = writer.sheets['Étudiants à Risque']
            for idx, col in enumerate(etudiants_risque.columns):
                max_length = max(
                    etudiants_risque[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 40)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'etudiants_risque_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
        
    except ImportError:
        return jsonify({'error': 'Module openpyxl non installé. Exécutez: pip install openpyxl'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/modules', methods=['GET'])
@require_auth
def export_modules_excel():
    """Exporter les statistiques des modules en Excel"""
    if df is None:
        return jsonify({'error': 'Données non chargées'}), 500
    
    try:
        modules = df.groupby('Module').agg({
            'Note_sur_20': 'mean',
            'Needs_Support': 'mean',
            'ID': 'nunique'
        }).reset_index()
        
        modules.columns = ['Module', 'Moyenne', 'Taux Échec', 'Nb Étudiants']
        modules['Moyenne'] = modules['Moyenne'].round(2)
        modules['Taux Échec (%)'] = (modules['Taux Échec'] * 100).round(1)
        modules['Module (FR)'] = modules['Module'].apply(traduire_module)
        
        # Difficulté
        def get_diff(taux):
            if taux >= 50: return 'Très Difficile'
            elif taux >= 30: return 'Difficile'
            elif taux >= 15: return 'Moyen'
            return 'Accessible'
        
        modules['Difficulté'] = modules['Taux Échec (%)'].apply(get_diff)
        modules = modules.sort_values('Taux Échec (%)', ascending=False)
        
        # Réorganiser les colonnes
        modules = modules[['Module', 'Module (FR)', 'Nb Étudiants', 'Moyenne', 'Taux Échec (%)', 'Difficulté']]
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            modules.to_excel(writer, sheet_name='Modules', index=False)
            
            worksheet = writer.sheets['Modules']
            for idx, col in enumerate(modules.columns):
                max_length = max(
                    modules[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 40)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'modules_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
        
    except ImportError:
        return jsonify({'error': 'Module openpyxl non installé. Exécutez: pip install openpyxl'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/interventions', methods=['GET'])
@require_auth
def export_interventions_excel():
    """Exporter l'historique des interventions en Excel depuis SQLite"""
    try:
        interventions = db.get_interventions()
        if not interventions:
            return jsonify({'error': 'Aucune intervention à exporter'}), 400
        
        interventions_df = pd.DataFrame(interventions)
        
        # Réorganiser et renommer les colonnes
        colonnes = {
            'id': 'ID',
            'etudiant_id': 'Code Étudiant',
            'type': 'Type',
            'titre': 'Titre',
            'description': 'Description',
            'statut': 'Statut',
            'priorite': 'Priorité',
            'date': 'Date',
            'heure': 'Heure',
            'created_by': 'Créé par',
            'resultat': 'Résultat'
        }
        
        cols_disponibles = [c for c in colonnes.keys() if c in interventions_df.columns]
        interventions_df = interventions_df[cols_disponibles].rename(columns={c: colonnes[c] for c in cols_disponibles})
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            interventions_df.to_excel(writer, sheet_name='Interventions', index=False)
            
            worksheet = writer.sheets['Interventions']
            for idx, col in enumerate(interventions_df.columns):
                max_length = max(
                    interventions_df[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'interventions_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
        
    except ImportError:
        return jsonify({'error': 'Module openpyxl non installé. Exécutez: pip install openpyxl'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/rapport-complet', methods=['GET'])
@require_auth
@require_role('admin')
def export_rapport_complet():
    """Exporter un rapport complet en Excel (multi-onglets)"""
    if df is None:
        return jsonify({'error': 'Données non chargées'}), 500
    
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # Onglet 1: Résumé
            nb_etudiants = df['ID'].nunique()
            nb_modules = df['Module'].nunique()
            nb_filieres = df['Filiere'].nunique()
            moyenne = df['Note_sur_20'].mean()
            taux_echec = df['Needs_Support'].mean() * 100
            
            resume = pd.DataFrame({
                'Métrique': ['Nombre d\'étudiants', 'Nombre de modules', 'Nombre de filières', 
                            'Moyenne générale', 'Taux d\'échec global (%)'],
                'Valeur': [nb_etudiants, nb_modules, nb_filieres, round(moyenne, 2), round(taux_echec, 1)]
            })
            resume.to_excel(writer, sheet_name='Résumé', index=False)
            
            # Onglet 2: Étudiants
            etudiants = df.groupby('ID').agg({
                'Filiere': 'first',
                'Note_sur_20': 'mean',
                'Needs_Support': 'sum',
                'Module': 'count'
            }).reset_index()
            etudiants.columns = ['Code', 'Filière', 'Moyenne', 'Échecs', 'Modules']
            etudiants['Moyenne'] = etudiants['Moyenne'].round(2)
            etudiants['Profil'] = etudiants['Moyenne'].apply(lambda x: get_profil(x)['nom'])
            etudiants.to_excel(writer, sheet_name='Étudiants', index=False)
            
            # Onglet 3: Modules
            modules = df.groupby('Module').agg({
                'Note_sur_20': 'mean',
                'Needs_Support': 'mean',
                'ID': 'nunique'
            }).reset_index()
            modules.columns = ['Module', 'Moyenne', 'Taux Échec', 'Étudiants']
            modules['Moyenne'] = modules['Moyenne'].round(2)
            modules['Taux Échec (%)'] = (modules['Taux Échec'] * 100).round(1)
            modules['Traduction'] = modules['Module'].apply(traduire_module)
            modules.to_excel(writer, sheet_name='Modules', index=False)
            
            # Onglet 4: Filières
            filieres = df.groupby('Filiere').agg({
                'Note_sur_20': 'mean',
                'Needs_Support': 'mean',
                'ID': 'nunique',
                'Module': 'nunique'
            }).reset_index()
            filieres.columns = ['Filière', 'Moyenne', 'Taux Échec', 'Étudiants', 'Modules']
            filieres['Moyenne'] = filieres['Moyenne'].round(2)
            filieres['Taux Échec (%)'] = (filieres['Taux Échec'] * 100).round(1)
            filieres.to_excel(writer, sheet_name='Filières', index=False)
            
            # Onglet 5: Interventions depuis SQLite
            interventions = db.get_interventions()
            if interventions:
                interv_df = pd.DataFrame(interventions)
                cols = ['id', 'etudiant_id', 'type', 'statut', 'date', 'created_by']
                cols = [c for c in cols if c in interv_df.columns]
                interv_df[cols].to_excel(writer, sheet_name='Interventions', index=False)
            
            # Ajuster les largeurs
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    worksheet.column_dimensions[column_letter].width = min(max_length + 2, 40)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'rapport_complet_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
        )
        
    except ImportError:
        return jsonify({'error': 'Module openpyxl non installé. Exécutez: pip install openpyxl'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# ROUTES EXISTANTES
# =============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification de l'état de l'API"""
    intervention_stats = db.get_intervention_stats()
    return jsonify({
        "status": "ok",
        "message": "API Soutien Pédagogique opérationnelle",
        "data_loaded": df is not None,
        "model_loaded": model_data is not None,
        "total_records": len(df) if df is not None else 0,
        "auth_enabled": True,
        "database": "SQLite",
        "interventions_count": intervention_stats.get('total', 0)
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Statistiques générales du système"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    nb_etudiants = df['ID'].nunique()
    nb_modules = df['Module'].nunique()
    nb_filieres = df['Filiere'].nunique()
    moyenne_generale = df['Note_sur_20'].mean()
    taux_echec_global = df['Needs_Support'].mean() * 100
    
    # Répartition par profil
    etudiants_stats = df.groupby('ID').agg({
        'Note_sur_20': 'mean',
        'Filiere': 'first'
    }).reset_index()
    
    profils_count = {
        "Excellence": len(etudiants_stats[etudiants_stats['Note_sur_20'] >= 14]),
        "Régulier": len(etudiants_stats[(etudiants_stats['Note_sur_20'] >= 12) & (etudiants_stats['Note_sur_20'] < 14)]),
        "En Progression": len(etudiants_stats[(etudiants_stats['Note_sur_20'] >= 10) & (etudiants_stats['Note_sur_20'] < 12)]),
        "En Difficulté": len(etudiants_stats[(etudiants_stats['Note_sur_20'] >= 7) & (etudiants_stats['Note_sur_20'] < 10)]),
        "À Risque": len(etudiants_stats[etudiants_stats['Note_sur_20'] < 7])
    }
    
    # Stats par filière
    filieres_stats = df.groupby('Filiere').agg({
        'Note_sur_20': 'mean',
        'Needs_Support': 'mean',
        'ID': 'nunique'
    }).round(2).to_dict('index')
    
    return jsonify({
        "nb_etudiants": nb_etudiants,
        "nb_modules": nb_modules,
        "nb_filieres": nb_filieres,
        "moyenne_generale": round(moyenne_generale, 2),
        "taux_echec_global": round(taux_echec_global, 1),
        "profils_count": profils_count,
        "filieres_stats": filieres_stats
    })

@app.route('/api/etudiants', methods=['GET'])
def get_etudiants():
    """Liste des étudiants avec pagination"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str)
    filiere_filter = request.args.get('filiere', '', type=str)
    profil_filter = request.args.get('profil', '', type=str)
    
    # Agrégation par étudiant
    etudiants = df.groupby('ID').agg({
        'Filiere': 'first',
        'Note_sur_20': 'mean',
        'Needs_Support': 'sum',
        'Module': 'count',
        'Annee': 'max'
    }).reset_index()
    
    etudiants.columns = ['id', 'filiere', 'moyenne', 'modules_echec', 'nb_modules', 'annee']
    
    # Filtres
    if search:
        etudiants = etudiants[etudiants['id'].str.contains(search, case=False)]
    if filiere_filter:
        etudiants = etudiants[etudiants['filiere'] == filiere_filter]
    
    # Ajouter profil
    etudiants['profil'] = etudiants['moyenne'].apply(lambda x: get_profil(x)['nom'])
    
    if profil_filter:
        etudiants = etudiants[etudiants['profil'] == profil_filter]
    
    # Tri par moyenne
    etudiants = etudiants.sort_values('moyenne', ascending=True)
    
    # Pagination
    total = len(etudiants)
    start = (page - 1) * per_page
    end = start + per_page
    
    etudiants_page = etudiants.iloc[start:end].to_dict('records')
    
    # Arrondir les valeurs
    for e in etudiants_page:
        e['moyenne'] = round(e['moyenne'], 2)
        e['profil_info'] = get_profil(e['moyenne'])
    
    return jsonify({
        "etudiants": etudiants_page,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    })

@app.route('/api/etudiant/<student_id>', methods=['GET'])
def get_etudiant(student_id):
    """Détails d'un étudiant spécifique"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    etudiant_data = df[df['ID'] == str(student_id)]
    
    if len(etudiant_data) == 0:
        return jsonify({"error": "Étudiant non trouvé"}), 404
    
    filiere = etudiant_data['Filiere'].iloc[0]
    moyenne = etudiant_data['Note_sur_20'].mean()
    profil = get_profil(moyenne)
    
    # Détails par module
    modules = []
    for _, row in etudiant_data.iterrows():
        modules.append({
            "nom": traduire_module(row['Module']),
            "nom_original": row['Module'],
            "note": round(row['Note_sur_20'], 1),
            "practical": row['Practical'],
            "theoretical": row['Theoretical'],
            "status": row['Status'],
            "semester": int(row['Semester']),
            "needs_support": bool(row['Needs_Support'])
        })
    
    # Modules en échec
    modules_echec = [m for m in modules if m['needs_support']]
    taux_echec = len(modules_echec) / len(modules) * 100 if modules else 0
    
    # Score de risque
    score_risque = min(0.99, taux_echec/100 + (10-moyenne)/20)
    
    return jsonify({
        "id": student_id,
        "filiere": filiere,
        "moyenne": round(moyenne, 2),
        "nb_modules": len(modules),
        "modules_echec": len(modules_echec),
        "taux_echec": round(taux_echec, 1),
        "score_risque": round(score_risque, 2),
        "profil": profil,
        "recommandation": get_recommandation(profil['nom']),
        "modules": sorted(modules, key=lambda x: x['note']),
        "modules_prioritaires": sorted(modules_echec, key=lambda x: x['note'])[:5]
    })

@app.route('/api/modules', methods=['GET'])
def get_modules():
    """Liste des modules avec statistiques"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    modules_stats = df.groupby('Module').agg({
        'Note_sur_20': 'mean',
        'Needs_Support': 'mean',
        'ID': 'nunique'
    }).reset_index()
    
    modules_stats.columns = ['nom', 'moyenne', 'taux_echec', 'nb_etudiants']
    modules_stats['taux_echec'] = modules_stats['taux_echec'] * 100
    modules_stats['nom_fr'] = modules_stats['nom'].apply(traduire_module)
    
    # Classification difficulté
    def get_difficulte(taux):
        if taux >= 50:
            return {"niveau": "Très Difficile", "color": "red"}
        elif taux >= 30:
            return {"niveau": "Difficile", "color": "orange"}
        elif taux >= 15:
            return {"niveau": "Moyen", "color": "yellow"}
        else:
            return {"niveau": "Accessible", "color": "green"}
    
    modules_stats['difficulte'] = modules_stats['taux_echec'].apply(get_difficulte)
    
    # Tri par taux d'échec
    modules_stats = modules_stats.sort_values('taux_echec', ascending=False)
    
    result = modules_stats.round(2).to_dict('records')
    
    return jsonify({
        "modules": result,
        "total": len(result)
    })

@app.route('/api/module/<path:module_name>', methods=['GET'])
def get_module(module_name):
    """Détails d'un module spécifique"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    module_data = df[df['Module'].str.contains(module_name, case=False, na=False, regex=False)]
    
    if len(module_data) == 0:
        return jsonify({"error": "Module non trouvé"}), 404
    
    module_exact = module_data['Module'].iloc[0]
    moyenne = module_data['Note_sur_20'].mean()
    taux_echec = module_data['Needs_Support'].mean() * 100
    
    # Stats par filière
    filieres_stats = module_data.groupby('Filiere').agg({
        'Note_sur_20': 'mean',
        'Needs_Support': 'mean',
        'ID': 'count'
    }).round(2)
    
    filieres = []
    for filiere, row in filieres_stats.iterrows():
        filieres.append({
            "nom": filiere,
            "moyenne": round(row['Note_sur_20'], 1),
            "taux_echec": round(row['Needs_Support'] * 100, 1),
            "nb_etudiants": int(row['ID'])
        })
    
    # Distribution des notes
    bins = [0, 4, 8, 10, 12, 14, 20]
    labels = ['0-4', '4-8', '8-10', '10-12', '12-14', '14-20']
    module_data['tranche'] = pd.cut(module_data['Note_sur_20'], bins=bins, labels=labels, include_lowest=True)
    distribution = module_data['tranche'].value_counts().to_dict()
    distribution = {str(k): int(v) for k, v in distribution.items()}
    
    return jsonify({
        "nom": module_exact,
        "nom_fr": traduire_module(module_exact),
        "moyenne": round(moyenne, 2),
        "taux_echec": round(taux_echec, 1),
        "nb_etudiants": len(module_data),
        "filieres": filieres,
        "distribution": distribution
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Prédiction pour un nouvel étudiant"""
    if model_data is None:
        return jsonify({"error": "Modèle non chargé"}), 500
    
    data = request.json
    
    try:
        # Support pour le nouveau format avec modules
        modules_input = data.get('modules', [])
        code_etudiant = data.get('code_etudiant', '')
        filiere = data.get('filiere', 'EEA')
        annee = int(data.get('annee', 1))
        semester = int(data.get('semester', 1))
        
        # Si on a des modules, calculer la moyenne
        if modules_input and len(modules_input) > 0:
            notes = [m.get('note', 0) for m in modules_input if m.get('note') is not None]
            if notes:
                note_sur_20 = sum(notes) / len(notes)
                total = note_sur_20 * 5  # Convertir sur 100
                practical = total * 0.4
                theoretical = total * 0.6
            else:
                practical = 0
                theoretical = 0
                total = 0
                note_sur_20 = 0
        else:
            # Ancien format direct
            practical = min(float(data.get('practical', 0)), 50)
            theoretical = min(float(data.get('theoretical', 0)), 50)
            total = min(float(data.get('total', practical + theoretical)), 100)
            note_sur_20 = total / 5
        
        note_sur_20 = total / 5
        
        # Créer les features
        features = {
            'Practical': practical,
            'Theoretical': theoretical,
            'Total': total,
            'Note_sur_20': note_sur_20,
            'Semester': semester,
            'Annee': annee,
            'Est_Echec': 1 if total < 50 else 0,
            'Ecart_Validation': total - 50,
            'Ratio_Practical': practical / total if total > 0 else 0,
            'Note_Ponderee': note_sur_20 * annee,
        }
        
        # Features encodées
        le_filiere = model_data.get('le_filiere')
        if le_filiere and filiere in le_filiere.classes_:
            features['Filiere_encoded'] = le_filiere.transform([filiere])[0]
        else:
            features['Filiere_encoded'] = 0
        
        # Ajouter les features manquantes avec des valeurs par défaut
        feature_columns = model_data.get('feature_columns', [])
        for col in feature_columns:
            if col not in features:
                features[col] = 0
        
        # Préparer le vecteur
        X = pd.DataFrame([features])[feature_columns] if feature_columns else pd.DataFrame([features])
        
        # Scaler
        scaler = model_data.get('scaler')
        if scaler:
            X_scaled = scaler.transform(X)
        else:
            X_scaled = X.values
        
        # Prédiction
        model = model_data.get('calibrated_model') or model_data.get('xgb_model')
        if model:
            prediction = int(model.predict(X_scaled)[0])
            proba = model.predict_proba(X_scaled)[0]
            proba_risque = float(proba[1]) if len(proba) > 1 else float(proba[0])
        else:
            # Fallback basé sur la note
            prediction = 1 if note_sur_20 < 10 else 0
            proba_risque = max(0, (10 - note_sur_20) / 10)
        
        # Catégorie de risque
        if proba_risque >= 0.8:
            categorie = {"niveau": "CRITIQUE", "color": "red", "emoji": "🔴"}
        elif proba_risque >= 0.6:
            categorie = {"niveau": "ÉLEVÉ", "color": "orange", "emoji": "🟠"}
        elif proba_risque >= 0.4:
            categorie = {"niveau": "MODÉRÉ", "color": "yellow", "emoji": "🟡"}
        elif proba_risque >= 0.2:
            categorie = {"niveau": "FAIBLE", "color": "lightgreen", "emoji": "🟢"}
        else:
            categorie = {"niveau": "MINIMAL", "color": "green", "emoji": "⚪"}
        
        # Profil
        profil = get_profil(note_sur_20)
        
        # Recommandations (liste pour correspondre au frontend)
        recommandations = []
        if proba_risque >= 0.8:
            recommandations = [
                "🚨 Tutorat individuel URGENT",
                "📞 Convocation conseiller pédagogique",
                "📚 Séances de rattrapage obligatoires",
                "👥 Intégration groupe de soutien"
            ]
        elif proba_risque >= 0.6:
            recommandations = [
                "📝 Inscription TD de soutien",
                "📅 Suivi hebdomadaire recommandé",
                "📖 Révision des fondamentaux",
                "🎯 Objectifs personnalisés"
            ]
        elif proba_risque >= 0.4:
            recommandations = [
                "📚 Sessions de révision recommandées",
                "💻 Ressources en ligne disponibles",
                "👥 Travail en groupe conseillé"
            ]
        elif proba_risque >= 0.2:
            recommandations = [
                "📖 Ressources complémentaires disponibles",
                "🎯 Maintenir le rythme actuel"
            ]
        else:
            recommandations = [
                "🌟 Excellent travail !",
                "📈 Ressources avancées disponibles",
                "👨‍🏫 Possibilité de tutorat pair"
            ]
        
        # Modules similaires à risque (basé sur les modules entrés)
        modules_similaires = []
        if modules_input:
            for m in modules_input:
                if m.get('note', 20) < 10:
                    modules_similaires.append(m.get('code', 'Module inconnu'))
        
        return jsonify({
            "etudiant_code": code_etudiant or "NOUVEAU",
            "risque": bool(prediction),
            "probabilite": round(proba_risque * 100, 1),
            "profil": profil.get('nom', 'Non défini') if isinstance(profil, dict) else str(profil),
            "recommandations": recommandations,
            "modules_similaires": modules_similaires,
            "note_sur_20": round(note_sur_20, 1),
            "categorie_risque": categorie,
            "details": {
                "practical": practical,
                "theoretical": theoretical,
                "total": total,
                "filiere": filiere,
                "annee": annee,
                "semester": semester,
                "nb_modules": len(modules_input) if modules_input else 0
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/predict/modules-futurs', methods=['POST'])
def predict_future_modules():
    """
    🔮 Prédit la probabilité de réussite pour tous les modules
    qu'un étudiant n'a pas encore passés.
    
    Utilise l'historique de l'étudiant et les statistiques des modules
    pour faire des prédictions préventives.
    """
    if df is None or model_data is None:
        return jsonify({"error": "Données ou modèle non chargés"}), 500
    
    try:
        data = request.json
        code_etudiant = data.get('code_etudiant', '')
        filiere = data.get('filiere', '')  # Optionnel maintenant
        
        # ✅ Si code étudiant fourni, récupérer TOUT depuis la base
        if code_etudiant and code_etudiant in df['ID'].values:
            student_history = df[df['ID'] == code_etudiant].copy()
            
            # 🎯 DÉTECTION AUTOMATIQUE de la filière ET de l'année
            filiere = student_history['Filiere'].iloc[0]
            annee_actuelle = int(student_history['Annee'].max()) if 'Annee' in student_history.columns else 1
            
        elif not code_etudiant:
            return jsonify({"error": "Code étudiant requis"}), 400
        else:
            return jsonify({"error": f"Code étudiant '{code_etudiant}' non trouvé dans la base de données"}), 404
        
        # Calculer stats de l'étudiant
        moyenne_generale = student_history['Note_sur_20'].mean()
        modules_passes_list = student_history['Module'].unique().tolist() if 'Module' in student_history.columns else []
        
        # Obtenir tous les modules de la filière
        all_modules = df[df['Filiere'] == filiere]['Module'].unique().tolist()
        
        # 🎯 PRÉDIRE POUR TOUTES LES ANNÉES FUTURES (pas juste l'année suivante)
        # Calculer le nombre d'années futures à prédire (jusqu'à l'année 5 max)
        annees_futures = list(range(annee_actuelle + 1, min(annee_actuelle + 4, 6)))  # Max 3 années futures
        
        # Si seulement une année future, limiter aux modules de cette année
        # Sinon, prendre tous les modules non passés
        if len(annees_futures) == 1 and 'Annee' in df.columns:
            modules_annee_suivante = df[
                (df['Filiere'] == filiere) & 
                (df['Annee'] == annees_futures[0])
            ]['Module'].unique().tolist()
            modules_futurs = [m for m in modules_annee_suivante if m not in modules_passes_list]
        else:
            # Identifier modules futurs (non encore passés) - TOUS
            modules_futurs = [m for m in all_modules if m not in modules_passes_list]
        
        # Limiter à 25 modules max pour éviter surcharge
        modules_futurs = modules_futurs[:25]
        
        # Prédire pour chaque module futur
        predictions = []
        
        for module in modules_futurs:
            # Utiliser predict_with_ml_model si disponible
            ml_pred, error = predict_with_ml_model(student_history, module_name=module)
            
            if ml_pred and not error:
                # Utiliser la prédiction ML
                proba_echec = ml_pred['probabilite']
                needs_support = ml_pred['prediction']
            else:
                # Fallback : utiliser statistiques simples
                module_data = df[df['Module'] == module]
                module_taux_echec = module_data['Needs_Support'].mean() if len(module_data) > 0 else 0.5
                
                # Ajuster selon la moyenne de l'étudiant
                if moyenne_generale >= 14:
                    proba_echec = module_taux_echec * 0.3
                elif moyenne_generale >= 12:
                    proba_echec = module_taux_echec * 0.6
                elif moyenne_generale >= 10:
                    proba_echec = module_taux_echec * 1.0
                else:
                    proba_echec = min(1.0, module_taux_echec * 1.5)
                
                needs_support = 1 if proba_echec > 0.5 else 0
            
            proba_reussite = 1 - proba_echec
            
            # Catégoriser le risque
            if proba_reussite >= 0.8:
                categorie = {"niveau": "EXCELLENT", "color": "green", "emoji": "✅"}
                action = "Aucune action nécessaire"
            elif proba_reussite >= 0.6:
                categorie = {"niveau": "BON", "color": "lightgreen", "emoji": "🟢"}
                action = "Suivi normal"
            elif proba_reussite >= 0.4:
                categorie = {"niveau": "MODÉRÉ", "color": "yellow", "emoji": "🟡"}
                action = "Tutorat préventif recommandé"
            elif proba_reussite >= 0.2:
                categorie = {"niveau": "RISQUÉ", "color": "orange", "emoji": "🟠"}
                action = "Tutorat préventif nécessaire"
            else:
                categorie = {"niveau": "TRÈS RISQUÉ", "color": "red", "emoji": "🔴"}
                action = "Reporter si possible ou tutorat intensif"
            
            # Stats du module
            module_stats = df[df['Module'] == module].agg({
                'Note_sur_20': 'mean',
                'Needs_Support': 'mean',
                'ID': 'count'
            })
            
            predictions.append({
                'module': module,
                'module_traduit': traduire_module(module),
                'probabilite_reussite': round(proba_reussite * 100, 1),
                'probabilite_echec': round(proba_echec * 100, 1),
                'besoin_soutien': bool(needs_support),
                'categorie': categorie,
                'action_preventive': action,
                'statistiques_module': {
                    'moyenne': round(module_stats['Note_sur_20'], 2) if not pd.isna(module_stats['Note_sur_20']) else 10.0,
                    'taux_echec': round(module_stats['Needs_Support'] * 100, 1) if not pd.isna(module_stats['Needs_Support']) else 50.0,
                    'nb_etudiants': int(module_stats['ID']) if not pd.isna(module_stats['ID']) else 0
                }
            })
        
        # Trier par probabilité de réussite (du plus risqué au plus sûr)
        predictions.sort(key=lambda x: x['probabilite_reussite'])
        
        # Séparer en catégories
        modules_haut_risque = [p for p in predictions if p['probabilite_reussite'] < 40]
        modules_risque_modere = [p for p in predictions if 40 <= p['probabilite_reussite'] < 60]
        modules_recommandes = [p for p in predictions if p['probabilite_reussite'] >= 60]
        
        return jsonify({
            'etudiant': code_etudiant,
            'filiere': filiere,
            'annee_actuelle': annee_actuelle,
            'annees_futures': annees_futures if 'annees_futures' in locals() else [annee_actuelle + 1],
            'moyenne_generale': round(moyenne_generale, 2),
            'nb_modules_passes': len(modules_passes_list),
            'nb_modules_futurs': len(predictions),
            'predictions': predictions,
            'resume': {
                'modules_haut_risque': len(modules_haut_risque),
                'modules_risque_modere': len(modules_risque_modere),
                'modules_recommandes': len(modules_recommandes)
            },
            'modules_par_categorie': {
                'haut_risque': modules_haut_risque[:5],  # Top 5 plus risqués
                'risque_modere': modules_risque_modere[:5],
                'recommandes': modules_recommandes[:10]  # Top 10 recommandés
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400



@app.route('/api/filieres', methods=['GET'])
def get_filieres():
    """Liste des filières disponibles"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    filieres = df['Filiere'].unique().tolist()
    return jsonify({"filieres": sorted(filieres)})

@app.route('/api/etudiants-risque', methods=['GET'])
def get_etudiants_risque():
    """Liste des étudiants à haut risque avec distribution par niveau"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    limit = request.args.get('limit', 100, type=int)
    
    etudiants = df.groupby('ID').agg({
        'Filiere': 'first',
        'Note_sur_20': 'mean',
        'Needs_Support': 'sum',
        'Module': 'count'
    }).reset_index()
    
    etudiants.columns = ['id', 'filiere', 'moyenne', 'modules_echec', 'nb_modules']
    etudiants['taux_echec'] = etudiants['modules_echec'] / etudiants['nb_modules'] * 100
    
    # Formule de score basée sur la moyenne
    def calculer_score_risque(row):
        moyenne = row['moyenne']
        taux_echec = row['taux_echec']
        
        # Score basé principalement sur la moyenne
        if moyenne < 5:
            score_base = 0.90  # Critique
        elif moyenne < 7:
            score_base = 0.70  # Élevé
        elif moyenne < 10:
            score_base = 0.50  # Modéré
        elif moyenne < 12:
            score_base = 0.30  # Faible
        else:
            score_base = 0.10  # Minimal
        
        # Ajustement basé sur le taux d'échec (max +0.09)
        bonus = (taux_echec / 100) * 0.09
        
        return round(min(0.99, score_base + bonus), 2)
    
    etudiants['score_risque'] = etudiants.apply(calculer_score_risque, axis=1)
    
    # Collecter des étudiants de chaque niveau pour avoir une distribution
    critiques = etudiants[etudiants['score_risque'] >= 0.8].sort_values('score_risque', ascending=False).head(limit // 4)
    eleves = etudiants[(etudiants['score_risque'] >= 0.6) & (etudiants['score_risque'] < 0.8)].sort_values('score_risque', ascending=False).head(limit // 4)
    moderes = etudiants[(etudiants['score_risque'] >= 0.4) & (etudiants['score_risque'] < 0.6)].sort_values('score_risque', ascending=False).head(limit // 4)
    faibles = etudiants[(etudiants['score_risque'] >= 0.2) & (etudiants['score_risque'] < 0.4)].sort_values('score_risque', ascending=False).head(limit // 4)
    
    # Combiner tous les niveaux
    import pandas as pd
    etudiants_risque = pd.concat([critiques, eleves, moderes, faibles])
    etudiants_risque = etudiants_risque.sort_values('score_risque', ascending=False)
    
    result = etudiants_risque.round(2).to_dict('records')
    
    for e in result:
        e['profil'] = get_profil(e['moyenne'])
    
    return jsonify(result)

# =============================================================================
# RAPPORTS PDF ET ALERTES EMAIL
# =============================================================================

@app.route('/api/rapports/types', methods=['GET'])
def get_rapport_types():
    """Liste des types de rapports disponibles"""
    return jsonify({
        "types": [
            {
                "id": "etudiant",
                "nom": "Fiche Étudiant",
                "description": "Rapport individuel détaillé d'un étudiant",
                "icon": "👤"
            },
            {
                "id": "module",
                "nom": "Rapport Module",
                "description": "Analyse des étudiants à risque par module",
                "icon": "📚"
            },
            {
                "id": "filiere",
                "nom": "Rapport Filière",
                "description": "Analyse complète d'une filière",
                "icon": "🎓"
            },
            {
                "id": "synthese",
                "nom": "Synthèse Complète",
                "description": "Rapport global de toutes les filières",
                "icon": "📊"
            }
        ]
    })


@app.route('/api/rapports/generer', methods=['POST'])
def generer_rapport():
    """Génère un rapport PDF"""
    try:
        data = request.json
        type_rapport = data.get('type', 'synthese')
        id_cible = data.get('id', None)
        
        # Import dynamique du générateur
        import sys
        sys.path.insert(0, str(BASE_PATH))
        from generate_pdf_reports import RapportPedagogiqueGenerator
        
        generator = RapportPedagogiqueGenerator()
        generator.charger_donnees()
        
        fichier = None
        
        if type_rapport == 'etudiant' and id_cible:
            fichier = generator.rapport_etudiant(id_cible)
        elif type_rapport == 'module' and id_cible:
            fichier = generator.rapport_module(id_cible)
        elif type_rapport == 'filiere' and id_cible:
            fichier = generator.rapport_filiere(id_cible)
        elif type_rapport == 'synthese':
            fichier = generator.rapport_synthese()
        else:
            return jsonify({"error": "Type de rapport invalide ou ID manquant"}), 400
        
        if fichier:
            return jsonify({
                "success": True,
                "fichier": fichier,
                "message": f"Rapport {type_rapport} généré avec succès"
            })
        else:
            return jsonify({"error": "Erreur lors de la génération"}), 500
            
    except ImportError:
        return jsonify({
            "error": "Module de génération PDF non disponible. Installez reportlab: pip install reportlab"
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rapports/liste', methods=['GET'])
def liste_rapports():
    """Liste les rapports PDF générés"""
    rapports_path = OUTPUT_PATH / "rapports_pdf"
    
    if not rapports_path.exists():
        return jsonify({"rapports": [], "total": 0})
    
    rapports = []
    for f in rapports_path.glob("*.pdf"):
        stat = f.stat()
        rapports.append({
            "nom": f.name,
            "chemin": str(f),
            "taille": f"{stat.st_size / 1024:.1f} KB",
            "date": pd.Timestamp(stat.st_mtime, unit='s').strftime('%d/%m/%Y %H:%M')
        })
    
    rapports.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({
        "rapports": rapports,
        "total": len(rapports)
    })


@app.route('/api/rapports/global', methods=['GET'])
def rapport_global():
    """Génère un rapport PDF global"""
    try:
        import sys
        sys.path.insert(0, str(BASE_PATH))
        from generate_pdf_reports import generate_global_report
        
        # Utiliser le DataFrame global déjà préparé
        global df
        if df is None:
            load_data()
        
        fichier = generate_global_report(df)
        
        if fichier:
            from flask import send_file
            return send_file(fichier, mimetype='application/pdf', as_attachment=True, 
                           download_name='rapport_global.pdf')
        else:
            return jsonify({"error": "Erreur lors de la génération"}), 500
    except ImportError as e:
        return jsonify({"error": f"Module de génération PDF non disponible: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rapports/filiere/<filiere>', methods=['GET'])
def rapport_filiere(filiere):
    """Génère un rapport PDF pour une filière"""
    try:
        import sys
        sys.path.insert(0, str(BASE_PATH))
        from generate_pdf_reports import generate_filiere_report
        
        # Utiliser le DataFrame global déjà préparé
        global df
        if df is None:
            load_data()
        
        fichier = generate_filiere_report(filiere, df)
        
        if fichier:
            from flask import send_file
            return send_file(fichier, mimetype='application/pdf', as_attachment=True,
                           download_name=f'rapport_filiere_{filiere}.pdf')
        else:
            return jsonify({"error": "Erreur lors de la génération"}), 500
    except ImportError as e:
        return jsonify({"error": f"Module de génération PDF non disponible: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/rapports/etudiant/<code>', methods=['GET'])
def rapport_etudiant(code):
    """Génère un rapport PDF pour un étudiant"""
    try:
        import sys
        sys.path.insert(0, str(BASE_PATH))
        from generate_pdf_reports import generate_student_report
        
        # Utiliser le DataFrame global déjà préparé
        global df
        if df is None:
            load_data()
        
        fichier = generate_student_report(code, df)
        
        if fichier:
            from flask import send_file
            return send_file(fichier, mimetype='application/pdf', as_attachment=True,
                           download_name=f'rapport_etudiant_{code}.pdf')
        else:
            return jsonify({"error": "Étudiant non trouvé"}), 404
    except ImportError as e:
        return jsonify({"error": f"Module de génération PDF non disponible: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/alertes/preview', methods=['GET'])
def preview_alertes():
    """Génère les aperçus des alertes email"""
    try:
        import sys
        sys.path.insert(0, str(BASE_PATH))
        from email_alerts import generate_student_alerts, generate_module_alerts, generate_admin_report
        
        # Charger les données
        df_alerts = df.copy()
        
        # Générer les alertes en mode preview
        student_alerts = generate_student_alerts(df_alerts, preview_only=True)
        module_alerts = generate_module_alerts(df_alerts, preview_only=True)
        admin_report = generate_admin_report(df_alerts, preview_only=True)
        
        return jsonify({
            "success": True,
            "alertes_etudiants": len(student_alerts),
            "alertes_modules": len(module_alerts),
            "rapport_admin": admin_report is not None,
            "chemin_aperçus": str(OUTPUT_PATH / "alertes")
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/alertes/statistiques', methods=['GET'])
def stats_alertes():
    """Statistiques sur les alertes potentielles"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    # Étudiants à alerter
    student_stats = df.groupby('ID').agg({
        'Note_sur_20': 'mean',
        'Needs_Support': ['sum', 'count']
    }).reset_index()
    student_stats.columns = ['ID', 'moyenne', 'echecs', 'total']
    
    etudiants_critique = len(student_stats[student_stats['moyenne'] < 7])
    etudiants_difficulte = len(student_stats[(student_stats['moyenne'] >= 7) & (student_stats['moyenne'] < 10)])
    
    # Modules critiques
    module_stats = df.groupby('Module').agg({
        'Needs_Support': 'mean'
    }).reset_index()
    module_stats['taux'] = module_stats['Needs_Support'] * 100
    modules_critiques = len(module_stats[module_stats['taux'] >= 50])
    
    return jsonify({
        "etudiants_a_alerter": {
            "critique": etudiants_critique,
            "difficulte": etudiants_difficulte,
            "total": etudiants_critique + etudiants_difficulte
        },
        "modules_critiques": modules_critiques,
        "total_alertes_potentielles": etudiants_critique + etudiants_difficulte + modules_critiques
    })


@app.route('/api/alertes/liste', methods=['GET'])
def liste_alertes():
    """Liste les aperçus d'alertes générés"""
    alertes_path = OUTPUT_PATH / "alertes"
    
    if not alertes_path.exists():
        return jsonify({"alertes": [], "total": 0})
    
    alertes = []
    for f in alertes_path.glob("*.html"):
        stat = f.stat()
        
        # Déterminer le type
        if "etudiant" in f.name:
            type_alerte = "Étudiant"
            icon = "👤"
        elif "module" in f.name:
            type_alerte = "Module"
            icon = "📚"
        else:
            type_alerte = "Administration"
            icon = "📊"
        
        alertes.append({
            "nom": f.name,
            "type": type_alerte,
            "icon": icon,
            "chemin": str(f),
            "taille": f"{stat.st_size / 1024:.1f} KB",
            "date": pd.Timestamp(stat.st_mtime, unit='s').strftime('%d/%m/%Y %H:%M')
        })
    
    alertes.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({
        "alertes": alertes,
        "total": len(alertes)
    })


@app.route('/api/alertes/etudiant', methods=['POST', 'OPTIONS'])
def alerte_etudiant():
    """Envoie une alerte email pour un étudiant"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        code = data.get('code')
        email = data.get('email')
        
        if not code or not email:
            return jsonify({"error": "Code étudiant et email requis"}), 400
        
        # Vérifier si l'étudiant existe
        student_data = df[df['ID'].astype(str) == str(code)]
        if student_data.empty:
            return jsonify({"error": f"Étudiant {code} non trouvé"}), 404
        
        # Calculer les informations de l'étudiant
        moyenne = student_data['Note_sur_20'].mean()
        filiere = student_data['Filiere'].iloc[0]
        nb_modules = len(student_data)
        modules_echec = len(student_data[student_data['Needs_Support'] == 1])
        
        # Déterminer le profil
        if moyenne >= 14:
            profil = "Excellence"
            couleur_profil = "#10B981"
        elif moyenne >= 12:
            profil = "Régulier"
            couleur_profil = "#3B82F6"
        elif moyenne >= 10:
            profil = "En Progression"
            couleur_profil = "#F59E0B"
        elif moyenne >= 8:
            profil = "En Difficulté"
            couleur_profil = "#F97316"
        else:
            profil = "À Risque"
            couleur_profil = "#EF4444"
        
        # Générer l'alerte HTML
        alertes_path = OUTPUT_PATH / "alertes"
        alertes_path.mkdir(exist_ok=True)
        
        alerte_file = alertes_path / f"alerte_etudiant_{code}.html"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Alerte Pédagogique - Étudiant {code}</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f8fafc;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); border-radius: 12px 12px 0 0; padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">🎓 Système de Soutien Pédagogique</h1>
                    <p style="color: rgba(255,255,255,0.8); margin-top: 10px;">Université - Faculté d'Ingénierie</p>
                </div>
                
                <!-- Content -->
                <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #1e293b; margin-top: 0;">⚠️ Notification de Suivi Pédagogique</h2>
                    
                    <p style="color: #475569; line-height: 1.6;">
                        Cher(e) étudiant(e),<br><br>
                        Notre système d'analyse pédagogique a identifié que vous pourriez bénéficier d'un accompagnement personnalisé pour optimiser vos chances de réussite.
                    </p>
                    
                    <!-- Info Card -->
                    <div style="background: #f1f5f9; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #1e293b; margin-top: 0; font-size: 16px;">📊 Votre Situation Actuelle</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; color: #64748b;">Code Étudiant:</td>
                                <td style="padding: 8px 0; color: #1e293b; font-weight: bold;">{code}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #64748b;">Filière:</td>
                                <td style="padding: 8px 0; color: #1e293b; font-weight: bold;">{filiere}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #64748b;">Moyenne Générale:</td>
                                <td style="padding: 8px 0; color: #1e293b; font-weight: bold;">{moyenne:.2f}/20</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #64748b;">Modules Suivis:</td>
                                <td style="padding: 8px 0; color: #1e293b; font-weight: bold;">{nb_modules}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #64748b;">Modules en Difficulté:</td>
                                <td style="padding: 8px 0; color: #dc2626; font-weight: bold;">{modules_echec}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #64748b;">Profil:</td>
                                <td style="padding: 8px 0;">
                                    <span style="background: {couleur_profil}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">{profil}</span>
                                </td>
                            </tr>
                        </table>
                    </div>
                    
                    <!-- Recommendations -->
                    <div style="border-left: 4px solid #3b82f6; padding-left: 16px; margin: 20px 0;">
                        <h3 style="color: #1e293b; margin-top: 0; font-size: 16px;">💡 Nos Recommandations</h3>
                        <ul style="color: #475569; line-height: 1.8; padding-left: 20px;">
                            <li>Prenez contact avec le service de tutorat</li>
                            <li>Participez aux séances de soutien proposées</li>
                            <li>Consultez les ressources pédagogiques en ligne</li>
                            <li>N'hésitez pas à solliciter vos enseignants</li>
                        </ul>
                    </div>
                    
                    <!-- CTA -->
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #64748b; font-size: 14px;">
                            Pour plus d'informations, contactez le service pédagogique.
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                    <p>Ce message a été envoyé automatiquement par le Système de Soutien Pédagogique.</p>
                    <p>© 2025 - Faculté d'Ingénierie</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Sauvegarder le fichier HTML (prévisualisation)
        with open(alerte_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Envoyer l'email
        result = send_email(
            to_email=email,
            subject=f"🎓 Notification de Suivi Pédagogique - Étudiant {code}",
            html_content=html_content
        )
        
        return jsonify({
            "message": f"✅ Email {'envoyé' if result['mode'] == 'smtp' else 'simulé'} vers {email}",
            "status": "success",
            "email_sent": result['success'],
            "mode": result['mode'],
            "preview_path": str(alerte_file),
            "note": "Mode simulation - consultez /api/emails/log pour voir les emails" if result['mode'] == 'simulation' else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/alertes/module', methods=['POST', 'OPTIONS'])
def alerte_module():
    """Envoie une alerte email pour un module critique"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        module = data.get('module')
        emails = data.get('emails', [])
        
        if not module:
            return jsonify({"error": "Nom du module requis"}), 400
        
        # Vérifier si le module existe
        module_data = df[df['Module'] == module]
        if module_data.empty:
            return jsonify({"error": f"Module '{module}' non trouvé"}), 404
        
        # Calculer les statistiques
        taux_echec = module_data['Needs_Support'].mean() * 100
        moyenne = module_data['Note_sur_20'].mean()
        effectif = len(module_data)
        
        # Générer l'alerte HTML
        alertes_path = OUTPUT_PATH / "alertes"
        alertes_path.mkdir(exist_ok=True)
        
        module_safe = module[:20].replace('/', '_').replace('\\', '_')
        alerte_file = alertes_path / f"alerte_module_{module_safe}.html"
        
        # Niveau de criticité
        if taux_echec >= 70:
            niveau = "Critique"
            couleur = "#dc2626"
            emoji = "🔴"
        elif taux_echec >= 50:
            niveau = "Élevé"
            couleur = "#f97316"
            emoji = "🟠"
        else:
            niveau = "Modéré"
            couleur = "#eab308"
            emoji = "🟡"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Alerte Module Critique</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">📚 Alerte Module Critique</h1>
                    <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0 0;">Intervention pédagogique recommandée</p>
                </div>
                
                <!-- Content -->
                <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                        Cher(e) enseignant(e),
                    </p>
                    <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                        Le module suivant présente des indicateurs préoccupants nécessitant votre attention :
                    </p>
                    
                    <!-- Module Info -->
                    <div style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 12px; padding: 25px; margin: 20px 0; border-left: 5px solid {couleur};">
                        <h2 style="color: #1e293b; margin: 0 0 5px 0; font-size: 18px;">{module}</h2>
                        <span style="background: {couleur}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                            {emoji} Niveau {niveau}
                        </span>
                    </div>
                    
                    <!-- Stats -->
                    <div style="display: table; width: 100%; margin: 20px 0;">
                        <div style="display: table-cell; width: 33%; text-align: center; padding: 15px;">
                            <div style="background: #fef2f2; border-radius: 12px; padding: 20px;">
                                <div style="font-size: 32px; font-weight: bold; color: #dc2626;">{taux_echec:.1f}%</div>
                                <div style="color: #6b7280; font-size: 12px; margin-top: 5px;">Taux d'échec</div>
                            </div>
                        </div>
                        <div style="display: table-cell; width: 33%; text-align: center; padding: 15px;">
                            <div style="background: #fff7ed; border-radius: 12px; padding: 20px;">
                                <div style="font-size: 32px; font-weight: bold; color: #f97316;">{moyenne:.2f}</div>
                                <div style="color: #6b7280; font-size: 12px; margin-top: 5px;">Moyenne /20</div>
                            </div>
                        </div>
                        <div style="display: table-cell; width: 33%; text-align: center; padding: 15px;">
                            <div style="background: #eff6ff; border-radius: 12px; padding: 20px;">
                                <div style="font-size: 32px; font-weight: bold; color: #3b82f6;">{effectif}</div>
                                <div style="color: #6b7280; font-size: 12px; margin-top: 5px;">Étudiants</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recommendations -->
                    <div style="background: #f0fdf4; border-radius: 12px; padding: 20px; margin: 20px 0;">
                        <h3 style="color: #166534; margin: 0 0 15px 0; font-size: 16px;">💡 Recommandations</h3>
                        <ul style="color: #374151; margin: 0; padding-left: 20px; line-height: 1.8;">
                            <li>Organiser des séances de remédiation</li>
                            <li>Revoir les méthodes pédagogiques</li>
                            <li>Proposer des TD supplémentaires</li>
                            <li>Identifier les difficultés spécifiques</li>
                        </ul>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                    <p>Ce message a été envoyé automatiquement par le Système de Soutien Pédagogique.</p>
                    <p>© 2025 - Faculté d'Ingénierie</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Sauvegarder le fichier HTML (prévisualisation)
        with open(alerte_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Envoyer les emails
        emails_envoyes = 0
        mode = 'simulation'
        for dest_email in emails:
            result = send_email(
                to_email=dest_email,
                subject=f"🔴 Alerte Module Critique: {module[:30]}",
                html_content=html_content
            )
            if result['success']:
                emails_envoyes += 1
                mode = result['mode']
        
        return jsonify({
            "message": f"✅ {emails_envoyes} email(s) {'envoyé(s)' if mode == 'smtp' else 'simulé(s)'}",
            "status": "success",
            "email_sent": emails_envoyes > 0,
            "mode": mode,
            "emails_notifies": emails_envoyes,
            "preview_path": str(alerte_file),
            "note": "Mode simulation - consultez /api/emails/log" if mode == 'simulation' else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/alertes/rapport-hebdo', methods=['POST', 'OPTIONS'])
def alerte_rapport_hebdo():
    """Génère et envoie un rapport hebdomadaire"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email requis"}), 400
        
        # Calculer les statistiques
        nb_etudiants = df['ID'].nunique()
        nb_risque = len(df[df['Needs_Support'] == 1]['ID'].unique())
        moyenne_globale = df['Note_sur_20'].mean()
        
        # Top 5 modules critiques
        module_stats = df.groupby('Module').agg({
            'Needs_Support': 'mean'
        }).reset_index()
        module_stats['taux_echec'] = module_stats['Needs_Support'] * 100
        top_modules = module_stats.nlargest(5, 'taux_echec')
        
        # Générer le rapport
        alertes_path = OUTPUT_PATH / "alertes"
        alertes_path.mkdir(exist_ok=True)
        
        rapport_file = alertes_path / "rapport_admin_hebdomadaire.html"
        
        modules_html = "".join([
            f"""<tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{i+1}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{row['Module'][:40]}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">
                    <span style="background: {'#dc2626' if row['taux_echec'] >= 60 else '#f97316' if row['taux_echec'] >= 40 else '#eab308'}; 
                           color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;">
                        {row['taux_echec']:.1f}%
                    </span>
                </td>
            </tr>""" 
            for i, (_, row) in enumerate(top_modules.iterrows())
        ])
        
        # Calcul du pourcentage de réussite
        taux_risque = (nb_risque / nb_etudiants * 100) if nb_etudiants > 0 else 0
        taux_reussite = 100 - taux_risque
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Rapport Hebdomadaire</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc;">
            <div style="max-width: 650px; margin: 0 auto; padding: 20px;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 30px; text-align: center; border-radius: 12px 12px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">📊 Rapport Hebdomadaire</h1>
                    <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0 0;">Système de Suivi Pédagogique</p>
                    <p style="color: rgba(255,255,255,0.6); margin: 5px 0 0 0; font-size: 12px;">Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                </div>
                
                <!-- Content -->
                <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                        Cher administrateur,
                    </p>
                    <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                        Voici le rapport récapitulatif de la situation pédagogique :
                    </p>
                    
                    <!-- Stats Cards -->
                    <div style="display: table; width: 100%; margin: 25px 0;">
                        <div style="display: table-cell; width: 33%; padding: 8px;">
                            <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #bfdbfe;">
                                <div style="font-size: 36px; font-weight: bold; color: #1e40af;">{nb_etudiants:,}</div>
                                <div style="color: #6b7280; font-size: 13px; margin-top: 5px;">👨‍🎓 Étudiants</div>
                            </div>
                        </div>
                        <div style="display: table-cell; width: 33%; padding: 8px;">
                            <div style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #fecaca;">
                                <div style="font-size: 36px; font-weight: bold; color: #dc2626;">{nb_risque:,}</div>
                                <div style="color: #6b7280; font-size: 13px; margin-top: 5px;">⚠️ À risque</div>
                            </div>
                        </div>
                        <div style="display: table-cell; width: 33%; padding: 8px;">
                            <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #bbf7d0;">
                                <div style="font-size: 36px; font-weight: bold; color: #16a34a;">{moyenne_globale:.1f}</div>
                                <div style="color: #6b7280; font-size: 13px; margin-top: 5px;">📊 Moyenne /20</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Progress Bar -->
                    <div style="background: #f3f4f6; border-radius: 12px; padding: 20px; margin: 25px 0;">
                        <h3 style="color: #1e293b; margin: 0 0 15px 0; font-size: 14px;">📈 Répartition des étudiants</h3>
                        <div style="background: #e5e7eb; border-radius: 10px; height: 24px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%); width: {taux_reussite:.1f}%; height: 100%; border-radius: 10px; display: inline-block;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 13px;">
                            <span style="color: #16a34a;">✅ En bonne voie: {taux_reussite:.1f}%</span>
                            <span style="color: #dc2626;">⚠️ À risque: {taux_risque:.1f}%</span>
                        </div>
                    </div>
                    
                    <!-- Top Modules Table -->
                    <div style="margin: 25px 0;">
                        <h3 style="color: #1e293b; margin: 0 0 15px 0; font-size: 16px;">🔴 Top 5 Modules Critiques</h3>
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                            <thead>
                                <tr style="background: #f8fafc;">
                                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb; color: #64748b;">#</th>
                                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb; color: #64748b;">Module</th>
                                    <th style="padding: 12px; text-align: center; border-bottom: 2px solid #e5e7eb; color: #64748b;">Taux d'échec</th>
                                </tr>
                            </thead>
                            <tbody>
                                {modules_html}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- CTA -->
                    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); border-radius: 12px; padding: 20px; text-align: center; margin-top: 25px;">
                        <p style="color: white; margin: 0 0 15px 0; font-size: 14px;">
                            Consultez le tableau de bord pour plus de détails
                        </p>
                        <a href="http://localhost:3000" style="display: inline-block; background: white; color: #1e40af; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px;">
                            📊 Ouvrir le Dashboard
                        </a>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 12px;">
                    <p>Ce message a été envoyé automatiquement par le Système de Soutien Pédagogique.</p>
                    <p>© 2025 - Faculté d'Ingénierie</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Sauvegarder le fichier HTML (prévisualisation)
        with open(rapport_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Envoyer l'email
        result = send_email(
            to_email=email,
            subject=f"📊 Rapport Hebdomadaire de Suivi Pédagogique - {datetime.now().strftime('%d/%m/%Y')}",
            html_content=html_content
        )
        
        return jsonify({
            "message": f"✅ Rapport {'envoyé' if result['mode'] == 'smtp' else 'simulé'} vers {email}",
            "status": "success",
            "email_sent": result['success'],
            "mode": result['mode'],
            "preview_path": str(rapport_file),
            "note": "Mode simulation - consultez /api/emails/log" if result['mode'] == 'simulation' else None,
            "stats": {
                "nb_etudiants": nb_etudiants,
                "nb_risque": nb_risque,
                "moyenne": round(moyenne_globale, 2),
                "taux_risque": round(taux_risque, 1)
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# PRÉDICTION AVANCÉE : ÉTUDIANT EXISTANT + MODULE FUTUR
# =============================================================================

@app.route('/api/predict-student-module', methods=['POST'])
def predict_student_module():
    """
    🎯 PRÉDICTION INTELLIGENTE
    Prédit le risque d'échec d'un étudiant EXISTANT pour un MODULE FUTUR
    qu'il n'a pas encore passé.
    
    Utilise:
    - L'historique des notes de l'étudiant
    - La difficulté connue du module cible
    - Les performances des étudiants similaires
    - Le profil académique de l'étudiant
    """
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    data = request.json or {}
    student_id = str(data.get('student_id', ''))
    module_cible = data.get('module', '')
    
    if not student_id:
        return jsonify({"error": "student_id requis"}), 400
    
    # 1. Récupérer l'historique de l'étudiant
    student_data = df[df['ID'] == student_id]
    
    if len(student_data) == 0:
        return jsonify({"error": f"Étudiant {student_id} non trouvé"}), 404
    
    # 2. Calculer les statistiques de l'étudiant
    moyenne_etudiant = student_data['Note_sur_20'].mean()
    ecart_type_etudiant = student_data['Note_sur_20'].std()
    nb_modules_passes = len(student_data)
    nb_echecs = (student_data['Needs_Support'] == 1).sum()
    taux_echec_etudiant = nb_echecs / nb_modules_passes * 100
    filiere = student_data['Filiere'].iloc[0]
    note_min = student_data['Note_sur_20'].min()
    note_max = student_data['Note_sur_20'].max()
    
    # Modules déjà passés par l'étudiant
    modules_passes = student_data['Module'].unique().tolist()
    
    # 3. Analyser le module cible (si spécifié)
    module_info = {}
    module_taux_echec = 50  # Valeur par défaut
    module_moyenne = 10
    
    if module_cible:
        # regex=False pour éviter les erreurs avec les caractères spéciaux (arabe, etc.)
        module_data = df[df['Module'].str.contains(module_cible, case=False, na=False, regex=False)]
        if len(module_data) > 0:
            module_taux_echec = (module_data['Needs_Support'].mean()) * 100
            module_moyenne = module_data['Note_sur_20'].mean()
            module_nb_etudiants = len(module_data)
            
            # Voir si des étudiants similaires (même filière) ont passé ce module
            module_filiere_data = module_data[module_data['Filiere'] == filiere]
            if len(module_filiere_data) > 0:
                module_taux_echec_filiere = (module_filiere_data['Needs_Support'].mean()) * 100
                module_moyenne_filiere = module_filiere_data['Note_sur_20'].mean()
            else:
                module_taux_echec_filiere = module_taux_echec
                module_moyenne_filiere = module_moyenne
            
            module_info = {
                "nom": str(module_cible),
                "taux_echec_global": round(float(module_taux_echec), 1),
                "taux_echec_filiere": round(float(module_taux_echec_filiere), 1),
                "moyenne_module": round(float(module_moyenne), 2),
                "moyenne_module_filiere": round(float(module_moyenne_filiere), 2),
                "nb_etudiants_passes": int(module_nb_etudiants),
                "deja_passe": bool(module_cible in str(modules_passes))
            }
    
    # 4. 🧠 PRÉDICTION ML RÉELLE
    ml_result, ml_error = predict_with_ml_model(student_data, module_cible)
    
    if ml_result is not None:
        # Utiliser les résultats du modèle ML
        probabilite_risque = ml_result['probabilite']
        profil_ml = ml_result['profil_ml']
        prediction_ml = ml_result['prediction']
        features_used = ml_result['features_used']
        using_ml = True
    else:
        # Fallback vers les heuristiques si le modèle ML échoue
        print(f"⚠️ ML Error: {ml_error}, using heuristics")
        
        # Score basé sur la moyenne de l'étudiant (0-1, 1 = risque max)
        if moyenne_etudiant >= 14:
            score_etudiant = 0.05
        elif moyenne_etudiant >= 12:
            score_etudiant = 0.15
        elif moyenne_etudiant >= 10:
            score_etudiant = 0.35
        elif moyenne_etudiant >= 7:
            score_etudiant = 0.60
        else:
            score_etudiant = 0.85
        
        # Score basé sur la difficulté du module (0-1)
        score_module = module_taux_echec / 100
        
        # Score basé sur la tendance de l'étudiant
        if ecart_type_etudiant > 5:
            score_stabilite = 0.2
        elif ecart_type_etudiant > 3:
            score_stabilite = 0.1
        else:
            score_stabilite = 0
        
        probabilite_risque = (
            score_etudiant * 0.5 +
            score_module * 0.35 +
            score_stabilite * 0.15
        )
        probabilite_risque = min(0.99, max(0.01, probabilite_risque))
        profil_ml = None
        prediction_ml = 1 if probabilite_risque >= 0.5 else 0
        features_used = 0
        using_ml = False
    
    # 5. Catégoriser le risque
    if probabilite_risque >= 0.7:
        categorie = "CRITIQUE"
        color = "red"
        emoji = "🔴"
        recommandations = [
            "🚨 Tutorat individuel FORTEMENT recommandé",
            "📞 Rencontre avec le conseiller pédagogique",
            "📚 Révision intensive des prérequis",
            "👥 Inscription groupe de soutien"
        ]
    elif probabilite_risque >= 0.5:
        categorie = "ÉLEVÉ"
        color = "orange"
        emoji = "🟠"
        recommandations = [
            "📝 TD de soutien recommandé",
            "📅 Suivi régulier conseillé",
            "📖 Renforcement des fondamentaux"
        ]
    elif probabilite_risque >= 0.3:
        categorie = "MODÉRÉ"
        color = "yellow"
        emoji = "🟡"
        recommandations = [
            "📚 Travail personnel régulier",
            "💻 Utilisation des ressources en ligne",
            "👥 Travail en groupe recommandé"
        ]
    else:
        categorie = "FAIBLE"
        color = "green"
        emoji = "🟢"
        recommandations = [
            "✅ Continuer sur cette lancée",
            "📈 Possibilité de tutorat pair"
        ]
    
    # 6. Prédiction de la note estimée
    # Basée sur la moyenne de l'étudiant ajustée par la difficulté du module
    note_predite = moyenne_etudiant * (1 - (module_taux_echec/100) * 0.3)
    note_predite = max(0, min(20, note_predite))
    
    # 7. Profil de l'étudiant
    profil = get_profil(moyenne_etudiant)
    
    # Convertir les types numpy en types Python natifs pour JSON
    # Construire la réponse avec les infos ML
    response_data = {
        "etudiant": {
            "id": student_id,
            "filiere": str(filiere),
            "moyenne_generale": round(float(moyenne_etudiant), 2),
            "ecart_type": round(float(ecart_type_etudiant), 2) if not pd.isna(ecart_type_etudiant) else 0,
            "nb_modules_passes": int(nb_modules_passes),
            "nb_echecs": int(nb_echecs),
            "taux_echec": round(float(taux_echec_etudiant), 1),
            "note_min": round(float(note_min), 1),
            "note_max": round(float(note_max), 1),
            "profil": profil
        },
        "module_cible": module_info,
        "prediction": {
            "probabilite_risque": round(float(probabilite_risque * 100), 1),
            "categorie": categorie,
            "color": color,
            "emoji": emoji,
            "note_estimee": round(float(note_predite), 1),
            "besoin_soutien": bool(probabilite_risque >= 0.5),
            "using_ml_model": using_ml,
            "profil_ml": profil_ml,
            "features_used": features_used
        },
        "recommandations": recommandations,
        "modules_passes": [str(m) for m in modules_passes[:10]]  # Limiter à 10
    }
    
    return jsonify(response_data)


@app.route('/api/students/search', methods=['GET'])
def search_students():
    """Recherche d'étudiants par ID partiel"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    query = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not query or len(query) < 2:
        return jsonify({"students": []})
    
    # Chercher les IDs qui contiennent la requête
    matching_ids = df[df['ID'].str.contains(query, case=False, na=False)]['ID'].unique()[:limit]
    
    students = []
    for sid in matching_ids:
        student_data = df[df['ID'] == sid]
        moyenne = student_data['Note_sur_20'].mean()
        filiere = student_data['Filiere'].iloc[0]
        students.append({
            "id": sid,
            "filiere": filiere,
            "moyenne": round(moyenne, 2),
            "nb_modules": len(student_data),
            "profil": get_profil(moyenne)['nom']
        })
    
    return jsonify({"students": students})


@app.route('/api/modules/search', methods=['GET'])
def search_modules():
    """Recherche de modules par nom partiel"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    query = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not query or len(query) < 2:
        return jsonify({"modules": []})
    
    # Chercher les modules qui contiennent la requête
    matching_modules = df[df['Module'].str.contains(query, case=False, na=False)]['Module'].unique()[:limit]
    
    modules = []
    for mod in matching_modules:
        mod_data = df[df['Module'] == mod]
        taux_echec = mod_data['Needs_Support'].mean() * 100
        moyenne = mod_data['Note_sur_20'].mean()
        modules.append({
            "nom": mod,
            "nom_fr": traduire_module(mod),
            "taux_echec": round(taux_echec, 1),
            "moyenne": round(moyenne, 2),
            "nb_etudiants": len(mod_data)
        })
    
    return jsonify({"modules": modules})


@app.route('/api/students/<student_id>/modules-non-passes', methods=['GET'])
def get_modules_non_passes(student_id):
    """Retourne les modules que l'étudiant n'a pas encore passés"""
    if df is None:
        return jsonify({"error": "Données non chargées"}), 500
    
    # Vérifier que l'étudiant existe
    student_data = df[df['ID'] == student_id]
    if student_data.empty:
        return jsonify({"error": "Étudiant non trouvé"}), 404
    
    # Récupérer la filière de l'étudiant
    filiere = student_data['Filiere'].iloc[0]
    
    # Modules déjà passés par l'étudiant
    modules_passes = set(student_data['Module'].unique())
    
    # Tous les modules de la même filière
    modules_filiere = df[df['Filiere'] == filiere]['Module'].unique()
    
    # Modules non passés = modules de la filière - modules passés
    modules_non_passes = [m for m in modules_filiere if m not in modules_passes]
    
    # Calculer les stats pour chaque module non passé
    result = []
    for mod in modules_non_passes:
        mod_data = df[df['Module'] == mod]
        mod_filiere_data = df[(df['Module'] == mod) & (df['Filiere'] == filiere)]
        
        taux_echec_global = mod_data['Needs_Support'].mean() * 100 if len(mod_data) > 0 else 50
        taux_echec_filiere = mod_filiere_data['Needs_Support'].mean() * 100 if len(mod_filiere_data) > 0 else taux_echec_global
        moyenne = mod_data['Note_sur_20'].mean() if len(mod_data) > 0 else 10
        
        result.append({
            "nom": str(mod),
            "nom_fr": traduire_module(mod),
            "taux_echec": round(float(taux_echec_global), 1),
            "taux_echec_filiere": round(float(taux_echec_filiere), 1),
            "moyenne": round(float(moyenne), 2),
            "nb_etudiants": int(len(mod_data)),
            "difficulte": "Difficile" if taux_echec_global >= 50 else "Modéré" if taux_echec_global >= 30 else "Facile"
        })
    
    # Trier par taux d'échec décroissant (modules les plus difficiles en premier)
    result.sort(key=lambda x: x['taux_echec'], reverse=True)
    
    return jsonify({
        "etudiant_id": student_id,
        "filiere": filiere,
        "nb_modules_passes": len(modules_passes),
        "nb_modules_restants": len(result),
        "modules": result
    })


# =============================================================================
# ROUTES ASSISTANT IA - CHATBOT OPENAI
# =============================================================================
@app.route('/api/chat/welcome', methods=['GET'])
def chat_welcome():
    """Message de bienvenue de l'assistant"""
    if assistant_ia is None:
        return jsonify({"error": "Assistant IA non disponible"}), 503
    
    return jsonify({
        'message': assistant_ia.get_welcome_message(),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """
    Envoie un message à l'assistant IA et retourne la réponse
    
    Body JSON:
    {
        "message": "Votre question",
        "history": [{"role": "user", "content": "..."}, ...],  # Optionnel
        "context": "Contexte additionnel"  # Optionnel
    }
    """
    if assistant_ia is None:
        return jsonify({"error": "Assistant IA non disponible. Vérifiez la clé OpenAI."}), 503
    
    try:
        data = request.json
        message = data.get('message', '')
        history = data.get('history', [])
        context = data.get('context', None)
        
        if not message:
            return jsonify({"error": "Message requis"}), 400
        
        # Appeler l'assistant IA
        result = assistant_ia.chat(
            message=message,
            history=history,
            context=context
        )
        
        if not result['success']:
            return jsonify({
                "error": "Erreur lors de l'appel à l'API OpenAI",
                "details": result.get('error', 'Erreur inconnue')
            }), 500
        
        return jsonify({
            'response': result['response'],
            'tokens_used': result['tokens_used'],
            'cost': result['cost'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chat/stats', methods=['GET'])
def chat_stats():
    """Retourne des statistiques sur l'utilisation de l'assistant IA"""
    if assistant_ia is None:
        return jsonify({"error": "Assistant IA non disponible"}), 503
    
    return jsonify({
        'model': assistant_ia.model,
        'available': True,
        'total_students': df['ID'].nunique() if df is not None and 'ID' in df.columns else 0,
        'total_modules': df['Module'].nunique() if df is not None and 'Module' in df.columns else 0
    })


# ROUTE DE TEST SIMPLE POUR EMAIL
@app.route('/api/alertes/test-email', methods=['POST', 'GET'])
def test_email_simple():
    """Route de test simple pour vérifier l'envoi d'emails avec données complètes"""
    try:
        if request.method == 'GET':
            return jsonify({"message": "Route accessible. Utilisez POST pour envoyer un email."})
        
        # Récupérer les données
        data = request.get_json() if request.is_json else {}
        code_etudiant = data.get('code', '')
        email_dest = data.get('email', os.getenv('SENDER_EMAIL'))
        
        # Configuration email depuis .env
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')
        
        if not sender_email or not sender_password:
            return jsonify({
                "error": "Configuration email manquante",
                "sender_configured": bool(sender_email),
                "password_configured": bool(sender_password)
            }), 500
        
        # Récupérer les données de l'étudiant
        if code_etudiant and code_etudiant in df['ID'].astype(str).values:
            student_data = df[df['ID'].astype(str) == code_etudiant]
            
            # Calculer les statistiques
            moyenne = student_data['Note_sur_20'].mean()
            filiere = student_data['Filiere'].iloc[0] if 'Filiere' in student_data.columns else 'N/A'
            nb_modules = len(student_data)
            nb_echecs = len(student_data[student_data['Needs_Support'] == 1]) if 'Needs_Support' in student_data.columns else 0
            
            # Déterminer le profil
            if moyenne >= 14:
                profil = "Excellence"
                couleur = "#10B981"
                emoji = "⭐"
                niveau_risque = "Faible"
            elif moyenne >= 12:
                profil = "Régulier"
                couleur = "#3B82F6"
                emoji = "✅"
                niveau_risque = "Faible"
            elif moyenne >= 10:
                profil = "Passable"
                couleur = "#F59E0B"
                emoji = "⚠️"
                niveau_risque = "Modéré"
            else:
                profil = "En Difficulté"
                couleur = "#EF4444"
                emoji = "🔴"
                niveau_risque = "Élevé"
            
            # Modules à risque
            modules_risque = student_data[student_data['Needs_Support'] == 1] if 'Needs_Support' in student_data.columns else pd.DataFrame()
            modules_risque_html = ""
            if len(modules_risque) > 0:
                for _, module in modules_risque.head(5).iterrows():
                    module_nom = module.get('Module', 'N/A')
                    note = module.get('Note_sur_20', 0)
                    modules_risque_html += f"""
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{module_nom}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; color: #EF4444; font-weight: bold;">{note:.1f}/20</td>
                    </tr>
                    """
            else:
                modules_risque_html = "<tr><td colspan='2' style='padding: 15px; text-align: center; color: #10B981;'>✅ Aucun module à risque</td></tr>"
            
            # Recommandations personnalisées
            if niveau_risque == "Élevé":
                recommandations = """
                <li>📌 <strong>Tutorat individuel URGENT</strong> - Inscription immédiate recommandée</li>
                <li>📚 Révision complète des bases avec un conseiller pédagogique</li>
                <li>👥 Intégration dans un groupe de soutien</li>
                <li>📅 Suivi hebdomadaire obligatoire</li>
                <li>📖 Ressources pédagogiques supplémentaires disponibles</li>
                """
            elif niveau_risque == "Modéré":
                recommandations = """
                <li>📌 <strong>TD de soutien recommandés</strong> - Inscription conseillée</li>
                <li>📚 Révision ciblée des modules faibles</li>
                <li>👥 Travail en groupe avec des étudiants performants</li>
                <li>📅 Suivi mensuel avec le tuteur</li>
                """
            else:
                recommandations = """
                <li>✅ <strong>Maintenir l'effort actuel</strong></li>
                <li>📚 Continuer le rythme de travail</li>
                <li>📖 Ressources d'approfondissement disponibles</li>
                <li>🎯 Possibilité de tutorat pair (aider d'autres étudiants)</li>
                """
            
            # Template email HTML complet
            html = f"""
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1f2937; margin: 0; padding: 0; background-color: #f3f4f6;">
                <div style="max-width: 600px; margin: 30px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">🎓 Alerte Soutien Pédagogique</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Système de Recommandation Intelligent</p>
                    </div>
                    
                    <!-- Profil Étudiant -->
                    <div style="padding: 30px;">
                        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                            <h2 style="color: #1e40af; margin: 0 0 15px 0; font-size: 20px;">
                                {emoji} Profil : {profil}
                            </h2>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; color: #6b7280;"><strong>Code Étudiant:</strong></td>
                                    <td style="padding: 8px 0; text-align: right; font-weight: bold;">{code_etudiant}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; color: #6b7280;"><strong>Filière:</strong></td>
                                    <td style="padding: 8px 0; text-align: right; font-weight: bold;">{filiere}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; color: #6b7280;"><strong>Moyenne Générale:</strong></td>
                                    <td style="padding: 8px 0; text-align: right; font-weight: bold; color: {couleur}; font-size: 18px;">{moyenne:.2f}/20</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; color: #6b7280;"><strong>Nombre de Modules:</strong></td>
                                    <td style="padding: 8px 0; text-align: right; font-weight: bold;">{nb_modules}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; color: #6b7280;"><strong>Niveau de Risque:</strong></td>
                                    <td style="padding: 8px 0; text-align: right; font-weight: bold; color: {couleur};">{niveau_risque}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <!-- Modules à Risque -->
                        <div style="margin: 25px 0;">
                            <h3 style="color: #1f2937; margin: 0 0 15px 0; font-size: 18px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px;">
                                📊 Modules Nécessitant Attention ({nb_echecs})
                            </h3>
                            <table style="width: 100%; border-collapse: collapse; background: #f9fafb; border-radius: 8px; overflow: hidden;">
                                <thead>
                                    <tr style="background: #f3f4f6;">
                                        <th style="padding: 12px; text-align: left; color: #374151; font-weight: 600;">Module</th>
                                        <th style="padding: 12px; text-align: left; color: #374151; font-weight: 600;">Note</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {modules_risque_html}
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- Recommandations -->
                        <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 20px; border-radius: 8px; margin: 25px 0;">
                            <h3 style="color: #92400e; margin: 0 0 15px 0; font-size: 18px; display: flex; align-items: center;">
                                💡 Recommandations Personnalisées
                            </h3>
                            <ul style="margin: 0; padding-left: 20px; color: #78350f;">
                                {recommandations}
                            </ul>
                        </div>
                        
                        <!-- Call to Action -->
                        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 20px; border-radius: 10px; text-align: center; margin: 25px 0;">
                            <h3 style="color: white; margin: 0 0 10px 0;">🚀 Prochaines Étapes</h3>
                            <p style="color: rgba(255,255,255,0.95); margin: 0 0 15px 0;">
                                Contactez votre tuteur pédagogique pour mettre en place un plan d'action personnalisé.
                            </p>
                            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 14px;">
                                📧 Email : tuteur@universite.ma<br>
                                📞 Tél : +212 XXX XXX XXX
                            </p>
                        </div>
                        
                        <!-- Footer -->
                        <div style="border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 30px; text-align: center; color: #6b7280; font-size: 12px;">
                            <p style="margin: 5px 0;">
                                <strong>Système de Soutien Pédagogique</strong><br>
                                Université Marocaine • Propulsé par IA
                            </p>
                            <p style="margin: 10px 0; font-size: 11px; color: #9ca3af;">
                                Ce message est généré automatiquement par notre système de prédiction ML.<br>
                                Précision du modèle : 99.96% • Basé sur 43 critères d'analyse
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
        else:
            # Si étudiant non trouvé, email basique
            html = f"""
            <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #EF4444;">⚠️ Étudiant non trouvé</h2>
                <p>Le code étudiant <strong>{code_etudiant}</strong> n'existe pas dans la base de données.</p>
                <p>Email envoyé à : {email_dest}</p>
            </body>
            </html>
            """
        
        # Créer et envoyer l'email
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Soutien Pédagogique <{sender_email}>"
        msg['To'] = email_dest
        msg['Subject'] = f"🎓 Alerte Soutien - Étudiant {code_etudiant}"
        msg.attach(MIMEText(html, 'html'))
        
        # Envoyer via Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return jsonify({
            "success": True,
            "message": f"Email complet envoyé avec succès à {email_dest}",
            "from": sender_email,
            "to": email_dest,
            "etudiant": code_etudiant
        })
        
    except smtplib.SMTPAuthenticationError as e:
        return jsonify({
            "error": "Erreur d'authentification Gmail",
            "details": "Vérifiez le mot de passe d'application",
            "smtp_error": str(e)
        }), 401
    except Exception as e:
        return jsonify({
            "error": "Erreur lors de l'envoi",
            "details": str(e)
        }), 500


# =============================================================================
# DÉMARRAGE
# =============================================================================

if __name__ == '__main__':
    load_data()
    print("\n🚀 API démarrée sur http://localhost:5000")
    app.run(debug=True, port=5000)
