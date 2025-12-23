"""
🔵 Projet 4 : Système de Recommandation Intelligente de Soutien Pédagogique
==============================================================================
🇲🇦 Adapté pour les Établissements d'Enseignement Supérieur Marocains
   (Universités, ENSA, ENSAM, FST, Écoles d'Ingénieurs)

Objectif: Identifier automatiquement les combinaisons Étudiant-Module nécessitant 
une intervention pédagogique pour optimiser l'allocation des ressources de tutorat
et de soutien universitaire.

Contexte Marocain:
- Système LMD (Licence-Master-Doctorat)
- Validation par modules et semestres
- Note de passage: 10/20 (ou 12/20 selon les filières)
- Rattrapages et sessions de rattrapage

Variable Cible: Needs_Support = 1 si:
  - Statut = Non Validé / Ajourné / Rattrapage
  - Note < 10/20 (seuil de validation)
  - Patterns d'absentéisme

Algorithmes:
- Collaborative Filtering (similarité entre étudiants)
- XGBoost Classifier avec calibration de probabilités
- K-Means Clustering + Classification
- Scoring de risque pour priorisation
"""

import pandas as pd
import numpy as np
import warnings
from pathlib import Path

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (classification_report, confusion_matrix, 
                            roc_auc_score, precision_recall_curve, 
                            average_precision_score, f1_score)
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')

# Configuration
RAW_PATH = Path("raw")
OUTPUT_PATH = Path("output_projet4")
OUTPUT_PATH.mkdir(exist_ok=True)

print("=" * 80)
print("🔵 PROJET 4: SYSTÈME DE RECOMMANDATION INTELLIGENTE DE SOUTIEN PÉDAGOGIQUE")
print("🇲🇦 Adapté pour les Établissements d'Enseignement Supérieur Marocains")
print("=" * 80)

# =============================================================================
# 1. CHARGEMENT ET PRÉPARATION DES DONNÉES
# =============================================================================
print("\n" + "=" * 80)
print("📊 ÉTAPE 1: CHARGEMENT ET PRÉPARATION DES DONNÉES")
print("=" * 80)

# Charger les deux fichiers
df1 = pd.read_csv(RAW_PATH / "1- one_clean.csv")
df2 = pd.read_csv(RAW_PATH / "2- two_clean.csv")

# Combiner les datasets
df = pd.concat([df1, df2], ignore_index=True)

print(f"\n📁 Données chargées:")
print(f"   • Fichier 1: {len(df1):,} enregistrements")
print(f"   • Fichier 2: {len(df2):,} enregistrements")
print(f"   • Total combiné: {len(df):,} enregistrements")

# Nettoyer les données
print("\n🔧 Nettoyage des données...")

# Taille avant nettoyage
taille_avant = len(df)

# Supprimer les lignes avec ID null ou Unknown
df['ID'] = df['ID'].astype(str)
df = df[~df['ID'].isin(['Unknown', 'unknown', 'nan', 'None', ''])].copy()
df = df[df['ID'].notna()].copy()

# Supprimer les lignes avec Major/Filière Unknown
df = df[~df['Major'].astype(str).str.lower().str.contains('unknown', na=False)].copy()

# Supprimer les lignes avec Subject/Module Unknown
df = df[~df['Subject'].astype(str).str.lower().str.contains('unknown', na=False)].copy()

# Supprimer les lignes avec Total null (notes manquantes)
df = df[df['Total'].notna() | (df['Practical'].notna() & df['Theoretical'].notna())].copy()

print(f"   • Enregistrements supprimés (Unknown/null): {taille_avant - len(df):,}")

# Renommer les colonnes pour le contexte marocain
# Major -> Filière, Subject -> Module, MajorYear -> Année
df = df.rename(columns={
    'Major': 'Filiere',
    'Subject': 'Module', 
    'MajorYear': 'Annee',
    'OfficalYear': 'AnneUniversitaire'
})

# Convertir les colonnes numériques
df['Practical'] = pd.to_numeric(df['Practical'], errors='coerce').fillna(0)
df['Theoretical'] = pd.to_numeric(df['Theoretical'], errors='coerce').fillna(0)
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')

# Calculer Total si manquant
df['Total'] = df['Total'].fillna(df['Practical'] + df['Theoretical'])

# Convertir les notes sur 20 (système marocain) si nécessaire
# Si les notes sont sur 100, les convertir sur 20
if df['Total'].max() > 20:
    df['Note_sur_20'] = df['Total'] / 5  # Conversion 100 -> 20
else:
    df['Note_sur_20'] = df['Total']

# Nettoyer Année d'études
df['Annee'] = pd.to_numeric(df['Annee'], errors='coerce').fillna(1).astype(int)

# Nettoyer Semestre
df['Semester'] = pd.to_numeric(df['Semester'], errors='coerce').fillna(1).astype(int)

print(f"   • Après nettoyage: {len(df):,} enregistrements")
print(f"   • Étudiants uniques: {df['ID'].nunique():,}")
print(f"   • Modules uniques: {df['Module'].nunique()}")
print(f"   • Filières: {df['Filiere'].nunique()}")

# Mapper les statuts vers le système marocain
status_mapping = {
    'Pass': 'Validé',
    'Fail': 'Non_Validé',
    'Absent': 'Absent',
    'Debarred': 'Exclu',
    'Withdrawal': 'Abandon',
    'Withhold': 'En_Attente',
    'Exempt': 'Dispensé'
}
df['Statut_MA'] = df['Status'].map(status_mapping).fillna(df['Status'])

# Afficher la distribution des Statuts
print(f"\n📊 Distribution des Statuts (Système Marocain):")
status_counts = df['Statut_MA'].value_counts()
for status, count in status_counts.items():
    pct = count / len(df) * 100
    print(f"   • {status}: {count:,} ({pct:.1f}%)")

# =============================================================================
# 2. CRÉATION DE LA VARIABLE CIBLE (Needs_Support) - Contexte Marocain
# =============================================================================
print("\n" + "=" * 80)
print("🎯 ÉTAPE 2: CRÉATION DE LA VARIABLE CIBLE (Système Marocain)")
print("=" * 80)

# Seuil de validation au Maroc (généralement 10/20 ou 12/20)
SEUIL_VALIDATION = 10  # Note minimale pour valider un module

# Définir les statuts nécessitant un soutien
statuts_problematiques = ['Non_Validé', 'Absent', 'Exclu', 'Abandon', 'En_Attente', 'Fail', 'Debarred', 'Withdrawal', 'Withhold']

