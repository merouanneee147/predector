# -*- coding: utf-8 -*-
"""
🔮 Script de Prédiction pour Données Externes
==============================================
Ce script permet de faire des prédictions sur de nouveaux étudiants
qui ne sont pas dans la base de données d'entraînement.

Usage:
    1. Préparez vos données dans un fichier CSV avec les colonnes requises
    2. Exécutez ce script
    3. Obtenez les prédictions et recommandations
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys
import io

# Fixer l'encodage pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

OUTPUT_PATH = Path("output_projet4")

print("=" * 70)
print("🔮 SYSTÈME DE PRÉDICTION - SOUTIEN PÉDAGOGIQUE")
print("=" * 70)

# =============================================================================
# 1. CHARGER LE MODÈLE ENTRAÎNÉ
# =============================================================================
print("\n📂 Chargement du modèle entraîné...")

model_path = OUTPUT_PATH / 'model_soutien_pedagogique.joblib'

if not model_path.exists():
    print("❌ ERREUR: Le modèle n'existe pas!")
    print("   Veuillez d'abord exécuter: python projet4_support_recommendation.py")
    print("   pour entraîner et sauvegarder le modèle.")
    sys.exit(1)

# Charger le modèle et ses composants
model_data = joblib.load(model_path)

calibrated_model = model_data['model']
xgb_model = model_data['xgb_model']
scaler = model_data['scaler']
feature_columns = model_data['feature_columns']
le_filiere = model_data['le_filiere']
le_pole = model_data['le_pole']
kmeans = model_data['kmeans']
profil_mapping = model_data['profil_mapping']
SEUIL_VALIDATION = model_data['seuil_validation']

print(f"✅ Modèle chargé avec succès!")
print(f"   • Features attendues: {len(feature_columns)}")
print(f"   • Seuil de validation: {SEUIL_VALIDATION}/20")

# =============================================================================
# 2. FONCTION DE PRÉDICTION
# =============================================================================

def predire_besoin_soutien(donnees_etudiant):
    """
    Prédit le besoin de soutien pour un nouvel étudiant.
    
    Paramètres:
    -----------
    donnees_etudiant : dict
        Dictionnaire avec les informations de l'étudiant:
        - 'Practical': Note pratique (0-100)
        - 'Theoretical': Note théorique (0-100)
        - 'Total': Note totale (0-100, optionnel)
        - 'Filiere': Code de la filière (EEC, EEA, etc.)
        - 'Annee': Année d'études (1, 2, 3, etc.)
        - 'Semester': Semestre (1 ou 2)
        
    Retourne:
    ---------
    dict avec:
        - 'besoin_soutien': 0 ou 1
        - 'probabilite_risque': float entre 0 et 1
        - 'categorie_risque': CRITIQUE, ÉLEVÉ, MODÉRÉ, FAIBLE, MINIMAL
        - 'profil': Excellence, Régulier, En_Progression, En_Difficulté, À_Risque
        - 'recommandation': Action recommandée
    """
    
    # Calculer Total si non fourni
    if 'Total' not in donnees_etudiant or pd.isna(donnees_etudiant.get('Total')):
        donnees_etudiant['Total'] = donnees_etudiant.get('Practical', 0) + donnees_etudiant.get('Theoretical', 0)
    
    # S'assurer que Total ne dépasse pas 100
    total = min(donnees_etudiant['Total'], 100)
    
    # Convertir en note sur 20
    note_sur_20 = total / 5
    
    # Créer le vecteur de features
    features = {}
    
    # Features de base
    features['Practical'] = min(donnees_etudiant.get('Practical', 0), 50)
    features['Theoretical'] = min(donnees_etudiant.get('Theoretical', 0), 50)
    features['Total'] = total
    features['Note_sur_20'] = note_sur_20
    features['Semester'] = donnees_etudiant.get('Semester', 1)
    features['Annee'] = donnees_etudiant.get('Annee', 1)
    
    # Features dérivées (valeurs moyennes par défaut)
    features['peer_group_avg_total'] = 50  # Moyenne typique
    features['peer_group_avg_note20'] = 10
    features['peer_group_avg_practical'] = 25
    features['peer_group_support_rate'] = 0.5
    features['deviation_from_peer'] = donnees_etudiant['Total'] - 50
    features['deviation_note20'] = note_sur_20 - 10
    
    # Profil étudiant (valeurs par défaut pour nouvel étudiant)
    features['student_avg_total'] = donnees_etudiant['Total']
    features['student_std_total'] = 0
    features['student_min_total'] = donnees_etudiant['Total']
    features['student_max_total'] = donnees_etudiant['Total']
    features['student_module_count'] = 1
    features['student_avg_note20'] = note_sur_20
    features['student_min_note20'] = note_sur_20
    features['student_avg_practical'] = donnees_etudiant.get('Practical', 0)
    features['student_avg_theoretical'] = donnees_etudiant.get('Theoretical', 0)
    features['student_support_rate'] = 0.5 if note_sur_20 < 10 else 0
    
    # Module stats (valeurs moyennes)
    features['module_avg_total'] = 50
    features['module_avg_note20'] = 10
    features['module_taux_echec'] = 0.5
    features['module_effectif'] = 100
    
    # Combo filière-module
    features['combo_taux_echec'] = 0.5
    features['combo_haut_risque'] = 1 if note_sur_20 < 10 else 0
    
    # Autres features
    features['charge_semestre'] = 6
    features['taux_absenteisme'] = 0
    features['ratio_pratique'] = donnees_etudiant.get('Practical', 0) / (donnees_etudiant['Total'] + 1)
    features['ecart_theorie_pratique'] = donnees_etudiant.get('Theoretical', 0) - donnees_etudiant.get('Practical', 0)
    features['modules_rattrapage'] = 1 if note_sur_20 < 10 else 0
    features['distance_seuil'] = note_sur_20 - SEUIL_VALIDATION
    
    # Features de force par pôle (valeurs par défaut)
    for col in feature_columns:
        if col.startswith('force_') and col not in features:
            features[col] = note_sur_20
    
    # Encoder la filière
    filiere = donnees_etudiant.get('Filiere', 'EEA')
    try:
        features['Filiere_encoded'] = le_filiere.transform([filiere])[0]
    except:
        features['Filiere_encoded'] = 0  # Filière inconnue
    
    # Encoder le pôle de compétences
    features['pole_encoded'] = 0  # Par défaut
    
    # Créer le DataFrame
    X_new = pd.DataFrame([features])
    
    # S'assurer que toutes les colonnes sont présentes
    for col in feature_columns:
        if col not in X_new.columns:
            X_new[col] = 0
    
    # Réordonner les colonnes
    X_new = X_new[feature_columns]
    
    # Normaliser
    X_new_scaled = scaler.transform(X_new)
    
    # Prédiction
    prediction = calibrated_model.predict(X_new_scaled)[0]
    probabilite = calibrated_model.predict_proba(X_new_scaled)[0, 1]
    
    # Clustering pour le profil
    cluster = kmeans.predict(X_new_scaled)[0]
    profil = profil_mapping.get(cluster, 'Inconnu')
    
    # Catégorie de risque
    if probabilite >= 0.8:
        categorie = 'CRITIQUE'
        recommandation = "🔴 Tutorat individuel URGENT + Convocation conseiller pédagogique"
    elif probabilite >= 0.6:
        categorie = 'ÉLEVÉ'
        recommandation = "🟠 Inscription obligatoire TD de soutien + Suivi bi-hebdomadaire"
    elif probabilite >= 0.4:
        categorie = 'MODÉRÉ'
        recommandation = "🟡 Groupes d'entraide + Ressources en ligne"
    elif probabilite >= 0.2:
        categorie = 'FAIBLE'
        recommandation = "🟢 Auto-évaluation + Permanences optionnelles"
    else:
        categorie = 'MINIMAL'
        recommandation = "⚪ Encouragement + Ressources avancées"
    
    return {
        'besoin_soutien': int(prediction),
        'probabilite_risque': float(probabilite),
        'categorie_risque': categorie,
        'profil': profil,
        'note_sur_20': note_sur_20,
        'recommandation': recommandation
    }


def predire_depuis_csv(fichier_csv):
    """
    Fait des prédictions pour tous les étudiants dans un fichier CSV.
    
    Le CSV doit contenir les colonnes:
    - ID, Practical, Theoretical, Total (optionnel), Filiere, Annee, Semester
    """
    print(f"\n📂 Lecture du fichier: {fichier_csv}")
    
    df = pd.read_csv(fichier_csv, encoding='utf-8')
    print(f"   • {len(df)} enregistrements trouvés")
    
    resultats = []
    
    for idx, row in df.iterrows():
        donnees = {
            'Practical': row.get('Practical', 0),
            'Theoretical': row.get('Theoretical', 0),
            'Total': row.get('Total', None),
            'Filiere': row.get('Filiere', row.get('Major', 'EEA')),
            'Annee': row.get('Annee', row.get('MajorYear', 1)),
            'Semester': row.get('Semester', 1)
        }
        
        prediction = predire_besoin_soutien(donnees)
        prediction['ID'] = row.get('ID', idx)
        prediction['Module'] = row.get('Module', row.get('Subject', 'Inconnu'))
        resultats.append(prediction)
    
    df_resultats = pd.DataFrame(resultats)
    
    # Réordonner les colonnes
    cols = ['ID', 'Module', 'note_sur_20', 'besoin_soutien', 'probabilite_risque', 
            'categorie_risque', 'profil', 'recommandation']
    df_resultats = df_resultats[[c for c in cols if c in df_resultats.columns]]
    
    return df_resultats


# =============================================================================
# 3. INTERFACE INTERACTIVE
# =============================================================================

def saisir_donnees_etudiant():
    """Interface pour saisir les données d'un nouvel étudiant"""
    print("\n" + "=" * 70)
    print("📝 SAISIE DES DONNÉES D'UN NOUVEL ÉTUDIANT")
    print("=" * 70)
    print("\n⚠️  NOTE: Les notes sont sur 100 au total")
    print("   • Practical (TP/Travaux Pratiques): 0-50")
    print("   • Theoretical (Cours/Examen): 0-50")
    print("   • OU entrez directement la note totale sur 100")
    
    try:
        # Option 1: Note totale directe
        total_input = input("\n   Note Totale sur 100 (ou appuyez Entrée pour saisir TP+Cours): ").strip()
        
        if total_input:
            total = float(total_input)
            practical = total / 2  # Estimation
            theoretical = total / 2
        else:
            # Option 2: Saisie séparée
            practical = float(input("   Note Pratique/TP (0-50): ") or 0)
            theoretical = float(input("   Note Théorique/Cours (0-50): ") or 0)
            total = practical + theoretical
        
        # Validation
        if total > 100:
            print(f"⚠️  Note {total} > 100, limitée à 100")
            total = 100
        
        filiere = input("   Filière (EEA, EEC, EED, EEE, EEM, EEP, EET): ").upper() or "EEA"
        annee = int(input("   Année d'études (1-5): ") or 1)
        semester = int(input("   Semestre (1-2): ") or 1)
        
        donnees = {
            'Practical': min(practical, 50),
            'Theoretical': min(theoretical, 50),
            'Total': total,
            'Filiere': filiere,
            'Annee': annee,
            'Semester': semester
        }
        
        return donnees
    except ValueError as e:
        print(f"❌ Erreur de saisie: {e}")
        return None


