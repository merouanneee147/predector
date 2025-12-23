# -*- coding: utf-8 -*-
"""
🧪 Script de Test du Modèle de Recommandation de Soutien Pédagogique
=====================================================================
Ce script permet de tester le modèle avec de nouveaux étudiants
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import sys
import io

# Fixer l'encodage pour les caractères arabes sur Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Charger les données et recréer le modèle (version simplifiée pour test)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb

RAW_PATH = Path("raw")
OUTPUT_PATH = Path("output_projet4")

print("=" * 70)
print("🧪 TEST DU MODÈLE DE SOUTIEN PÉDAGOGIQUE")
print("=" * 70)

# =============================================================================
# 1. CHARGER ET PRÉPARER LES DONNÉES (comme dans le modèle principal)
# =============================================================================
print("\n📊 Chargement des données...")

df1 = pd.read_csv(RAW_PATH / "1- one_clean.csv", encoding='utf-8')
df2 = pd.read_csv(RAW_PATH / "2- two_clean.csv", encoding='utf-8')
df = pd.concat([df1, df2], ignore_index=True)

# Nettoyage complet des données
taille_avant = len(df)

# Supprimer les lignes avec ID null ou Unknown
df['ID'] = df['ID'].astype(str)
df = df[~df['ID'].isin(['Unknown', 'unknown', 'nan', 'None', ''])].copy()
df = df[df['ID'].notna()].copy()

# Supprimer les lignes avec Major Unknown
df = df[~df['Major'].astype(str).str.lower().str.contains('unknown', na=False)].copy()

# Supprimer les lignes avec Subject Unknown  
df = df[~df['Subject'].astype(str).str.lower().str.contains('unknown', na=False)].copy()

print(f"   • Enregistrements nettoyés (Unknown supprimés): {taille_avant - len(df):,}")

df = df.rename(columns={'Major': 'Filiere', 'Subject': 'Module', 'MajorYear': 'Annee', 'OfficalYear': 'AnneUniversitaire'})

df['Practical'] = pd.to_numeric(df['Practical'], errors='coerce').fillna(0)
df['Theoretical'] = pd.to_numeric(df['Theoretical'], errors='coerce').fillna(0)
df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(df['Practical'] + df['Theoretical'])
df['Note_sur_20'] = df['Total'] / 5 if df['Total'].max() > 20 else df['Total']
df['Annee'] = pd.to_numeric(df['Annee'], errors='coerce').fillna(1).astype(int)
df['Semester'] = pd.to_numeric(df['Semester'], errors='coerce').fillna(1).astype(int)

# Variable cible
SEUIL_VALIDATION = 10
df['Needs_Support'] = ((df['Status'] == 'Fail') | 
                        (df['Total'] < 50) | 
                        (df['Status'].isin(['Absent', 'Debarred', 'Withdrawal']))).astype(int)

# Dictionnaire de traduction Arabe -> Français pour les modules principaux
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
    'تحكم حديث 1': 'Controle Moderne 1',
    'التحليل الرياضي': 'Analyse Mathematique',
    'التحليل العددي': 'Analyse Numerique',
    'نظرية الدارات الكهربائية': 'Theorie des Circuits Electriques',
    'نظرية الدارات الكهربائية 1': 'Theorie des Circuits Electriques 1',
    'نظرية الدارات الكهربائية 2': 'Theorie des Circuits Electriques 2',
    'الخوارزميات وبنى المعطيات': 'Algorithmes et Structures de Donnees',
    'اللغة الانكليزية 3': 'Anglais 3',
    'اللغة الانكليزية 4': 'Anglais 4',
    'النظم المنطقية والدارات الرقمية': 'Systemes Logiques et Circuits Numeriques',
    'بحوث العمليات 1': 'Recherche Operationnelle 1',
    'هندسة الكترونية': 'Genie Electronique',
    'هندسة الكترونية 1': 'Genie Electronique 1',
    'هندسة الكترونية 2': 'Genie Electronique 2',
    'الجبر الخطي': 'Algebre Lineaire',
    'الجبر المنطقي': 'Algebre de Boole',
    'برمجة منطقية': 'Programmation Logique',
    'برمجة': 'Programmation',
    'برمجة وتطبيقاتها': 'Programmation et Applications',
    'مبادئ الهندسة الكهربائية': 'Principes Genie Electrique',
    'ميكانيك هندسي': 'Mecanique Generale',
    'هندسة ميكانيكية': 'Genie Mecanique',
    'هندسة ميكانيكية 1': 'Genie Mecanique 1',
    'هندسة ميكانيكية 2': 'Genie Mecanique 2',
    'الآلات الكهربائية': 'Machines Electriques',
    'الآلات الكهربائية 1': 'Machines Electriques 1',
    'الآلات الكهربائية 2': 'Machines Electriques 2',
    'الدارات الالكترونية': 'Circuits Electroniques',
    'دارات الكترونية': 'Circuits Electroniques',
    'دارات الإلكترونية': 'Circuits Electroniques',
    'الهندسة الإلكترونية 2': 'Genie Electronique 2',
    'الهندسة الالكترونية 1': 'Genie Electronique 1',
    'الرسم الهندسي': 'Dessin Technique',
    'الثقافة القومية الاشتراكية': 'Culture Nationale',
    'القياسات الكهربائية وأجهزة القياس': 'Mesures Electriques',
    'القياسات الالكترونية': 'Mesures Electroniques',
    'القياسات الإلكترونية': 'Mesures Electroniques',
    'مقاومة المواد وخواصها': 'Resistance des Materiaux',
    'تكنولوجيا المواد الكهربائية': 'Technologie Materiaux Electriques',
    'الحقول الكهرومغناطيسية': 'Champs Electromagnetiques',
    'حقول الكهرومغناطيسية': 'Champs Electromagnetiques',
    'نظرية الحقول الكهرطيسية': 'Theorie Champs Electromagnetiques',
    'الحقول المغناطيسية في الآلات الكهربائية': 'Champs Magnetiques Machines',
    'إشارات ونظم': 'Signaux et Systemes',
    'لغات برمجة': 'Langages de Programmation',
    'برمجيات متقدمة في نظم التحكم 1': 'Logiciels Avances Controle 1',
    'برمجيات متقدمة في نظم التحكم 2': 'Logiciels Avances Controle 2',
    'مبادئ الاتصالات': 'Principes Telecommunications',
    'الآلات والقيادة الكهربائية': 'Machines et Commande Electrique',
    'الأمن الصناعي والاقتصاد الهندسي': 'Securite Industrielle et Economie',
    'أسس الهندسة الكهربائية 1': 'Bases Genie Electrique 1',
    'أسس الهندسة الكهربائية 2': 'Bases Genie Electrique 2',
    'الأدوات نصف الناقلة': 'Composants Semi-conducteurs',
    'الأدوات الالكترونية': 'Composants Electroniques',
    'جبر المنطق': 'Algebre de Boole',
    'هندسة كهربائية': 'Genie Electrique',
    'الهندسة الكهربائية': 'Genie Electrique',
    'الهندسة الميكانيكية': 'Genie Mecanique',
    'نظم القدرة الكهربائية': 'Systemes de Puissance Electrique',
    'اللغة الفرنسية 3': 'Francais 3',
    'Unknown': 'Inconnu'
}

def traduire_module(nom_arabe):
    """Traduit le nom du module de l'arabe vers le français"""
    return TRADUCTION_MODULES.get(nom_arabe, nom_arabe)