def needs_support_ma(row):
    """
    Détermine si un étudiant marocain a besoin de soutien pour un module.
    Critères adaptés au système universitaire marocain:
    1. Statut = Non Validé / Ajourné
    2. Note < 10/20 (seuil de validation standard)
    3. Patterns d'absentéisme ou exclusion
    4. Risque de redoublement
    """
    # Critère 1: Non validation explicite
    if row['Status'] == 'Fail' or row['Statut_MA'] == 'Non_Validé':
        return 1
    
    # Critère 2: Note insuffisante (< 10/20)
    if pd.notna(row['Note_sur_20']) and row['Note_sur_20'] > 0 and row['Note_sur_20'] < SEUIL_VALIDATION:
        return 1
    
    # Critère 3: Note originale faible (si sur 100, < 50)
    if pd.notna(row['Total']) and row['Total'] > 0 and row['Total'] < 50:
        return 1
    
    # Critère 4: Patterns problématiques (absentéisme, exclusion, abandon)
    if row['Statut_MA'] in ['Absent', 'Exclu', 'Abandon']:
        return 1
    
    # Critère 5: En attente (généralement problème administratif ou académique)
    if row['Statut_MA'] == 'En_Attente':
        return 1
    
    return 0

df['Needs_Support'] = df.apply(needs_support_ma, axis=1)

# Classification selon le système marocain
def classification_ma(note):
    """Classification des notes selon le barème marocain"""
    if pd.isna(note) or note == 0:
        return 'Non_Évalué'
    elif note >= 16:
        return 'Très_Bien'
    elif note >= 14:
        return 'Bien'
    elif note >= 12:
        return 'Assez_Bien'
    elif note >= 10:
        return 'Passable'
    else:
        return 'Non_Validé'

df['Mention'] = df['Note_sur_20'].apply(classification_ma)

print(f"\n🎯 Variable Cible créée: Needs_Support (Besoin de Soutien)")
print(f"   • Seuil de validation: {SEUIL_VALIDATION}/20")
print(f"   • Étudiants nécessitant un soutien: {df['Needs_Support'].sum():,} ({df['Needs_Support'].mean()*100:.1f}%)")
print(f"   • Étudiants sans besoin identifié: {(1-df['Needs_Support']).sum():,} ({(1-df['Needs_Support'].mean())*100:.1f}%)")

print(f"\n📊 Répartition par Mention:")
mention_counts = df['Mention'].value_counts()
for mention in ['Très_Bien', 'Bien', 'Assez_Bien', 'Passable', 'Non_Validé', 'Non_Évalué']:
    if mention in mention_counts.index:
        count = mention_counts[mention]
        pct = count / len(df) * 100
        print(f"   • {mention}: {count:,} ({pct:.1f}%)")

# =============================================================================
# 3. FEATURE ENGINEERING AVANCÉ - Contexte Universitaire Marocain
# =============================================================================
print("\n" + "=" * 80)
print("🔧 ÉTAPE 3: FEATURE ENGINEERING (Contexte Universitaire Marocain)")
print("=" * 80)

# 3.1 Performance du groupe de pairs (Filière + Année)
print("\n📈 3.1 Calcul de la performance par promotion (Filière + Année)...")
peer_group = df.groupby(['Filiere', 'Annee']).agg({
    'Total': 'mean',
    'Note_sur_20': 'mean',
    'Practical': 'mean',
    'Theoretical': 'mean',
    'Needs_Support': 'mean'
}).reset_index()
peer_group.columns = ['Filiere', 'Annee', 'peer_group_avg_total', 'peer_group_avg_note20',
                      'peer_group_avg_practical', 'peer_group_avg_theoretical',
                      'peer_group_support_rate']

df = df.merge(peer_group, on=['Filiere', 'Annee'], how='left')

# Écart par rapport à la promotion
df['deviation_from_peer'] = df['Total'] - df['peer_group_avg_total'].fillna(0)
df['deviation_note20'] = df['Note_sur_20'] - df['peer_group_avg_note20'].fillna(0)

# 3.2 Profil de Performance Étudiant (Historique)
print("📈 3.2 Création du profil de performance étudiant...")
student_profile = df.groupby('ID').agg({
    'Total': ['mean', 'std', 'min', 'max', 'count'],
    'Note_sur_20': ['mean', 'min'],
    'Practical': 'mean',
    'Theoretical': 'mean',
    'Needs_Support': ['sum', 'mean']
}).reset_index()
student_profile.columns = ['ID', 'student_avg_total', 'student_std_total', 
                           'student_min_total', 'student_max_total', 'student_module_count',
                           'student_avg_note20', 'student_min_note20',
                           'student_avg_practical', 'student_avg_theoretical',
                           'student_support_count', 'student_support_rate']
student_profile['student_std_total'] = student_profile['student_std_total'].fillna(0)

# Indicateur de risque de redoublement (plusieurs modules non validés)
student_profile['risque_redoublement'] = (student_profile['student_support_count'] >= 3).astype(int)

df = df.merge(student_profile, on='ID', how='left')

# 3.3 Difficulté des Modules
print("📈 3.3 Calcul du score de difficulté par module...")
module_stats = df.groupby('Module').agg({
    'Total': 'mean',
    'Note_sur_20': 'mean',
    'Needs_Support': 'mean',
    'ID': 'count'
}).reset_index()
module_stats.columns = ['Module', 'module_avg_total', 'module_avg_note20', 'module_taux_echec', 'module_effectif']

# Classifier les modules par difficulté
def classifier_difficulte_module(taux_echec):
    if taux_echec >= 0.5:
        return 'Très_Difficile'
    elif taux_echec >= 0.3:
        return 'Difficile'
    elif taux_echec >= 0.15:
        return 'Moyen'
    else:
        return 'Accessible'

module_stats['difficulte_module'] = module_stats['module_taux_echec'].apply(classifier_difficulte_module)

df = df.merge(module_stats, on='Module', how='left')

# 3.4 Combinaisons Filière-Module à Haut Risque
print("📈 3.4 Identification des combinaisons Filière-Module à haut risque...")
filiere_module = df.groupby(['Filiere', 'Module']).agg({
    'Needs_Support': 'mean',
    'ID': 'count'
}).reset_index()
filiere_module.columns = ['Filiere', 'Module', 'combo_taux_echec', 'combo_effectif']
filiere_module['combo_haut_risque'] = (filiere_module['combo_taux_echec'] > 0.3).astype(int)

df = df.merge(filiere_module[['Filiere', 'Module', 'combo_taux_echec', 'combo_haut_risque']], 
              on=['Filiere', 'Module'], how='left')

# 3.5 Charge de Travail par Semestre
print("📈 3.5 Calcul de la charge de travail par semestre...")
workload = df.groupby(['ID', 'AnneUniversitaire', 'Semester'])['Module'].nunique().reset_index()
workload.columns = ['ID', 'AnneUniversitaire', 'Semester', 'charge_semestre']

