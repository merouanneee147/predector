# -*- coding: utf-8 -*-
"""
🗄️ Module Base de Données SQLite
==================================
Gestion de la persistance des données
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib
import json
from contextlib import contextmanager

# Chemin de la base de données
DB_PATH = Path(__file__).parent.parent / "output_projet4" / "soutien_pedagogique.db"

def get_db_path():
    """Retourne le chemin de la base de données"""
    DB_PATH.parent.mkdir(exist_ok=True)
    return str(DB_PATH)

@contextmanager
def get_db_connection():
    """Context manager pour les connexions à la base de données"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# =============================================================================
# CLASSE DATABASE - INTERFACE PRINCIPALE
# =============================================================================

class Database:
    """Classe principale pour l'accès à la base de données"""
    
    def __init__(self):
        """Initialise la base de données"""
        self._init_database()
    
    def _init_database(self):
        """Crée les tables si elles n'existent pas"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Table des utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'tuteur',
                    nom TEXT,
                    prenom TEXT,
                    email TEXT,
                    active INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            ''')
            
            # Table des sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    is_valid INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Table des interventions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interventions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    etudiant_id TEXT NOT NULL,
                    etudiant_nom TEXT,
                    type TEXT NOT NULL,
                    titre TEXT NOT NULL,
                    description TEXT,
                    statut TEXT DEFAULT 'planifié',
                    priorite TEXT DEFAULT 'normale',
                    date DATE DEFAULT CURRENT_DATE,
                    heure TIME DEFAULT CURRENT_TIME,
                    created_by TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT,
                    resultat TEXT,
                    notes TEXT DEFAULT '[]'
                )
            ''')
            
            # Table des emails envoyés
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emails_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    to_email TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    mode TEXT,
                    message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table audit log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    # =========================================================================
    # MÉTHODES UTILISATEURS
    # =========================================================================
    
    def hash_password(self, password: str) -> str:
        """Hash un mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, email: str, role: str, nom: str, prenom: str) -> int:
        """Crée un nouvel utilisateur et retourne son ID"""
        password_hash = self.hash_password(password)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, role, nom, prenom)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, password_hash, email, role, nom, prenom))
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None
    
    def get_user_by_username(self, username: str) -> dict:
        """Récupère un utilisateur par son nom d'utilisateur"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND active = 1', (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Récupère un utilisateur par son ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ? AND active = 1', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_users(self) -> list:
        """Récupère tous les utilisateurs actifs"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE active = 1 ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """Authentifie un utilisateur et retourne ses infos"""
        password_hash = self.hash_password(password)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM users 
                WHERE username = ? AND password_hash = ? AND active = 1
            ''', (username, password_hash))
            row = cursor.fetchone()
            
            if row:
                # Mettre à jour la date de dernière connexion
                cursor.execute(
                    'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                    (row['id'],)
                )
                return dict(row)
            return None
    
    # =========================================================================
    # MÉTHODES SESSIONS
    # =========================================================================
    
    def create_session(self, user_id: int, token: str, expires_at: str) -> int:
        """Crée une nouvelle session"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, token, expires_at))
            return cursor.lastrowid
    
    def validate_session(self, token: str) -> dict:
        """Valide une session et retourne ses infos"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM sessions 
                WHERE token = ? AND is_valid = 1 AND expires_at > datetime('now')
            ''', (token,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def invalidate_session(self, token: str) -> bool:
        """Invalide une session"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET is_valid = 0 WHERE token = ?', (token,))
            return cursor.rowcount > 0
    
    # =========================================================================
    # MÉTHODES INTERVENTIONS
    # =========================================================================
    
    def create_intervention(self, etudiant_id: str, etudiant_nom: str, type_intervention: str,
                           titre: str, description: str, statut: str, priorite: str,
                           created_by: str, resultat: str = '') -> int:
        """Crée une nouvelle intervention"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interventions 
                (etudiant_id, etudiant_nom, type, titre, description, statut, priorite, created_by, resultat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (etudiant_id, etudiant_nom, type_intervention, titre, description, 
                  statut, priorite, created_by, resultat))
            return cursor.lastrowid
    
    def get_intervention_by_id(self, intervention_id: int) -> dict:
        """Récupère une intervention par son ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM interventions WHERE id = ?', (intervention_id,))
            row = cursor.fetchone()
            if row:
                interv = dict(row)
                try:
                    interv['notes'] = json.loads(interv.get('notes', '[]'))
                except:
                    interv['notes'] = []
                return interv
            return None
    
    def get_interventions(self, filters: dict = None) -> list:
        """Récupère les interventions avec filtres"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM interventions WHERE 1=1'
            params = []
            
            if filters:
                if filters.get('etudiant_id'):
                    query += ' AND etudiant_id = ?'
                    params.append(filters['etudiant_id'])
                if filters.get('type'):
                    query += ' AND type = ?'
                    params.append(filters['type'])
                if filters.get('statut'):
                    query += ' AND statut = ?'
                    params.append(filters['statut'])
                if filters.get('date_debut'):
                    query += ' AND date >= ?'
                    params.append(filters['date_debut'])
                if filters.get('date_fin'):
                    query += ' AND date <= ?'
                    params.append(filters['date_fin'])
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            interventions = []
            for row in cursor.fetchall():
                interv = dict(row)
                try:
                    interv['notes'] = json.loads(interv.get('notes', '[]'))
                except:
                    interv['notes'] = []
                interventions.append(interv)
            return interventions
    
    def get_interventions_by_student(self, etudiant_id: str) -> list:
        """Récupère les interventions pour un étudiant"""
        return self.get_interventions({'etudiant_id': etudiant_id})
    
    def update_intervention(self, intervention_id: int, updated_by: str, **kwargs) -> bool:
        """Met à jour une intervention"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            updates = ['updated_at = CURRENT_TIMESTAMP', 'updated_by = ?']
            params = [updated_by]
            
            for field in ['type', 'titre', 'description', 'statut', 'priorite', 'resultat']:
                if field in kwargs:
                    updates.append(f'{field} = ?')
                    params.append(kwargs[field])
            
            params.append(intervention_id)
            query = f'UPDATE interventions SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_intervention(self, intervention_id: int) -> bool:
        """Supprime une intervention"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM interventions WHERE id = ?', (intervention_id,))
            return cursor.rowcount > 0
    
    def get_intervention_stats(self) -> dict:
        """Statistiques des interventions"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total
            cursor.execute('SELECT COUNT(*) FROM interventions')
            total = cursor.fetchone()[0]
            
            # Par statut
            cursor.execute('SELECT statut, COUNT(*) FROM interventions GROUP BY statut')
            par_statut = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Par type
            cursor.execute('SELECT type, COUNT(*) FROM interventions GROUP BY type')
            par_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Par priorité
            cursor.execute('SELECT priorite, COUNT(*) FROM interventions GROUP BY priorite')
            par_priorite = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Récentes (7 jours)
            cursor.execute('''
                SELECT COUNT(*) FROM interventions 
                WHERE date >= date('now', '-7 days')
            ''')
            recentes = cursor.fetchone()[0]
            
            # Étudiants suivis
            cursor.execute('SELECT COUNT(DISTINCT etudiant_id) FROM interventions')
            etudiants_suivis = cursor.fetchone()[0]
            
            return {
                'total': total,
                'par_statut': par_statut,
                'par_type': par_type,
                'par_priorite': par_priorite,
                'recentes_7j': recentes,
                'etudiants_suivis': etudiants_suivis
            }
    
    # =========================================================================
    # MÉTHODES AUDIT LOG
    # =========================================================================
    
    def add_audit_log(self, user_id: int, action: str, details: str = None) -> int:
        """Ajoute une entrée dans le journal d'audit"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))
            return cursor.lastrowid
    
    def get_audit_log(self, limit: int = 100) -> list:
        """Récupère le journal d'audit"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, u.username, u.nom as user_nom
                FROM audit_log a
                LEFT JOIN users u ON a.user_id = u.id
                ORDER BY a.created_at DESC LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # MÉTHODES EMAILS LOG
    # =========================================================================
    
    def log_email(self, to_email: str, subject: str, status: str, mode: str, message: str = None) -> int:
        """Enregistre un email envoyé"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO emails_log (to_email, subject, status, mode, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (to_email, subject, status, mode, message))
            return cursor.lastrowid
    
    def get_emails_log(self, limit: int = 50) -> list:
        """Récupère l'historique des emails"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM emails_log ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]


# Instance globale pour compatibilité avec l'ancienne API
_db_instance = None

def get_database() -> Database:
    """Retourne l'instance de la base de données"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


# Initialiser la base de données au chargement du module
if __name__ == '__main__':
    Database()
    print(f"📁 Base de données: {get_db_path()}")
