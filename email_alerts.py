# -*- coding: utf-8 -*-
"""
📧 Système d'Alertes Email - Soutien Pédagogique
=================================================
Envoie des alertes automatiques aux étudiants, enseignants et administration
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import os

OUTPUT_PATH = Path("output_projet4")
ALERTS_PATH = OUTPUT_PATH / "alertes"
ALERTS_PATH.mkdir(exist_ok=True)

# =============================================================================
# CONFIGURATION EMAIL (À personnaliser)
# =============================================================================

EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # Serveur SMTP
    'smtp_port': 587,                  # Port TLS
    'sender_email': 'votre.email@gmail.com',  # Email expéditeur
    'sender_password': 'votre_mot_de_passe_app',  # Mot de passe d'application
    'admin_email': 'admin@universite.ma',  # Email administration
}

# =============================================================================
# TEMPLATES D'EMAILS
# =============================================================================

def get_student_alert_template(student_data):
    """
    Template d'email pour alerter un étudiant à risque
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; }}
            .alert-box {{ background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
            .alert-box.warning {{ background: #fffbeb; border-left-color: #f59e0b; }}
            .stats-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .stats-table th, .stats-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
            .stats-table th {{ background: #1e40af; color: white; }}
            .stats-table tr:nth-child(even) {{ background: #f1f5f9; }}
            .button {{ display: inline-block; background: #1e40af; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin-top: 20px; }}
            .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
            .profil-badge {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
            .profil-risque {{ background: #fecaca; color: #dc2626; }}
            .profil-difficulte {{ background: #fed7aa; color: #ea580c; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 Service de Soutien Pédagogique</h1>
                <p>Université - Département {student_data['filiere']}</p>
            </div>
            
            <div class="content">
                <h2>Bonjour,</h2>
                
                <p>Nous avons analysé vos résultats académiques et souhaitons vous informer de votre situation actuelle.</p>
                
                <div class="alert-box">
                    <strong>⚠️ Attention requise</strong>
                    <p>Votre profil actuel nécessite un accompagnement pédagogique renforcé.</p>
                </div>
                
                <h3>📊 Votre Situation Actuelle</h3>
                
                <table class="stats-table">
                    <tr>
                        <th>Indicateur</th>
                        <th>Valeur</th>
                    </tr>
                    <tr>
                        <td>Moyenne Générale</td>
                        <td><strong>{student_data['moyenne']:.2f}/20</strong></td>
                    </tr>
                    <tr>
                        <td>Modules en Difficulté</td>
                        <td>{student_data['modules_echec']} sur {student_data['nb_modules']}</td>
                    </tr>
                    <tr>
                        <td>Profil</td>
                        <td><span class="profil-badge profil-{student_data['profil_class']}">{student_data['profil']}</span></td>
                    </tr>
                    <tr>
                        <td>Score de Risque</td>
                        <td>{student_data['score_risque']:.0%}</td>
                    </tr>
                </table>
                
                <h3>💡 Recommandations</h3>
                <ul>
                    {student_data['recommandations_html']}
                </ul>
                
                <h3>📅 Prochaines Étapes</h3>
                <p>Nous vous invitons à:</p>
                <ol>
                    <li>Prendre rendez-vous avec votre conseiller pédagogique</li>
                    <li>Vous inscrire aux TD de soutien disponibles</li>
                    <li>Consulter les ressources en ligne sur la plateforme</li>
                </ol>
                
                <center>
                    <a href="#" class="button">📞 Contacter le Service Pédagogique</a>
                </center>
            </div>
            
            <div class="footer">
                <p>Ce message a été généré automatiquement par le Système de Soutien Pédagogique.</p>
                <p>© {datetime.now().year} - Université - Service Pédagogique</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def get_teacher_alert_template(module_data):
    """
    Template d'email pour alerter un enseignant sur un module critique
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; }}
            .alert-box {{ background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .stat-value {{ font-size: 28px; font-weight: bold; color: #1e40af; }}
            .stat-label {{ font-size: 12px; color: #64748b; text-transform: uppercase; }}
            .student-list {{ background: white; padding: 15px; border-radius: 10px; margin: 20px 0; }}
            .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>👨‍🏫 Alerte Module - Soutien Pédagogique</h1>
                <p>Rapport pour le module: {module_data['module']}</p>
            </div>
            
            <div class="content">
                <h2>Cher(e) Enseignant(e),</h2>
                
                <p>Le système de soutien pédagogique a détecté un taux d'échec élevé dans votre module.</p>
                
                <div class="alert-box">
                    <strong>🔴 Module Critique</strong>
                    <p>Le taux d'échec de <strong>{module_data['taux_echec']:.1f}%</strong> dépasse le seuil d'alerte de 50%.</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{module_data['nb_etudiants']}</div>
                        <div class="stat-label">Étudiants inscrits</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{module_data['nb_echec']}</div>
                        <div class="stat-label">En difficulté</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{module_data['moyenne']:.1f}/20</div>
                        <div class="stat-label">Moyenne du module</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{module_data['taux_echec']:.0f}%</div>
                        <div class="stat-label">Taux d'échec</div>
                    </div>
                </div>
                
                <h3>📋 Actions Suggérées</h3>
                <ul>
                    <li>Organiser des TD de soutien supplémentaires</li>
                    <li>Identifier les points de blocage avec les étudiants</li>
                    <li>Proposer des ressources complémentaires</li>
                    <li>Envisager des sessions de révision avant les examens</li>
                </ul>
                
                <div class="student-list">
                    <h4>👥 Étudiants Prioritaires (Top 10)</h4>
                    <p>{module_data['etudiants_prioritaires']}</p>
                </div>
            </div>
            
            <div class="footer">
                <p>Ce message a été généré automatiquement par le Système de Soutien Pédagogique.</p>
                <p>© {datetime.now().year} - Université - Service Pédagogique</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def get_admin_report_template(report_data):
    """
    Template d'email pour le rapport hebdomadaire à l'administration
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0f172a, #1e293b); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; }}
            .summary-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
            .summary-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .summary-value {{ font-size: 32px; font-weight: bold; }}
            .summary-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; margin-top: 5px; }}
            .green {{ color: #16a34a; }}
            .orange {{ color: #ea580c; }}
            .red {{ color: #dc2626; }}
            .section {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            .section h3 {{ color: #1e40af; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
            th {{ background: #f1f5f9; font-size: 12px; text-transform: uppercase; }}
            .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; text-align: center; font-size: 12px; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Rapport Hebdomadaire - Soutien Pédagogique</h1>
                <p>Semaine du {report_data['date_debut']} au {report_data['date_fin']}</p>
            </div>
            
            <div class="content">
                <h2>Vue d'Ensemble</h2>
                
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="summary-value">{report_data['nb_etudiants']:,}</div>
                        <div class="summary-label">Étudiants suivis</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-value red">{report_data['nb_critiques']}</div>
                        <div class="summary-label">À risque critique</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-value orange">{report_data['nb_difficulte']}</div>
                        <div class="summary-label">En difficulté</div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>🎓 Performance par Filière</h3>
                    <table>
                        <tr>
                            <th>Filière</th>
                            <th>Étudiants</th>
                            <th>Moyenne</th>
                            <th>Taux Échec</th>
                            <th>Statut</th>
                        </tr>
                        {report_data['filieres_html']}
                    </table>
                </div>
                
                <div class="section">
                    <h3>🔴 Modules Critiques</h3>
                    <table>
                        <tr>
                            <th>Module</th>
                            <th>Filière</th>
                            <th>Taux Échec</th>
                            <th>Étudiants</th>
                        </tr>
                        {report_data['modules_critiques_html']}
                    </table>
                </div>
                
                <div class="section">
                    <h3>📋 Actions Requises</h3>
                    <ul>
                        <li>✅ Convoquer les <strong>{report_data['nb_critiques']}</strong> étudiants à risque critique</li>
                        <li>✅ Ouvrir <strong>{report_data['nb_modules_critiques']}</strong> TD de soutien supplémentaires</li>
                        <li>✅ Affecter <strong>{report_data['tuteurs_necessaires']}</strong> tuteurs</li>
                        <li>✅ Budget estimé: <strong>{report_data['budget_estime']} DH</strong></li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>Rapport généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                <p>© {datetime.now().year} - Université - Système de Soutien Pédagogique</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


# =============================================================================
# FONCTIONS D'ENVOI D'EMAILS
# =============================================================================

def send_email(to_email, subject, html_content, attachments=None):
    """
    Envoie un email avec le contenu HTML
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = to_email
        
        # Corps HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Pièces jointes
        if attachments:
            for filepath in attachments:
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(filepath)}"')
                        msg.attach(part)
        
        # Connexion et envoi
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"❌ Erreur d'envoi: {e}")
        return False


def save_email_preview(filename, html_content):
    """
    Sauvegarde un aperçu HTML de l'email (pour test sans envoi)
    """
    preview_path = ALERTS_PATH / filename
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return preview_path


# =============================================================================
# GÉNÉRATION DES ALERTES
# =============================================================================

def generate_student_alerts(df, preview_only=True):
    """
    Génère les alertes pour les étudiants à risque
    """
    print("\n📧 Génération des alertes étudiants...")
    
    # Calculer les statistiques par étudiant
    student_stats = df.groupby('ID').agg({
        'Note_sur_20': 'mean',
        'Filiere': 'first',
        'Needs_Support': ['sum', 'count']
    }).reset_index()
    student_stats.columns = ['ID', 'moyenne', 'filiere', 'modules_echec', 'nb_modules']
    
    # Filtrer les étudiants à risque
    students_risque = student_stats[student_stats['moyenne'] < 10].sort_values('moyenne')
    
    print(f"   • {len(students_risque)} étudiants à alerter")
    
    alerts_generated = []
    
    for _, student in students_risque.head(20).iterrows():  # Limiter à 20 pour le test
        # Déterminer le profil
        if student['moyenne'] < 7:
            profil = "À Risque"
            profil_class = "risque"
            recommandations = [
                "<li>Convocation urgente avec le conseiller pédagogique</li>",
                "<li>Tutorat individuel obligatoire (2h/semaine minimum)</li>",
                "<li>Contrat pédagogique personnalisé à signer</li>",
                "<li>Suivi psychologique disponible si besoin</li>"
            ]
        else:
            profil = "En Difficulté"
            profil_class = "difficulte"
            recommandations = [
                "<li>Inscription aux TD de soutien recommandée</li>",
                "<li>Participation aux groupes de travail</li>",
                "<li>Exercices supplémentaires disponibles en ligne</li>"
            ]
        
        score_risque = min(0.99, student['modules_echec']/student['nb_modules'] + (10-student['moyenne'])/20)
        
        student_data = {
            'id': student['ID'],
            'filiere': student['filiere'],
            'moyenne': student['moyenne'],
            'modules_echec': int(student['modules_echec']),
            'nb_modules': int(student['nb_modules']),
            'profil': profil,
            'profil_class': profil_class,
            'score_risque': score_risque,
            'recommandations_html': '\n'.join(recommandations)
        }
        
        html_content = get_student_alert_template(student_data)
        
        if preview_only:
            # Sauvegarder l'aperçu
            preview_file = save_email_preview(f"alerte_etudiant_{student['ID']}.html", html_content)
            alerts_generated.append({
                'type': 'student',
                'id': student['ID'],
                'preview': str(preview_file)
            })
        else:
            # Envoyer l'email (nécessite configuration)
            # send_email(student_email, f"[URGENT] Alerte Pédagogique - {student['ID']}", html_content)
            pass
    
    return alerts_generated


def generate_module_alerts(df, preview_only=True):
    """
    Génère les alertes pour les modules critiques
    """
    print("\n📧 Génération des alertes modules...")
    
    # Statistiques par module
    module_stats = df.groupby(['Module', 'Filiere']).agg({
        'Note_sur_20': 'mean',
        'Needs_Support': ['sum', 'count'],
        'ID': 'nunique'
    }).reset_index()
    module_stats.columns = ['module', 'filiere', 'moyenne', 'nb_echec', 'total', 'nb_etudiants']
    module_stats['taux_echec'] = module_stats['nb_echec'] / module_stats['total'] * 100
    
    # Filtrer les modules critiques (taux > 50%)
    modules_critiques = module_stats[module_stats['taux_echec'] >= 50].sort_values('taux_echec', ascending=False)
    
    print(f"   • {len(modules_critiques)} modules critiques à alerter")
    
    alerts_generated = []
    
    for _, module in modules_critiques.head(10).iterrows():
        # Étudiants prioritaires
        module_df = df[(df['Module'] == module['module']) & (df['Filiere'] == module['filiere'])]
        etudiants_echec = module_df[module_df['Needs_Support'] == 1].nsmallest(10, 'Note_sur_20')
        etudiants_list = ', '.join([f"ID: {row['ID']} ({row['Note_sur_20']:.1f}/20)" for _, row in etudiants_echec.iterrows()])
        
        module_data = {
            'module': module['module'][:50],
            'filiere': module['filiere'],
            'moyenne': module['moyenne'],
            'nb_etudiants': int(module['nb_etudiants']),
            'nb_echec': int(module['nb_echec']),
            'taux_echec': module['taux_echec'],
            'etudiants_prioritaires': etudiants_list or 'Aucun étudiant identifié'
        }
        
        html_content = get_teacher_alert_template(module_data)
        
        if preview_only:
            safe_name = module['module'][:20].replace('/', '_').replace('\\', '_')
            preview_file = save_email_preview(f"alerte_module_{module['filiere']}_{safe_name}.html", html_content)
            alerts_generated.append({
                'type': 'module',
                'module': module['module'],
                'filiere': module['filiere'],
                'preview': str(preview_file)
            })
    
    return alerts_generated


def generate_admin_report(df, preview_only=True):
    """
    Génère le rapport hebdomadaire pour l'administration
    """
    print("\n📧 Génération du rapport administration...")
    
    # Statistiques générales
    nb_etudiants = df['ID'].nunique()
    
    student_stats = df.groupby('ID')['Note_sur_20'].mean().reset_index()
    nb_critiques = len(student_stats[student_stats['Note_sur_20'] < 7])
    nb_difficulte = len(student_stats[(student_stats['Note_sur_20'] >= 7) & (student_stats['Note_sur_20'] < 10)])
    
    # Par filière
    filiere_stats = df.groupby('Filiere').agg({
        'ID': 'nunique',
        'Note_sur_20': 'mean',
        'Needs_Support': 'mean'
    }).reset_index()
    
    filieres_html = ""
    for _, row in filiere_stats.iterrows():
        taux = row['Needs_Support'] * 100
        if taux >= 60:
            statut = '<span style="color: #dc2626;">🔴 Critique</span>'
        elif taux >= 45:
            statut = '<span style="color: #ea580c;">🟠 Attention</span>'
        else:
            statut = '<span style="color: #16a34a;">🟢 Normal</span>'
        
        filieres_html += f"""
        <tr>
            <td>{row['Filiere']}</td>
            <td>{row['ID']}</td>
            <td>{row['Note_sur_20']:.1f}/20</td>
            <td>{taux:.1f}%</td>
            <td>{statut}</td>
        </tr>
        """
    
    # Modules critiques
    module_stats = df.groupby('Module').agg({
        'Filiere': 'first',
        'Needs_Support': 'mean',
        'ID': 'count'
    }).reset_index()
    module_stats['taux'] = module_stats['Needs_Support'] * 100
    modules_crit = module_stats[module_stats['taux'] >= 50].nlargest(10, 'taux')
    
    modules_html = ""
    for _, row in modules_crit.iterrows():
        module_name = str(row['Module'])[:30] + ('...' if len(str(row['Module'])) > 30 else '')
        modules_html += f"""
        <tr>
            <td>{module_name}</td>
            <td>{row['Filiere']}</td>
            <td style="color: #dc2626;">{row['taux']:.1f}%</td>
            <td>{row['ID']}</td>
        </tr>
        """
    
    tuteurs = max(1, (nb_critiques + nb_difficulte) // 15)
    
    report_data = {
        'date_debut': (datetime.now().replace(day=1)).strftime('%d/%m/%Y'),
        'date_fin': datetime.now().strftime('%d/%m/%Y'),
        'nb_etudiants': nb_etudiants,
        'nb_critiques': nb_critiques,
        'nb_difficulte': nb_difficulte,
        'filieres_html': filieres_html,
        'modules_critiques_html': modules_html,
        'nb_modules_critiques': len(modules_crit),
        'tuteurs_necessaires': tuteurs,
        'budget_estime': tuteurs * 200
    }
    
    html_content = get_admin_report_template(report_data)
    
    if preview_only:
        preview_file = save_email_preview("rapport_admin_hebdomadaire.html", html_content)
        print(f"   ✅ Rapport admin généré: {preview_file}")
        return str(preview_file)
    else:
        # Envoyer à l'admin
        # send_email(EMAIL_CONFIG['admin_email'], "[Rapport] Soutien Pédagogique - Semaine", html_content)
        pass


def generate_all_alerts():
    """
    Génère toutes les alertes (mode aperçu)
    """
    print("=" * 60)
    print("📧 SYSTÈME D'ALERTES EMAIL - SOUTIEN PÉDAGOGIQUE")
    print("=" * 60)
    
    # Charger les données
    RAW_PATH = Path("raw")
    df1 = pd.read_csv(RAW_PATH / "1- one_clean.csv", encoding='utf-8')
    df2 = pd.read_csv(RAW_PATH / "2- two_clean.csv", encoding='utf-8')
    df = pd.concat([df1, df2], ignore_index=True)
    
    # Nettoyage
    df['ID'] = df['ID'].astype(str)
    df = df[~df['ID'].isin(['Unknown', 'unknown', 'nan', 'None', ''])].copy()
    df = df[~df['Major'].astype(str).str.lower().str.contains('unknown', na=False)].copy()
    df = df[~df['Subject'].astype(str).str.lower().str.contains('unknown', na=False)].copy()
    
    df = df.rename(columns={'Major': 'Filiere', 'Subject': 'Module'})
    df['Practical'] = pd.to_numeric(df['Practical'], errors='coerce').fillna(0)
    df['Theoretical'] = pd.to_numeric(df['Theoretical'], errors='coerce').fillna(0)
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(df['Practical'] + df['Theoretical'])
    df['Note_sur_20'] = df['Total'] / 5
    df['Needs_Support'] = ((df['Status'] == 'Fail') | 
                           (df['Total'] < 50) | 
                           (df['Status'].isin(['Absent', 'Debarred', 'Withdrawal']))).astype(int)
    
    print(f"\n📊 Données chargées: {len(df):,} enregistrements")
    
    # Générer les alertes
    student_alerts = generate_student_alerts(df, preview_only=True)
    module_alerts = generate_module_alerts(df, preview_only=True)
    admin_report = generate_admin_report(df, preview_only=True)
    
    # Résumé
    print("\n" + "=" * 60)
    print("✅ ALERTES GÉNÉRÉES (Mode Aperçu)")
    print("=" * 60)
    print(f"   📧 Alertes étudiants: {len(student_alerts)}")
    print(f"   📧 Alertes modules: {len(module_alerts)}")
    print(f"   📧 Rapport admin: 1")
    print(f"\n📁 Aperçus sauvegardés dans: {ALERTS_PATH}")
    print("\n💡 Pour activer l'envoi réel:")
    print("   1. Configurez EMAIL_CONFIG avec vos identifiants SMTP")
    print("   2. Changez preview_only=False dans les fonctions")


if __name__ == "__main__":
    generate_all_alerts()