df = df.merge(workload, on=['ID', 'AnneUniversitaire', 'Semester'], how='left')

# 3.6 Pattern d'Absentéisme
print("📈 3.6 Détection des patterns d'absentéisme...")
absence_pattern = df.groupby('ID').apply(
    lambda x: (x['Statut_MA'].isin(['Absent', 'Exclu', 'Abandon'])).sum() / len(x)
).reset_index()
absence_pattern.columns = ['ID', 'taux_absenteisme']

df = df.merge(absence_pattern, on='ID', how='left')

# 3.7 Équilibre TP/Cours (Pratique vs Théorique)
print("📈 3.7 Calcul de l'équilibre TP/Cours...")
df['ratio_pratique'] = df['Practical'] / (df['Total'] + 1)
df['ecart_theorie_pratique'] = df['Theoretical'] - df['Practical']

# 3.8 Catégorie de Performance
print("📈 3.8 Analyse des tendances de performance...")
df['categorie_performance'] = pd.cut(df['Note_sur_20'], 
                                      bins=[-1, 6, 10, 12, 14, 20], 
                                      labels=['Critique', 'En_Difficulté', 'Passable', 'Bien', 'Excellent'])

# 3.9 Profil de Force par Catégorie de Module (Pôles de compétences)
print("📈 3.9 Profil de force étudiant par pôle de compétences...")

def categoriser_module(module):
    """Catégorisation des modules selon les pôles de compétences marocains"""
    module_lower = str(module).lower()
    
    # Sciences fondamentales
    if any(word in module_lower for word in ['رياضيات', 'math', 'جبر', 'algebra', 'analyse', 'probabilité']):
        return 'Mathematiques'
    elif any(word in module_lower for word in ['فيزياء', 'physics', 'physique', 'mécanique', 'thermodynamique']):
        return 'Physique'
    
    # Sciences de l'ingénieur
    elif any(word in module_lower for word in ['كهربائية', 'electrical', 'électrique', 'دارات', 'circuits']):
        return 'Electrique'
    elif any(word in module_lower for word in ['الكترون', 'electron', 'électronique']):
        return 'Electronique'
    elif any(word in module_lower for word in ['ميكانيك', 'mechanical', 'mécanique', 'rdm']):
        return 'Mecanique'
    elif any(word in module_lower for word in ['تحكم', 'control', 'automatique', 'régulation']):
        return 'Automatique'
    
    # Informatique
    elif any(word in module_lower for word in ['برمج', 'program', 'حاسوب', 'computer', 'informatique', 'algorithme']):
        return 'Informatique'
    
    # Langues et communication
    elif any(word in module_lower for word in ['انكليزية', 'english', 'لغة', 'français', 'communication', 'tec']):
        return 'Langues_Communication'
    
    # Gestion et économie
    elif any(word in module_lower for word in ['اقتصاد', 'économie', 'gestion', 'management', 'comptabilité']):
        return 'Gestion_Economie'
    
    else:
        return 'Autres'

df['pole_competence'] = df['Module'].apply(categoriser_module)

# Performance par pôle de compétences
pole_perf = df.groupby(['ID', 'pole_competence'])['Note_sur_20'].mean().unstack(fill_value=0)
pole_perf = pole_perf.add_prefix('force_')
pole_perf = pole_perf.reset_index()

df = df.merge(pole_perf, on='ID', how='left')

# 3.10 Indicateurs spécifiques au système marocain
print("📈 3.10 Indicateurs spécifiques au système LMD marocain...")

# Nombre de modules en rattrapage potentiel
df['modules_rattrapage'] = df.groupby('ID')['Needs_Support'].transform('sum')

# Distance au seuil de validation
df['distance_seuil'] = df['Note_sur_20'] - SEUIL_VALIDATION

print(f"\n✅ Feature Engineering terminé!")
print(f"   • Nombre de features créées: {len([c for c in df.columns if c not in ['index', 'ID', 'Module', 'Status', 'AnneUniversitaire', 'Filiere']])}")

# =============================================================================
# 4. PRÉPARATION DES DONNÉES POUR LA MODÉLISATION
# =============================================================================
print("\n" + "=" * 80)
print("🔧 ÉTAPE 4: PRÉPARATION POUR LA MODÉLISATION")
print("=" * 80)

# Sélectionner les features pour le modèle
feature_columns = [
    'Practical', 'Theoretical', 'Total', 'Note_sur_20', 'Semester', 'Annee',
    'peer_group_avg_total', 'peer_group_avg_note20', 'peer_group_avg_practical', 'peer_group_support_rate',
    'deviation_from_peer', 'deviation_note20', 'student_avg_total', 'student_std_total',
    'student_min_total', 'student_max_total', 'student_module_count',
    'student_avg_note20', 'student_min_note20',
    'student_avg_practical', 'student_avg_theoretical', 'student_support_rate',
    'module_avg_total', 'module_avg_note20', 'module_taux_echec', 'module_effectif',
    'combo_taux_echec', 'combo_haut_risque', 'charge_semestre',
    'taux_absenteisme', 'ratio_pratique', 'ecart_theorie_pratique',
    'modules_rattrapage', 'distance_seuil'
]

# Ajouter les colonnes de force par pôle de compétences
force_cols = [c for c in df.columns if c.startswith('force_')]
feature_columns.extend(force_cols)

# Encoder les variables catégorielles
le_filiere = LabelEncoder()
df['Filiere_encoded'] = le_filiere.fit_transform(df['Filiere'].fillna('Inconnue'))
feature_columns.append('Filiere_encoded')

# Encoder le pôle de compétences
le_pole = LabelEncoder()
df['pole_encoded'] = le_pole.fit_transform(df['pole_competence'].fillna('Autres'))
feature_columns.append('pole_encoded')

# Créer le DataFrame de features (garder seulement les colonnes existantes)
available_features = [c for c in feature_columns if c in df.columns]
X = df[available_features].copy()
y = df['Needs_Support']

# Remplir les valeurs manquantes
X = X.fillna(0)

# Remplacer les infinis
X = X.replace([np.inf, -np.inf], 0)

print(f"\n📊 Dimensions des données:")
print(f"   • Features (X): {X.shape}")
print(f"   • Target (y): {y.shape}")
print(f"   • Features sélectionnées: {len(available_features)}")
print(f"   • Filières: {df['Filiere'].nunique()}")

# Mise à jour de feature_columns pour utiliser les features disponibles
feature_columns = available_features

# Split des données
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📊 Split Train/Test:")
print(f"   • Training: {len(X_train):,} échantillons")
print(f"   • Test: {len(X_test):,} échantillons")

# Standardisation
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =============================================================================
# 5. CLUSTERING DES ÉTUDIANTS (Profils d'Apprenants)
# =============================================================================
print("\n" + "=" * 80)
print("🔷 ÉTAPE 5: CLUSTERING DES PROFILS D'APPRENANTS")
print("=" * 80)