print(f"✅ Données chargées: {len(df):,} enregistrements")

# =============================================================================
# 2. FONCTION DE TEST POUR UN ÉTUDIANT
# =============================================================================

def tester_etudiant(student_id):
    """
    Teste le modèle pour un étudiant spécifique
    """
    print(f"\n{'='*70}")
    print(f"🎓 ANALYSE DE L'ÉTUDIANT: {student_id}")
    print(f"{'='*70}")
    
    # Récupérer les données de l'étudiant
    etudiant_data = df[df['ID'] == str(student_id)]
    
    if len(etudiant_data) == 0:
        print(f"❌ Étudiant {student_id} non trouvé dans la base de données")
        return None
    
    # Informations générales
    filiere = etudiant_data['Filiere'].iloc[0]
    nb_modules = len(etudiant_data)
    moyenne_generale = etudiant_data['Note_sur_20'].mean()
    modules_echec = etudiant_data[etudiant_data['Needs_Support'] == 1]
    
    print(f"\n📋 INFORMATIONS GÉNÉRALES:")
    print(f"   • Filière: {filiere}")
    print(f"   • Nombre de modules: {nb_modules}")
    print(f"   • Moyenne générale: {moyenne_generale:.2f}/20")
    print(f"   • Modules en difficulté: {len(modules_echec)}")
    
    # Détail par module
    print(f"\n📚 DÉTAIL PAR MODULE:")
    print("-" * 70)
    
    for _, row in etudiant_data.iterrows():
        status_emoji = "✅" if row['Needs_Support'] == 0 else "❌"
        note = row['Note_sur_20']
        module_ar = row['Module']
        module = traduire_module(module_ar)
        if len(str(module)) > 40:
            module = module[:40] + "..."
        status = row['Status']
        
        print(f"   {status_emoji} {module}")
        print(f"      Note: {note:.1f}/20 | Statut: {status}")
    
    # Diagnostic
    print(f"\n🔍 DIAGNOSTIC:")
    if moyenne_generale >= 14:
        profil = "Excellence"
        emoji = "⭐"
        recommandation = "Encourager vers les programmes d'excellence"
    elif moyenne_generale >= 12:
        profil = "Régulier"
        emoji = "🟢"
        recommandation = "Consolidation des acquis"
    elif moyenne_generale >= 10:
        profil = "En Progression"
        emoji = "🟡"
        recommandation = "Sessions de révision recommandées"
    elif moyenne_generale >= 7:
        profil = "En Difficulté"
        emoji = "🟠"
        recommandation = "Inscription aux TD de soutien obligatoire"
    else:
        profil = "À Risque"
        emoji = "🔴"
        recommandation = "Intervention urgente - Tutorat individuel"
    
    taux_echec = len(modules_echec) / nb_modules * 100
    
    print(f"   {emoji} Profil: {profil}")
    print(f"   • Taux d'échec: {taux_echec:.1f}%")
    print(f"   • Score de risque estimé: {min(0.99, taux_echec/100 + (10-moyenne_generale)/20):.2f}")
    
    print(f"\n💡 RECOMMANDATION:")
    print(f"   {recommandation}")
    
    if len(modules_echec) > 0:
        print(f"\n📌 MODULES PRIORITAIRES POUR LE SOUTIEN:")
        for _, row in modules_echec.head(5).iterrows():
            module = traduire_module(row['Module'])
            if len(str(module)) > 45:
                module = module[:45] + "..."
            print(f"   • {module} (Note: {row['Note_sur_20']:.1f}/20)")
    
    return {
        'id': student_id,
        'filiere': filiere,
        'moyenne': moyenne_generale,
        'profil': profil,
        'modules_echec': len(modules_echec),
        'recommandation': recommandation
    }