def afficher_prediction(resultat):
    """Affiche le résultat de la prédiction de manière formatée"""
    print("\n" + "=" * 70)
    print("🔮 RÉSULTAT DE LA PRÉDICTION")
    print("=" * 70)
    
    print(f"\n📊 NOTE: {resultat['note_sur_20']:.1f}/20")
    
    if resultat['besoin_soutien'] == 1:
        print(f"\n⚠️  BESOIN DE SOUTIEN: OUI")
    else:
        print(f"\n✅ BESOIN DE SOUTIEN: NON")
    
    print(f"\n📈 ANALYSE:")
    print(f"   • Probabilité de risque: {resultat['probabilite_risque']*100:.1f}%")
    print(f"   • Catégorie de risque: {resultat['categorie_risque']}")
    print(f"   • Profil d'apprenant: {resultat['profil']}")
    
    print(f"\n💡 RECOMMANDATION:")
    print(f"   {resultat['recommandation']}")


def menu_prediction():
    """Menu principal pour les prédictions"""
    while True:
        print("\n" + "=" * 70)
        print("🔮 MENU DE PRÉDICTION")
        print("=" * 70)
        print("1. Prédire pour un nouvel étudiant (saisie manuelle)")
        print("2. Prédire depuis un fichier CSV")
        print("3. Exemples de prédictions")
        print("4. Quitter")
        print("-" * 70)
        
        choix = input("Votre choix (1-4): ").strip()
        
        if choix == "1":
            donnees = saisir_donnees_etudiant()
            if donnees:
                resultat = predire_besoin_soutien(donnees)
                afficher_prediction(resultat)
        
        elif choix == "2":
            fichier = input("Chemin du fichier CSV: ").strip()
            if fichier:
                try:
                    resultats = predire_depuis_csv(fichier)
                    print(f"\n✅ Prédictions terminées pour {len(resultats)} enregistrements")
                    
                    # Sauvegarder les résultats
                    output_file = OUTPUT_PATH / 'predictions_externes.csv'
                    resultats.to_csv(output_file, index=False, encoding='utf-8-sig')
                    print(f"   💾 Résultats sauvegardés: {output_file}")
                    
                    # Afficher un résumé
                    print(f"\n📊 RÉSUMÉ:")
                    print(f"   • Étudiants nécessitant un soutien: {resultats['besoin_soutien'].sum()}")
                    print(f"   • Risque CRITIQUE: {(resultats['categorie_risque'] == 'CRITIQUE').sum()}")
                    print(f"   • Risque ÉLEVÉ: {(resultats['categorie_risque'] == 'ÉLEVÉ').sum()}")
                except Exception as e:
                    print(f"❌ Erreur: {e}")
        
        elif choix == "3":
            print("\n📋 EXEMPLES DE PRÉDICTIONS:")
            
            # Exemple 1: Étudiant en difficulté
            exemple1 = predire_besoin_soutien({
                'Practical': 15,
                'Theoretical': 20,
                'Filiere': 'EEC',
                'Annee': 1,
                'Semester': 1
            })
            print(f"\n   🔴 Étudiant faible (35/100 = 7/20):")
            print(f"      Risque: {exemple1['probabilite_risque']*100:.0f}% | {exemple1['categorie_risque']}")
            print(f"      → {exemple1['recommandation']}")
            
            # Exemple 2: Étudiant moyen
            exemple2 = predire_besoin_soutien({
                'Practical': 25,
                'Theoretical': 30,
                'Filiere': 'EEA',
                'Annee': 2,
                'Semester': 2
            })
            print(f"\n   🟡 Étudiant moyen (55/100 = 11/20):")
            print(f"      Risque: {exemple2['probabilite_risque']*100:.0f}% | {exemple2['categorie_risque']}")
            print(f"      → {exemple2['recommandation']}")
            
            # Exemple 3: Bon étudiant
            exemple3 = predire_besoin_soutien({
                'Practical': 40,
                'Theoretical': 42,
                'Filiere': 'EET',
                'Annee': 3,
                'Semester': 1
            })
            print(f"\n   🟢 Bon étudiant (82/100 = 16.4/20):")
            print(f"      Risque: {exemple3['probabilite_risque']*100:.0f}% | {exemple3['categorie_risque']}")
            print(f"      → {exemple3['recommandation']}")
        
        elif choix == "4":
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide, réessayez.")


# =============================================================================
# EXÉCUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎯 SYSTÈME PRÊT POUR LES PRÉDICTIONS EXTERNES")
    print("=" * 70)
    
    # Lancer le menu
    menu_prediction()