# Clustering sur les profils étudiants
print("\n📊 Identification des profils d'apprenants par K-Means...")

# Déterminer le nombre optimal de clusters avec l'inertie
inertias = []
K_range = range(2, 10)
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_train_scaled)
    inertias.append(kmeans.inertia_)

# Utiliser K=5 clusters (profils types d'étudiants marocains)
n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
cluster_labels_train = kmeans.fit_predict(X_train_scaled)
cluster_labels_test = kmeans.predict(X_test_scaled)

# Nommer les clusters selon les profils
profil_names = {
    0: "Excellence",
    1: "Régulier", 
    2: "En_Progression",
    3: "En_Difficulté",
    4: "À_Risque"
}

# Analyser les clusters
print(f"\n📊 Analyse des {n_clusters} profils d'apprenants:")
cluster_analysis = []
for i in range(n_clusters):
    mask = cluster_labels_train == i
    support_rate = y_train.iloc[mask].mean() * 100
    size = mask.sum()
    cluster_analysis.append((i, size, support_rate))

# Trier par taux de soutien pour attribuer les noms
cluster_analysis.sort(key=lambda x: x[2])
profil_mapping = {}
profil_labels = ["Excellence", "Régulier", "En_Progression", "En_Difficulté", "À_Risque"]
for idx, (cluster_id, size, rate) in enumerate(cluster_analysis):
    profil_mapping[cluster_id] = profil_labels[idx]
    print(f"   • Profil '{profil_labels[idx]}' (Cluster {cluster_id}): {size:,} étudiants, Taux de soutien: {rate:.1f}%")

# Visualisation des clusters
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Elbow curve
axes[0].plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
axes[0].set_xlabel('Nombre de Profils (K)', fontsize=12)
axes[0].set_ylabel('Inertie', fontsize=12)
axes[0].set_title('Méthode du Coude - Sélection du Nombre de Profils', fontsize=14, fontweight='bold')
axes[0].axvline(x=n_clusters, color='r', linestyle='--', label=f'K choisi = {n_clusters}')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Cluster distribution avec noms de profils
cluster_support = pd.DataFrame({
    'Cluster': cluster_labels_train,
    'Needs_Support': y_train.values
})
cluster_summary = cluster_support.groupby('Cluster')['Needs_Support'].agg(['sum', 'count', 'mean'])
cluster_summary['mean'] = cluster_summary['mean'] * 100

colors = plt.cm.RdYlGn_r(cluster_summary['mean'] / 100)
bars = axes[1].bar(range(len(cluster_summary)), cluster_summary['mean'], color=colors, edgecolor='black')
axes[1].set_xticks(range(len(cluster_summary)))
axes[1].set_xticklabels([profil_mapping.get(i, f'Profil {i}') for i in cluster_summary.index], rotation=45, ha='right')
axes[1].set_xlabel('Profil d\'Apprenant', fontsize=12)
axes[1].set_ylabel('Taux de Besoin de Soutien (%)', fontsize=12)
axes[1].set_title('Taux de Soutien par Profil d\'Apprenant', fontsize=14, fontweight='bold')
axes[1].axhline(y=50, color='r', linestyle='--', alpha=0.7, label='Seuil 50%')
for bar, (idx, row) in zip(bars, cluster_summary.iterrows()):
    axes[1].annotate(f'n={int(row["count"])}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                     ha='center', va='bottom', fontsize=10)
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'profils_apprenants.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"\n✅ Visualisation des profils sauvegardée: profils_apprenants.png")

# =============================================================================
# 6. COLLABORATIVE FILTERING (Similarité entre Étudiants Marocains)
# =============================================================================
print("\n" + "=" * 80)
print("🤝 ÉTAPE 6: SYSTÈME DE RECOMMANDATION COLLABORATIF")
print("=" * 80)

print("\n📊 Construction du système de recommandation basé sur la similarité...")

# Créer une matrice étudiant-module pour le collaborative filtering
student_module_matrix = df.pivot_table(
    index='ID', 
    columns='Module', 
    values='Note_sur_20', 
    aggfunc='mean'
).fillna(0)

print(f"   • Matrice Étudiant-Module: {student_module_matrix.shape}")
print(f"   • Étudiants: {student_module_matrix.shape[0]}")
print(f"   • Modules: {student_module_matrix.shape[1]}")

# Trouver les voisins les plus proches (étudiants similaires)
n_neighbors = min(10, len(student_module_matrix) - 1)
nn_model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
nn_model.fit(student_module_matrix.values)

def recommander_soutien(student_id, student_matrix, nn_model, df):
    """
    Recommande des modules nécessitant du soutien basé sur des étudiants 
    au profil similaire (système de recommandation collaboratif).
    
    Logique: Si des étudiants similaires ont eu des difficultés dans certains
    modules, l'étudiant actuel risque aussi d'avoir des difficultés.
    """
    if student_id not in student_matrix.index:
        return {}
    
    student_vec = student_matrix.loc[student_id].values.reshape(1, -1)
    distances, indices = nn_model.kneighbors(student_vec)
    
    # Étudiants similaires (exclure l'étudiant lui-même)
    similar_students = student_matrix.index[indices[0][1:]]
    
    # Modules problématiques chez les étudiants similaires
    similar_df = df[df['ID'].isin(similar_students)]
    modules_risque = similar_df[similar_df['Needs_Support'] == 1]['Module'].value_counts()
    
    return modules_risque.head(5).to_dict()

# Exemples de recommandations
sample_students = df['ID'].unique()[:3]
print("\n📋 Exemples de recommandations pour étudiants:")
for student in sample_students:
    recommendations = recommander_soutien(student, student_module_matrix, nn_model, df)
    if recommendations:
        filiere = df[df['ID'] == student]['Filiere'].iloc[0] if len(df[df['ID'] == student]) > 0 else 'Inconnue'
        print(f"\n   🎓 Étudiant {student} (Filière: {filiere}):")
        print(f"      Modules à surveiller (basé sur étudiants similaires):")
        for module, count in list(recommendations.items())[:3]:
            module_display = module[:50] + '...' if len(str(module)) > 50 else module
            print(f"      • {module_display}: {count} étudiants similaires en difficulté")

# =============================================================================
# 7. MODÈLE XGBOOST AVEC CALIBRATION (Prédiction du Besoin de Soutien)
# =============================================================================
print("\n" + "=" * 80)
print("🚀 ÉTAPE 7: MODÈLE DE PRÉDICTION XGBOOST")
print("=" * 80)

# Entraîner XGBoost
print("\n📊 Entraînement du modèle XGBoost pour prédire le besoin de soutien...")

xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)