def tester_module(module_name):
    """
    Teste les statistiques d'un module spécifique
    """
    print(f"\n{'='*70}")
    print(f"📚 ANALYSE DU MODULE: {module_name}")
    print(f"{'='*70}")
    
    # Recherche partielle
    module_data = df[df['Module'].str.contains(module_name, case=False, na=False)]
    
    if len(module_data) == 0:
        print(f"❌ Module '{module_name}' non trouvé")
        return None
    
    module_exact = module_data['Module'].iloc[0]
    module_fr = traduire_module(module_exact)
    nb_etudiants = len(module_data)
    moyenne = module_data['Note_sur_20'].mean()
    taux_echec = module_data['Needs_Support'].mean() * 100
    
    print(f"\n📋 STATISTIQUES DU MODULE:")
    print(f"   • Nom complet: {module_fr}")
    print(f"   • Nombre d'étudiants: {nb_etudiants}")
    print(f"   • Moyenne du module: {moyenne:.2f}/20")
    print(f"   • Taux d'échec: {taux_echec:.1f}%")
    
    # Classification difficulté
    if taux_echec >= 50:
        difficulte = "🔴 Très Difficile"
    elif taux_echec >= 30:
        difficulte = "🟠 Difficile"
    elif taux_echec >= 15:
        difficulte = "🟡 Moyen"
    else:
        difficulte = "🟢 Accessible"
    
    print(f"   • Difficulté: {difficulte}")
    
    # Par filière
    print(f"\n📊 RÉPARTITION PAR FILIÈRE:")
    filiere_stats = module_data.groupby('Filiere').agg({
        'Note_sur_20': 'mean',
        'Needs_Support': 'mean',
        'ID': 'count'
    }).round(2)
    
    for filiere, row in filiere_stats.iterrows():
        print(f"   • {filiere}: {int(row['ID'])} étudiants, Moy: {row['Note_sur_20']:.1f}/20, Échec: {row['Needs_Support']*100:.0f}%")
    
    return {
        'module': module_exact,
        'nb_etudiants': nb_etudiants,
        'moyenne': moyenne,
        'taux_echec': taux_echec
    }