xgb_model.fit(X_train_scaled, y_train)

# Calibration des probabilités pour des scores de risque fiables
print("📊 Calibration des probabilités pour scoring de risque...")
calibrated_model = CalibratedClassifierCV(xgb_model, method='sigmoid', cv=5)
calibrated_model.fit(X_train_scaled, y_train)

# Prédictions
y_pred = calibrated_model.predict(X_test_scaled)
y_proba = calibrated_model.predict_proba(X_test_scaled)[:, 1]

# Évaluation
print("\n📊 RÉSULTATS DU MODÈLE DE PRÉDICTION:")
print("-" * 50)
print(classification_report(y_test, y_pred, target_names=['Validé', 'Besoin_Soutien']))

# Métriques supplémentaires
roc_auc = roc_auc_score(y_test, y_proba)
avg_precision = average_precision_score(y_test, y_proba)
f1 = f1_score(y_test, y_pred)

print(f"\n📈 Métriques de Performance:")
print(f"   • ROC-AUC Score: {roc_auc:.4f}")
print(f"   • Average Precision: {avg_precision:.4f}")
print(f"   • F1-Score: {f1:.4f}")

# Cross-validation
print("\n📊 Validation croisée (5-fold)...")
cv_scores = cross_val_score(xgb_model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
print(f"   • ROC-AUC moyen: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

# =============================================================================
# 7.1 SAUVEGARDE DU MODÈLE POUR PRÉDICTIONS EXTERNES
# =============================================================================
print("\n💾 Sauvegarde du modèle pour prédictions futures...")
import joblib

# Sauvegarder le modèle calibré, le scaler, et les métadonnées
model_data = {
    'model': calibrated_model,
    'xgb_model': xgb_model,
    'scaler': scaler,
    'feature_columns': feature_columns,
    'le_filiere': le_filiere,
    'le_pole': le_pole,
    'kmeans': kmeans,
    'profil_mapping': profil_mapping,
    'seuil_validation': SEUIL_VALIDATION
}

joblib.dump(model_data, OUTPUT_PATH / 'model_soutien_pedagogique.joblib')
print(f"   ✅ Modèle sauvegardé: model_soutien_pedagogique.joblib")

# =============================================================================
# 8. IMPORTANCE DES FACTEURS DE RISQUE
# =============================================================================
print("\n" + "=" * 80)
print("📊 ÉTAPE 8: FACTEURS DE RISQUE LES PLUS IMPORTANTS")
print("=" * 80)

# Feature importance
feature_importance = pd.DataFrame({
    'facteur': feature_columns,
    'importance': xgb_model.feature_importances_
}).sort_values('importance', ascending=False)

# Renommer les features pour le contexte marocain
feature_names_ma = {
    'student_support_rate': 'Historique_Echecs_Etudiant',
    'module_taux_echec': 'Difficulté_Module',
    'taux_absenteisme': 'Taux_Absentéisme',
    'deviation_from_peer': 'Écart_Promotion',
    'student_avg_note20': 'Moyenne_Générale_Étudiant',
    'combo_taux_echec': 'Risque_Filière_Module',
    'distance_seuil': 'Distance_Seuil_Validation',
    'Note_sur_20': 'Note_Module',
    'charge_semestre': 'Charge_Semestre',
    'Annee': 'Année_Études'
}

feature_importance['facteur_ma'] = feature_importance['facteur'].map(
    lambda x: feature_names_ma.get(x, x)
)

print("\n🔝 Top 15 Facteurs de Risque les plus importants:")
for i, row in feature_importance.head(15).iterrows():
    rank = list(feature_importance.index).index(i) + 1
    print(f"   {rank:2d}. {row['facteur_ma']}: {row['importance']:.4f}")

# Visualisation
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Feature importance
top_features = feature_importance.head(15)
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features)))
bars = axes[0].barh(range(len(top_features)), top_features['importance'].values, color=colors)
axes[0].set_yticks(range(len(top_features)))
axes[0].set_yticklabels(top_features['facteur_ma'].values)
axes[0].invert_yaxis()
axes[0].set_xlabel('Importance', fontsize=12)
axes[0].set_title('Top 15 Facteurs de Risque - Importance XGBoost', fontsize=14, fontweight='bold')
axes[0].grid(True, alpha=0.3, axis='x')

# Confusion Matrix avec labels marocains
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1],
            xticklabels=['Validé', 'Besoin Soutien'],
            yticklabels=['Validé', 'Besoin Soutien'])
axes[1].set_xlabel('Prédit', fontsize=12)
axes[1].set_ylabel('Réel', fontsize=12)
axes[1].set_title('Matrice de Confusion', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'performance_modele.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"\n✅ Visualisation performance sauvegardée: performance_modele.png")

# =============================================================================
# 9. SYSTÈME DE SCORING DE RISQUE (Priorisation Marocaine)
# =============================================================================
print("\n" + "=" * 80)
print("⚠️ ÉTAPE 9: SYSTÈME DE SCORING ET PRIORISATION")
print("=" * 80)

# Ajouter les scores de risque au dataset
df_test = df.iloc[X_test.index].copy()
df_test['score_risque'] = y_proba
df_test['cluster'] = cluster_labels_test
df_test['profil_apprenant'] = df_test['cluster'].map(profil_mapping)
df_test['besoin_soutien_predit'] = y_pred

# Catégoriser les risques selon le système marocain
def categorie_risque(score):
    """
    Catégorisation du risque adaptée au contexte universitaire marocain:
    - CRITIQUE: Risque très élevé de non-validation / redoublement
    - ÉLEVÉ: Nécessite intervention urgente
    - MODÉRÉ: Suivi recommandé
    - FAIBLE: Accompagnement léger
    - MINIMAL: Pas d'intervention nécessaire
    """
    if score >= 0.8:
        return 'CRITIQUE'
    elif score >= 0.6:
        return 'ÉLEVÉ'
    elif score >= 0.4:
        return 'MODÉRÉ'
    elif score >= 0.2:
        return 'FAIBLE'
    else:
        return 'MINIMAL'

df_test['categorie_risque'] = df_test['score_risque'].apply(categorie_risque)

# Recommandation d'action
def recommander_action(cat_risque, note):
    if cat_risque == 'CRITIQUE':
        return "Tutorat individuel + Convocation conseiller pédagogique"
    elif cat_risque == 'ÉLEVÉ':
        return "Inscription TD de soutien + Suivi bi-hebdomadaire"
    elif cat_risque == 'MODÉRÉ':
        return "Groupes d'entraide + Ressources en ligne"
    elif cat_risque == 'FAIBLE':
        return "Auto-évaluation + Permanences optionnelles"
    else:
        return "Encouragement + Ressources avancées"

df_test['action_recommandee'] = df_test.apply(
    lambda row: recommander_action(row['categorie_risque'], row['Note_sur_20']), axis=1
)

print("\n📊 Distribution des catégories de risque:")
risk_dist = df_test['categorie_risque'].value_counts()
for cat in ['CRITIQUE', 'ÉLEVÉ', 'MODÉRÉ', 'FAIBLE', 'MINIMAL']:
    if cat in risk_dist.index:
        count = risk_dist[cat]
        pct = count / len(df_test) * 100
        emoji = {'CRITIQUE': '🔴', 'ÉLEVÉ': '🟠', 'MODÉRÉ': '🟡', 'FAIBLE': '🟢', 'MINIMAL': '⚪'}
        print(f"   {emoji.get(cat, '•')} {cat}: {count:,} étudiants ({pct:.1f}%)")

# =============================================================================
# 10. ANALYSE DES COMBINAISONS FILIÈRE-MODULE À HAUT RISQUE
# =============================================================================
print("\n" + "=" * 80)
print("🔴 ÉTAPE 10: COMBINAISONS FILIÈRE-MODULE À SURVEILLER")
print("=" * 80)

high_risk_combos = df.groupby(['Filiere', 'Module']).agg({
    'Needs_Support': ['mean', 'sum', 'count'],
    'Note_sur_20': 'mean'
}).reset_index()
high_risk_combos.columns = ['Filiere', 'Module', 'taux_echec', 'nb_echecs', 'effectif', 'moyenne_module']
high_risk_combos = high_risk_combos[high_risk_combos['effectif'] >= 10]  # Au moins 10 étudiants
high_risk_combos = high_risk_combos.sort_values('taux_echec', ascending=False)

print("\n🔴 Combinaisons Filière-Module avec taux d'échec > 50%:")
print("-" * 90)
high_risk_top = high_risk_combos[high_risk_combos['taux_echec'] > 0.5].head(15)
for i, row in high_risk_top.iterrows():
    module_display = row['Module'][:35] + '...' if len(str(row['Module'])) > 35 else row['Module']
    print(f"   📚 {row['Filiere']} - {module_display}")
    print(f"      Taux échec: {row['taux_echec']*100:.1f}% | Échecs: {int(row['nb_echecs'])}/{int(row['effectif'])} | Moy: {row['moyenne_module']:.1f}/20")

# Visualisation des risques
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Distribution des catégories de risque
risk_order = ['MINIMAL', 'FAIBLE', 'MODÉRÉ', 'ÉLEVÉ', 'CRITIQUE']
risk_counts = df_test['categorie_risque'].value_counts().reindex(risk_order).fillna(0)
colors = ['#27ae60', '#f1c40f', '#e67e22', '#e74c3c', '#8e44ad']
axes[0].bar(risk_counts.index, risk_counts.values, color=colors, edgecolor='black')
axes[0].set_xlabel('Catégorie de Risque', fontsize=12)
axes[0].set_ylabel('Nombre d\'Étudiants', fontsize=12)
axes[0].set_title('Distribution des Niveaux de Risque\n(Système Universitaire Marocain)', fontsize=14, fontweight='bold')
for i, v in enumerate(risk_counts.values):
    axes[0].annotate(f'{int(v):,}', xy=(i, v), ha='center', va='bottom', fontsize=11)
axes[0].grid(True, alpha=0.3, axis='y')

# Distribution des scores de risque
axes[1].hist(y_proba[y_test == 0], bins=50, alpha=0.7, label='Validé', color='green', density=True)
axes[1].hist(y_proba[y_test == 1], bins=50, alpha=0.7, label='Besoin Soutien', color='red', density=True)
axes[1].axvline(x=0.5, color='black', linestyle='--', label='Seuil 0.5')
axes[1].axvline(x=0.8, color='purple', linestyle='--', alpha=0.7, label='Seuil Critique')
axes[1].set_xlabel('Score de Risque', fontsize=12)
axes[1].set_ylabel('Densité', fontsize=12)
axes[1].set_title('Distribution des Scores de Risque', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'analyse_risques.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"\n✅ Visualisation risques sauvegardée: analyse_risques.png")

# =============================================================================
# 11. RECOMMANDATIONS D'ALLOCATION DES RESSOURCES DE SOUTIEN
# =============================================================================
print("\n" + "=" * 80)
print("👨‍🏫 ÉTAPE 11: PLAN D'ALLOCATION DES RESSOURCES DE SOUTIEN")
print("=" * 80)

# Priorité par module
module_priority = df_test[df_test['categorie_risque'].isin(['CRITIQUE', 'ÉLEVÉ'])].groupby('Module').agg({
    'score_risque': 'mean',
    'ID': 'count',
    'Note_sur_20': 'mean'
}).reset_index()
module_priority.columns = ['Module', 'score_risque_moy', 'nb_etudiants', 'moyenne_module']
module_priority = module_priority.sort_values('score_risque_moy', ascending=False)

print("\n📋 MODULES PRIORITAIRES POUR LE TUTORAT (TD de Soutien):")
print("-" * 90)
print(f"{'Rang':<5} {'Module':<40} {'Score Risque':<15} {'Étudiants':<12} {'Moyenne':<10}")
print("-" * 90)
for i, row in module_priority.head(10).iterrows():
    rank = list(module_priority.index).index(i) + 1
    module_name = row['Module'][:37] + '...' if len(str(row['Module'])) > 40 else row['Module']
    print(f"{rank:<5} {module_name:<40} {row['score_risque_moy']:.3f}          {int(row['nb_etudiants']):<12} {row['moyenne_module']:.1f}/20")

# Recommandations par profil d'apprenant
print("\n📋 STRATÉGIE DE SOUTIEN PAR PROFIL D'APPRENANT:")
print("-" * 70)

strategies_ma = {
    'À_Risque': """🔴 INTERVENTION URGENTE
      • Convocation par le conseiller pédagogique
      • Tutorat individuel (2h/semaine minimum)
      • Contrat pédagogique personnalisé
      • Suivi psychologique si nécessaire
      • Orientation vers les permanences de soutien""",
    
    'En_Difficulté': """🟠 SOUTIEN RENFORCÉ
      • Inscription obligatoire aux TD de soutien
      • Groupes de travail dirigés
      • Exercices de rattrapage hebdomadaires
      • Suivi bi-hebdomadaire par le tuteur
      • Accès prioritaire aux ressources numériques""",
    
    'En_Progression': """🟡 ACCOMPAGNEMENT MODÉRÉ
      • Sessions de révision optionnelles
      • Groupes d'entraide entre étudiants
      • Auto-évaluation régulière
      • Permanences des enseignants""",
    
    'Régulier': """🟢 CONSOLIDATION
      • Ressources en ligne complémentaires
      • Préparation aux examens
      • Encouragement à l'excellence""",
    
    'Excellence': """⭐ ENCOURAGEMENT
      • Programmes d'excellence
      • Tutorat par les pairs (comme tuteur)
      • Projets avancés
      • Préparation concours et bourses"""
}

for profil in ['À_Risque', 'En_Difficulté', 'En_Progression', 'Régulier', 'Excellence']:
    if profil in df_test['profil_apprenant'].values:
        profil_data = df_test[df_test['profil_apprenant'] == profil]
        size = len(profil_data)
        moy = profil_data['Note_sur_20'].mean()
        print(f"\n{profil.upper()} ({size} étudiants, moyenne: {moy:.1f}/20):")
        if profil in strategies_ma:
            print(strategies_ma[profil])

# =============================================================================
# 12. EXPORT DES RÉSULTATS
# =============================================================================
print("\n" + "=" * 80)
print("💾 ÉTAPE 12: EXPORT DES RÉSULTATS")
print("=" * 80)

# Export des étudiants à risque élevé
etudiants_risque = df_test[df_test['categorie_risque'].isin(['CRITIQUE', 'ÉLEVÉ'])][
    ['ID', 'Filiere', 'Module', 'Note_sur_20', 'Statut_MA', 'score_risque', 
     'categorie_risque', 'profil_apprenant', 'action_recommandee']
].sort_values('score_risque', ascending=False)

etudiants_risque.to_csv(OUTPUT_PATH / 'etudiants_risque_eleve.csv', index=False, encoding='utf-8-sig')
print(f"\n✅ Liste étudiants à haut risque: etudiants_risque_eleve.csv ({len(etudiants_risque):,} enregistrements)")

# Export des recommandations par module
recommandations_modules = module_priority.copy()
recommandations_modules['rang_priorite'] = range(1, len(recommandations_modules) + 1)
recommandations_modules['tuteurs_recommandes'] = (recommandations_modules['nb_etudiants'] / 15).apply(lambda x: max(1, int(x)))
recommandations_modules['heures_td_soutien'] = recommandations_modules['tuteurs_recommandes'] * 2  # 2h par tuteur
recommandations_modules.to_csv(OUTPUT_PATH / 'recommandations_modules.csv', index=False, encoding='utf-8-sig')
print(f"✅ Recommandations par module: recommandations_modules.csv")

# Export du scoring complet
scoring_complet = df_test[['ID', 'Filiere', 'Module', 'Annee', 'Semester', 'Note_sur_20', 
                           'Statut_MA', 'Mention', 'score_risque', 'categorie_risque', 
                           'profil_apprenant', 'action_recommandee', 'besoin_soutien_predit']].copy()
scoring_complet.to_csv(OUTPUT_PATH / 'scoring_complet.csv', index=False, encoding='utf-8-sig')
print(f"✅ Scoring complet: scoring_complet.csv ({len(scoring_complet):,} enregistrements)")

# Export des combinaisons filière-module à risque
high_risk_combos.to_csv(OUTPUT_PATH / 'combinaisons_risque.csv', index=False, encoding='utf-8-sig')
print(f"✅ Combinaisons à risque: combinaisons_risque.csv")

# Export du plan d'action par filière
plan_filiere = df_test.groupby('Filiere').agg({
    'score_risque': 'mean',
    'Needs_Support': 'sum',
    'ID': 'count',
    'Note_sur_20': 'mean'
}).reset_index()
plan_filiere.columns = ['Filiere', 'score_risque_moy', 'etudiants_en_difficulte', 'effectif_total', 'moyenne_filiere']
plan_filiere['taux_difficulte'] = plan_filiere['etudiants_en_difficulte'] / plan_filiere['effectif_total'] * 100
plan_filiere = plan_filiere.sort_values('score_risque_moy', ascending=False)
plan_filiere.to_csv(OUTPUT_PATH / 'plan_action_filieres.csv', index=False, encoding='utf-8-sig')
print(f"✅ Plan d'action par filière: plan_action_filieres.csv")

# =============================================================================
# 13. TABLEAU DE BORD RÉCAPITULATIF
# =============================================================================
print("\n" + "=" * 80)
print("📊 TABLEAU DE BORD RÉCAPITULATIF")
print("=" * 80)

fig = plt.figure(figsize=(20, 14))

# 1. Distribution des risques (pie chart)
ax1 = fig.add_subplot(2, 3, 1)
risk_counts = df_test['categorie_risque'].value_counts()
colors_pie = {'MINIMAL': '#27ae60', 'FAIBLE': '#f1c40f', 'MODÉRÉ': '#e67e22', 'ÉLEVÉ': '#e74c3c', 'CRITIQUE': '#8e44ad'}
ax1.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%',
        colors=[colors_pie.get(x, 'gray') for x in risk_counts.index], startangle=90)
ax1.set_title('Distribution des Niveaux de Risque\n(Université Marocaine)', fontsize=12, fontweight='bold')

# 2. Performance par Filière
ax2 = fig.add_subplot(2, 3, 2)
filiere_perf = df.groupby('Filiere')['Needs_Support'].mean().sort_values(ascending=True)
colors_filiere = plt.cm.RdYlGn_r(filiere_perf.values)
bars = ax2.barh(filiere_perf.index, filiere_perf.values * 100, color=colors_filiere)
ax2.set_xlabel('Taux de Besoin de Soutien (%)')
ax2.set_title('Taux de Soutien par Filière', fontsize=12, fontweight='bold')
ax2.axvline(x=50, color='r', linestyle='--', alpha=0.7)

# 3. Évolution par année universitaire
ax3 = fig.add_subplot(2, 3, 3)
year_trend = df.groupby('AnneUniversitaire')['Needs_Support'].mean() * 100
ax3.plot(range(len(year_trend)), year_trend.values, 'bo-', linewidth=2, markersize=8)
ax3.set_xticks(range(len(year_trend)))
ax3.set_xticklabels(year_trend.index, rotation=45)
ax3.set_ylabel('Taux de Besoin de Soutien (%)')
ax3.set_title('Évolution par Année Universitaire', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

# 4. Top 10 modules à risque
ax4 = fig.add_subplot(2, 3, 4)
top_modules = df.groupby('Module')['Needs_Support'].mean().sort_values(ascending=False).head(10)
colors_mod = plt.cm.Reds(np.linspace(0.4, 0.9, len(top_modules)))
ax4.barh(range(len(top_modules)), top_modules.values * 100, color=colors_mod)
ax4.set_yticks(range(len(top_modules)))
ax4.set_yticklabels([s[:25] + '...' if len(str(s)) > 25 else s for s in top_modules.index], fontsize=9)
ax4.invert_yaxis()
ax4.set_xlabel('Taux de Besoin de Soutien (%)')
ax4.set_title('Top 10 Modules à Risque', fontsize=12, fontweight='bold')

# 5. Analyse par Profil d'Apprenant
ax5 = fig.add_subplot(2, 3, 5)
profil_risk = df_test.groupby('profil_apprenant').agg({
    'score_risque': 'mean',
    'ID': 'count'
}).reset_index()
profil_colors = {'Excellence': '#27ae60', 'Régulier': '#3498db', 'En_Progression': '#f1c40f', 
                 'En_Difficulté': '#e67e22', 'À_Risque': '#e74c3c'}
bars = ax5.bar(profil_risk['profil_apprenant'], profil_risk['score_risque'],
               color=[profil_colors.get(p, 'gray') for p in profil_risk['profil_apprenant']], edgecolor='black')
ax5.set_xlabel('Profil d\'Apprenant')
ax5.set_ylabel('Score de Risque Moyen')
ax5.set_title('Risque par Profil d\'Apprenant', fontsize=12, fontweight='bold')
ax5.tick_params(axis='x', rotation=45)
for bar, (_, row) in zip(bars, profil_risk.iterrows()):
    ax5.annotate(f'n={int(row["ID"])}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                 ha='center', va='bottom', fontsize=9)

# 6. Métriques clés
ax6 = fig.add_subplot(2, 3, 6)
ax6.axis('off')
nb_critique = len(df_test[df_test['categorie_risque']=='CRITIQUE']) if 'CRITIQUE' in df_test['categorie_risque'].values else 0
nb_eleve = len(df_test[df_test['categorie_risque']=='ÉLEVÉ']) if 'ÉLEVÉ' in df_test['categorie_risque'].values else 0
nb_modules_surveiller = len(module_priority[module_priority['score_risque_moy'] > 0.5]) if len(module_priority) > 0 else 0
metrics_text = f"""
╔══════════════════════════════════════════════════════╗
║    🇲🇦 MÉTRIQUES - SYSTÈME UNIVERSITAIRE MAROCAIN   ║
╠══════════════════════════════════════════════════════╣
║  📊 Total Étudiants Analysés: {len(df):,}            
║  🎯 ROC-AUC Score: {roc_auc:.4f}                     
║  📈 F1-Score: {f1:.4f}                               
║  🔍 Précision Moyenne: {avg_precision:.4f}           
║                                                      
║  ⚠️ Étudiants Risque CRITIQUE: {nb_critique:,}
║  🔴 Étudiants Risque ÉLEVÉ: {nb_eleve:,}
║  📚 Modules à Surveiller: {nb_modules_surveiller}
║  🏷️ Profils Identifiés: {n_clusters}               
║                                                      
║  💡 RECOMMANDATION:                                  
║  Allouer {int((nb_critique + nb_eleve)/15)} tuteurs minimum
║  Ouvrir {nb_modules_surveiller} TD de soutien                      
╚══════════════════════════════════════════════════════╝
"""
ax6.text(0.05, 0.5, metrics_text, transform=ax6.transAxes, fontsize=10,
         verticalalignment='center', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.suptitle('🔵 Système de Recommandation de Soutien Pédagogique\n🇲🇦 Adapté pour les Universités Marocaines', 
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'tableau_bord_soutien.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"\n✅ Tableau de bord sauvegardé: tableau_bord_soutien.png")

# =============================================================================
# RÉSUMÉ FINAL
# =============================================================================
print("\n" + "=" * 80)
print("🎯 RÉSUMÉ FINAL - SYSTÈME DE SOUTIEN PÉDAGOGIQUE MAROCAIN")
print("=" * 80)

nb_critique = len(df_test[df_test['categorie_risque']=='CRITIQUE']) if 'CRITIQUE' in df_test['categorie_risque'].values else 0
nb_eleve = len(df_test[df_test['categorie_risque']=='ÉLEVÉ']) if 'ÉLEVÉ' in df_test['categorie_risque'].values else 0

print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║      🇲🇦 PROJET 4: SYSTÈME DE SOUTIEN - UNIVERSITÉS MAROCAINES              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📊 DONNÉES ANALYSÉES:                                                       ║
║     • {len(df):,} inscriptions étudiants                                     
║     • {df['ID'].nunique():,} étudiants uniques                               
║     • {df['Module'].nunique()} modules différents                            
║     • {df['Filiere'].nunique()} filières                                     
║                                                                              ║
║  🎯 PERFORMANCE DU MODÈLE:                                                   ║
║     • ROC-AUC: {roc_auc:.4f}                                                 
║     • F1-Score: {f1:.4f}                                                     
║     • Précision Moyenne: {avg_precision:.4f}                                 
║                                                                              ║
║  ⚠️ IDENTIFICATION DES BESOINS (Seuil validation: {SEUIL_VALIDATION}/20):   ║
║     • Taux global de besoin de soutien: {df['Needs_Support'].mean()*100:.1f}%
║     • Étudiants en situation CRITIQUE: {nb_critique:,}
║     • Étudiants à risque ÉLEVÉ: {nb_eleve:,}
║                                                                              ║
║  ✅ VALEUR AJOUTÉE POUR L'UNIVERSITÉ:                                        ║
║     • Identification précoce des étudiants à risque de redoublement          ║
║     • Allocation optimisée des TD de soutien par module                      ║
║     • Priorisation des interventions avec scoring de risque                  ║
║     • Profils d'apprenants pour stratégies pédagogiques ciblées              ║
║     • Système de recommandation collaboratif                                 ║
║                                                                              ║
║  💾 FICHIERS GÉNÉRÉS:                                                        ║
║     • etudiants_risque_eleve.csv - Étudiants prioritaires                    ║
║     • recommandations_modules.csv - Plan TD soutien par module               ║
║     • scoring_complet.csv - Scoring de tous les étudiants                    ║
║     • combinaisons_risque.csv - Filière-Module à surveiller                  ║
║     • plan_action_filieres.csv - Plan par filière                            ║
║     • tableau_bord_soutien.png - Dashboard visuel                            ║
║     • performance_modele.png - Métriques du modèle                           ║
║     • analyse_risques.png - Analyse des risques                              ║
║     • profils_apprenants.png - Clustering des profils                        ║
║                                                                              ║
║  📋 ACTIONS RECOMMANDÉES:                                                    ║
║     • Convoquer les {nb_critique} étudiants en situation critique            
║     • Ouvrir TD de soutien pour les modules à taux d'échec > 50%             ║
║     • Affecter {int((nb_critique + nb_eleve)/15)} tuteurs minimum            
║     • Mettre en place le suivi par profil d'apprenant                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

print("\n✅ Projet 4 terminé avec succès!")
print("🇲🇦 Système adapté au contexte universitaire marocain")
print("=" * 80)