def liste_etudiants_disponibles():
    """Affiche quelques étudiants disponibles pour le test"""
    print("\n📋 EXEMPLES D'ÉTUDIANTS DISPONIBLES POUR LE TEST:")
    print("-" * 50)
    sample = df.groupby('ID').agg({
        'Filiere': 'first',
        'Note_sur_20': 'mean',
        'Module': 'count'
    }).reset_index().head(20)
    
    for _, row in sample.iterrows():
        print(f"   • ID: {row['ID']} | Filière: {row['Filiere']} | Moy: {row['Note_sur_20']:.1f}/20 | {int(row['Module'])} modules")

def liste_modules_disponibles():
    """Affiche les modules disponibles pour le test"""
    print("\n📚 MODULES DISPONIBLES POUR LE TEST:")
    print("-" * 50)
    modules = df['Module'].unique()[:20]
    for m in modules:
        m_fr = traduire_module(m)
        display = m_fr[:50] + "..." if len(str(m_fr)) > 50 else m_fr
        print(f"   • {display}")

# =============================================================================
# 3. MENU INTERACTIF
# =============================================================================

def menu_principal():
    """Menu interactif pour tester le modèle"""
    while True:
        print("\n" + "=" * 70)
        print("🧪 MENU DE TEST DU MODÈLE")
        print("=" * 70)
        print("1. Tester un étudiant par ID")
        print("2. Analyser un module")
        print("3. Voir la liste des étudiants disponibles")
        print("4. Voir la liste des modules disponibles")
        print("5. Tester plusieurs étudiants aléatoires")
        print("6. Quitter")
        print("-" * 70)
        
        choix = input("Votre choix (1-6): ").strip()
        
        if choix == "1":
            student_id = input("Entrez l'ID de l'étudiant: ").strip()
            tester_etudiant(student_id)
        
        elif choix == "2":
            module_name = input("Entrez le nom du module (ou partie): ").strip()
            tester_module(module_name)
        
        elif choix == "3":
            liste_etudiants_disponibles()
        
        elif choix == "4":
            liste_modules_disponibles()
        
        elif choix == "5":
            print("\n🎲 Test de 5 étudiants aléatoires...")
            random_ids = df['ID'].drop_duplicates().sample(5).tolist()
            for sid in random_ids:
                tester_etudiant(sid)
        
        elif choix == "6":
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide, réessayez.")

# =============================================================================
# EXÉCUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("📊 EXEMPLES DE TESTS RAPIDES")
    print("=" * 70)
    
    # Test automatique avec quelques étudiants
    sample_ids = df['ID'].drop_duplicates().head(3).tolist()
    
    print(f"\n🎯 Test automatique avec {len(sample_ids)} étudiants:")
    for sid in sample_ids:
        result = tester_etudiant(sid)
    
    # Test d'un module
    print("\n" + "=" * 70)
    tester_module("رياضيات")  # Test du module Mathématiques
    
    print("\n" + "=" * 70)
    print("💡 Lancement du mode interactif...")
    print("=" * 70)
    
    # Mode interactif activé:
    menu_principal()
