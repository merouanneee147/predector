# 📘 Documentation Technique
## Système de Recommandation Intelligente de Soutien Pédagogique
### 🇲🇦 Adapté pour les Établissements d'Enseignement Supérieur Marocains

---

## 📋 Table des Matières

1. [Aperçu du Projet](#1-aperçu-du-projet)
2. [Architecture du Système](#2-architecture-du-système)
3. [Préparation des Données](#3-préparation-des-données)
4. [Modèles de Machine Learning](#4-modèles-de-machine-learning)
5. [API Backend](#5-api-backend)
6. [Interface Frontend](#6-interface-frontend)
7. [Fonctionnalités Principales](#7-fonctionnalités-principales)
8. [Installation et Déploiement](#8-installation-et-déploiement)
9. [Performances du Modèle](#9-performances-du-modèle)
10. [Guide d'Utilisation](#10-guide-dutilisation)

---

## 1. Aperçu du Projet

### 1.1 Objectif

Le **Système de Recommandation Intelligente de Soutien Pédagogique** est une solution complète de Machine Learning conçue pour :

- ✅ **Identifier automatiquement** les étudiants à risque d'échec académique
- ✅ **Prédire les besoins de soutien** par combinaison étudiant-module
- ✅ **Recommander des actions personnalisées** pour chaque profil d'apprenant
- ✅ **Optimiser l'allocation des ressources** de tutorat et d'accompagnement

### 1.2 Contexte Marocain

Le système est spécifiquement adapté au contexte universitaire marocain :

| Critère | Valeur |
|---------|--------|
| Système | LMD (Licence-Master-Doctorat) |
| Seuil de validation | 10/20 |
| Échelle de notation | Sur 20 points |
| Mentions | Très Bien (≥16), Bien (≥14), Assez Bien (≥12), Passable (≥10) |

### 1.3 Variable Cible

Un étudiant est considéré comme **nécessitant un soutien** (`Needs_Support = 1`) si :

```
1. Statut = Non Validé / Ajourné / Rattrapage
2. Note < 10/20 (seuil de validation standard)
3. Patterns d'absentéisme ou d'exclusion
4. Risque de redoublement (≥3 modules non validés)
```

---

## 2. Architecture du Système

### 2.1 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ARCHITECTURE GLOBALE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────┐   │
│  │   Données    │───▶│   Pipeline ML    │───▶│   Modèle Entraîné    │   │
│  │   (CSV)      │    │   (Python)       │    │   (.joblib)          │   │
│  └──────────────┘    └──────────────────┘    └──────────────────────┘   │
│         │                                              │                 │
│         │                                              ▼                 │
│         │            ┌──────────────────────────────────────────┐       │
│         │            │           API Flask (Backend)             │       │
│         │            │              Port 5000                    │       │
│         └───────────▶│  • /api/stats       • /api/predict        │       │
│                      │  • /api/etudiants   • /api/rapports       │       │
│                      │  • /api/modules     • /api/alertes        │       │
│                      └──────────────────────────────────────────┘       │
│                                        │                                 │
│                                        ▼                                 │
│                      ┌──────────────────────────────────────────┐       │
│                      │        Frontend Next.js (React)           │       │
│                      │              Port 3000                    │       │
│                      │  • Dashboard         • Prédiction         │       │
│                      │  • Liste Étudiants   • Rapports PDF       │       │
│                      │  • Liste Modules     • Alertes Email      │       │
│                      └──────────────────────────────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technologies Utilisées

| Composant | Technologies |
|-----------|-------------|
| **Machine Learning** | Python 3.12, XGBoost, Scikit-learn, K-Means, NearestNeighbors |
| **Backend API** | Flask 3.1.2, Flask-CORS, Pandas, NumPy, Joblib |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Recharts, Lucide Icons |
| **Rapports** | ReportLab (PDF), HTML Templates |
| **Données** | CSV (UTF-8), 157,068 enregistrements nettoyés |

### 2.3 Structure des Fichiers

```
PFA-V2/
├── 📊 Données
│   └── raw/
│       ├── 1- one_clean.csv
│       └── 2- two_clean.csv
│
├── 🤖 Machine Learning
│   ├── projet4_support_recommendation.py   # Pipeline ML principal
│   ├── predict_external.py                  # Prédictions externes
│   ├── test_model.py                        # Tests du modèle
│   └── check_unknown.py                     # Vérification données
│
├── 🔧 Backend
│   └── backend/
│       └── app.py                           # API Flask
│
├── 🎨 Frontend
│   └── frontend-next/
│       ├── src/app/                         # Pages Next.js
│       ├── src/components/                  # Composants React
│       └── src/lib/api.ts                   # Client API
│
├── 📁 Outputs
│   └── output_projet4/
│       ├── model_soutien_pedagogique.joblib # Modèle sauvegardé
│       ├── scoring_complet.csv              # Scores de risque
│       ├── recommandations_modules.csv      # Recommandations
│       ├── alertes/                         # Alertes HTML
│       └── rapports_pdf/                    # Rapports PDF
│
└── 📚 Documentation
    ├── DOCUMENTATION.md                     # Ce fichier
    └── README.md
```

---

## 3. Préparation des Données

### 3.1 Données Sources

Les données proviennent de deux fichiers CSV contenant les résultats académiques :

| Métrique | Valeur |
|----------|--------|
| Enregistrements bruts | ~160,000 |
| Après nettoyage | 157,068 |
| Étudiants uniques | 7,171 |
| Modules uniques | 78 |
| Filières | 7 |

### 3.2 Nettoyage des Données

```python
# Opérations de nettoyage effectuées :
1. Suppression des ID = "Unknown" ou null
2. Suppression des filières = "Unknown"
3. Suppression des modules = "Unknown"
4. Correction des notes > 20/20 (divisées par 5)
5. Conversion en encodage UTF-8
6. Harmonisation des statuts vers le système marocain
```

### 3.3 Mapping des Colonnes

| Colonne Source | Colonne Cible | Description |
|---------------|---------------|-------------|
| `Major` | `Filiere` | Filière d'études (EEA, EEC, EED, etc.) |
| `Subject` | `Module` | Nom du module |
| `MajorYear` | `Annee` | Année d'études (1-5) |
| `Total` | `Note_sur_20` | Note convertie sur 20 |
| `Status` | `Statut_MA` | Statut adapté au système marocain |

### 3.4 Mapping des Statuts

| Statut Original | Statut Marocain |
|----------------|-----------------|
| Pass | Validé |
| Fail | Non_Validé |
| Absent | Absent |
| Debarred | Exclu |
| Withdrawal | Abandon |
| Withhold | En_Attente |
| Exempt | Dispensé |

---

## 4. Modèles de Machine Learning

### 4.1 Vue d'Ensemble des Algorithmes

Le système utilise **3 algorithmes complémentaires** :

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE MACHINE LEARNING                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │    K-Means      │  │    XGBoost      │  │  Collaborative  │  │
│  │   Clustering    │  │   Classifier    │  │   Filtering     │  │
│  │                 │  │                 │  │                 │  │
│  │  5 Profils      │  │  Prédiction     │  │  Recommandation │  │
│  │  d'Apprenants   │  │  Besoin Soutien │  │  par Similarité │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│          │                    │                    │            │
│          └────────────────────┴────────────────────┘            │
│                              │                                   │
│                              ▼                                   │
│                 ┌─────────────────────────┐                     │
│                 │    Score de Risque      │                     │
│                 │    (0-100%)             │                     │
│                 │                         │                     │
│                 │  Recommandations        │                     │
│                 │  Personnalisées         │                     │
│                 └─────────────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Algorithme 1 : K-Means Clustering

**Objectif** : Identifier les profils d'apprenants

**Configuration** :
```python
KMeans(n_clusters=5, random_state=42, n_init=10)
```

**5 Profils Identifiés** :

| Profil | Description | Taux Soutien |
|--------|-------------|--------------|
| 🌟 **Excellence** | Étudiants performants, notes élevées | < 10% |
| ✅ **Régulier** | Résultats stables, peu de difficultés | 10-25% |
| 📈 **En Progression** | Performance variable, potentiel d'amélioration | 25-40% |
| ⚠️ **En Difficulté** | Difficultés fréquentes, besoin d'accompagnement | 40-60% |
| 🚨 **À Risque** | Situation critique, intervention urgente | > 60% |

### 4.3 Algorithme 2 : XGBoost Classifier

**Objectif** : Prédire la probabilité qu'un étudiant ait besoin de soutien

**Configuration** :
```python
XGBClassifier(
    n_estimators=200,      # Nombre d'arbres
    max_depth=6,           # Profondeur maximale
    learning_rate=0.1,     # Taux d'apprentissage
    subsample=0.8,         # Échantillonnage
    colsample_bytree=0.8,  # Features par arbre
    random_state=42
)
```

**Calibration** :
```python
CalibratedClassifierCV(xgb_model, method='sigmoid', cv=5)
```

La calibration permet d'obtenir des probabilités fiables (score de risque en %).

### 4.4 Algorithme 3 : Collaborative Filtering

**Objectif** : Recommander des modules à surveiller basé sur des étudiants similaires

**Configuration** :
```python
NearestNeighbors(n_neighbors=10, metric='cosine')
```

**Fonctionnement** :
1. Construction d'une matrice Étudiant × Module (notes)
2. Calcul de similarité cosinus entre étudiants
3. Identification des K voisins les plus proches
4. Analyse des difficultés communes des étudiants similaires
5. Recommandation des modules à risque

### 4.5 Feature Engineering

**43 Features** créées pour capturer les patterns de risque :

#### Features Étudiant
| Feature | Description |
|---------|-------------|
| `student_avg_total` | Moyenne générale de l'étudiant |
| `student_std_total` | Écart-type des notes (régularité) |
| `student_min_total` | Note minimale obtenue |
| `student_support_rate` | Taux historique d'échecs |
| `taux_absenteisme` | Fréquence des absences |
| `modules_rattrapage` | Nombre de modules non validés |

#### Features Module
| Feature | Description |
|---------|-------------|
| `module_avg_total` | Moyenne du module |
| `module_taux_echec` | Taux d'échec global du module |
| `module_effectif` | Nombre d'étudiants inscrits |
| `difficulte_module` | Niveau de difficulté (Accessible → Très Difficile) |

#### Features Contextuelles
| Feature | Description |
|---------|-------------|
| `peer_group_avg_note20` | Moyenne de la promotion |
| `deviation_from_peer` | Écart par rapport à la promotion |
| `combo_taux_echec` | Risque spécifique Filière-Module |
| `charge_semestre` | Nombre de modules par semestre |
| `distance_seuil` | Distance à la note de validation (10/20) |

#### Features Pôles de Compétences
| Feature | Description |
|---------|-------------|
| `force_Mathematiques` | Performance en maths |
| `force_Physique` | Performance en physique |
| `force_Informatique` | Performance en informatique |
| `force_Electrique` | Performance en électricité |
| `force_Electronique` | Performance en électronique |

---

## 5. API Backend

### 5.1 Configuration

```python
# backend/app.py
Flask API sur http://localhost:5000
CORS activé pour requêtes cross-origin
Timeout: 30 secondes
```

### 5.2 Endpoints Disponibles

#### Statistiques
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/stats` | GET | Statistiques générales du système |
| `/api/filieres` | GET | Liste des filières disponibles |

#### Étudiants
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/etudiants` | GET | Liste paginée des étudiants |
| `/api/etudiant/<code>` | GET | Détails d'un étudiant |
| `/api/etudiants-risque` | GET | Étudiants à haut risque |

#### Modules
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/modules` | GET | Liste paginée des modules |

#### Prédiction
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/predict` | POST | Prédiction pour un étudiant |

#### Rapports PDF
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/rapports/global` | GET | Rapport global PDF |
| `/api/rapports/filiere/<filiere>` | GET | Rapport par filière |
| `/api/rapports/etudiant/<code>` | GET | Rapport individuel |

#### Alertes Email
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/alertes/etudiant` | POST | Alerte pour un étudiant |
| `/api/alertes/module` | POST | Alerte pour un module |
| `/api/alertes/rapport-hebdo` | POST | Rapport hebdomadaire |

### 5.3 Exemple de Réponse API

**GET `/api/stats`**
```json
{
  "nb_etudiants": 7171,
  "nb_modules": 78,
  "nb_filieres": 7,
  "moyenne_generale": 11.86,
  "taux_echec_global": 27.8,
  "profils_count": {
    "Excellence": 1254,
    "Régulier": 2103,
    "En Progression": 1567,
    "En Difficulté": 1389,
    "À Risque": 858
  },
  "filieres_stats": {
    "EEA": {"ID": 1250, "Note_sur_20": 12.3, "Needs_Support": 0.25},
    "EEC": {"ID": 980, "Note_sur_20": 11.8, "Needs_Support": 0.30}
  }
}
```

**POST `/api/predict`**
```json
// Request
{
  "code_etudiant": "12345",
  "filiere": "EEA",
  "modules": [
    {"code": "MATH101", "note": 8.5},
    {"code": "PHYS101", "note": 12.0}
  ]
}

// Response
{
  "etudiant_code": "12345",
  "risque": true,
  "probabilite": 0.75,
  "profil": "En Difficulté",
  "recommandations": [
    "Tutorat intensif en mathématiques",
    "Séances de remédiation recommandées",
    "Suivi personnalisé conseillé"
  ],
  "modules_similaires": ["MATH102", "ELEC101"]
}
```

---

## 6. Interface Frontend

### 6.1 Technologies

- **Framework** : Next.js 14 avec App Router
- **Langage** : TypeScript
- **Styling** : Tailwind CSS
- **Graphiques** : Recharts
- **Icônes** : Lucide React
- **HTTP Client** : Axios

### 6.2 Pages Disponibles

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/` | Vue d'ensemble avec statistiques clés |
| Étudiants | `/etudiants` | Liste et recherche d'étudiants |
| Modules | `/modules` | Liste des modules avec taux d'échec |
| Risque | `/risque` | Étudiants à haut risque (prioritaires) |
| Prédiction | `/prediction` | Outil de prédiction interactive |
| Rapports | `/rapports` | Génération de rapports PDF |
| Alertes | `/alertes` | Envoi d'alertes email |

### 6.3 Composants Principaux

```typescript
// Composants réutilisables
├── Sidebar.tsx        // Navigation latérale
├── StatCard.tsx       // Cartes de statistiques
├── ProfilBadge.tsx    // Badge coloré par profil
├── RiskIndicator.tsx  // Indicateur visuel de risque
└── DataTable.tsx      // Tableau de données paginé
```

### 6.4 Thème Visuel

**Palette de couleurs (mode clair professionnel)** :

| Élément | Couleur |
|---------|---------|
| Fond principal | `#F8FAFC` (Slate 50) |
| Sidebar | `#1E293B` (Slate 800) |
| Accent primaire | `#3B82F6` (Blue 500) |
| Succès | `#10B981` (Emerald 500) |
| Avertissement | `#F59E0B` (Amber 500) |
| Danger | `#EF4444` (Red 500) |

---

## 7. Fonctionnalités Principales

### 7.1 Dashboard Interactif

- **Statistiques en temps réel** : Nombre d'étudiants, modules, taux d'échec
- **Graphiques** : Distribution par profil, performance par filière
- **KPIs** : Indicateurs clés de performance

### 7.2 Gestion des Étudiants

- **Liste paginée** avec recherche et filtres
- **Détail étudiant** : Historique, modules, recommandations
- **Export** des données

### 7.3 Analyse des Modules

- **Classement par difficulté**
- **Taux d'échec** par module
- **Comparaison** entre filières

### 7.4 Système de Prédiction

```
┌─────────────────────────────────────────────────────────────┐
│                  PROCESSUS DE PRÉDICTION                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. ENTRÉE                                                   │
│     ├── Code étudiant (optionnel)                           │
│     ├── Filière                                              │
│     └── Notes par module                                     │
│                                                              │
│  2. FEATURE ENGINEERING                                      │
│     ├── Calcul des features (43 variables)                  │
│     ├── Normalisation (StandardScaler)                      │
│     └── Encodage des catégories                              │
│                                                              │
│  3. PRÉDICTION                                               │
│     ├── XGBoost : Probabilité de risque                     │
│     ├── K-Means : Profil d'apprenant                        │
│     └── Collaborative Filtering : Modules à surveiller      │
│                                                              │
│  4. SORTIE                                                   │
│     ├── Score de risque (0-100%)                            │
│     ├── Profil assigné (5 catégories)                       │
│     └── Recommandations personnalisées                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.5 Rapports PDF

Génération automatique de rapports pour :
- **Administrateurs** : Vue globale de l'établissement
- **Responsables filière** : Performance par filière
- **Étudiants** : Rapport individuel avec recommandations

### 7.6 Alertes Email

- **Alertes étudiants** : Notification personnalisée
- **Alertes modules** : Aux enseignants responsables
- **Rapport hebdomadaire** : Synthèse automatique

---

## 8. Installation et Déploiement

### 8.1 Prérequis

```bash
# Versions requises
Python >= 3.10
Node.js >= 18.0
npm >= 9.0
```

### 8.2 Installation Backend

```bash
# Cloner le projet
cd PFA-V2

# Installer les dépendances Python
pip install flask flask-cors pandas numpy scikit-learn xgboost joblib reportlab

# Lancer le serveur Flask
cd backend
python app.py
# → Serveur sur http://localhost:5000
```

### 8.3 Installation Frontend

```bash
# Installer les dépendances Node.js
cd frontend-next
npm install

# Lancer le serveur de développement
npm run dev
# → Application sur http://localhost:3000
```

### 8.4 Entraînement du Modèle

```bash
# Entraîner/réentraîner le modèle
python projet4_support_recommendation.py

# Outputs générés :
# - output_projet4/model_soutien_pedagogique.joblib
# - output_projet4/scoring_complet.csv
# - output_projet4/*.png (visualisations)
```

---

## 9. Performances du Modèle

### 9.1 Métriques de Classification

| Métrique | Valeur |
|----------|--------|
| **ROC-AUC Score** | 1.0000 |
| **F1-Score** | 0.9995 |
| **Précision** | 99.96% |
| **Recall** | 99.94% |
| **Accuracy** | 99.95% |

### 9.2 Matrice de Confusion

```
                    Prédit
                 Validé  Soutien
Réel   Validé    22,456      8
       Soutien       6    8,944
```

### 9.3 Validation Croisée (5-Fold)

```
ROC-AUC moyen: 0.9998 (+/- 0.0003)
```

### 9.4 Top 10 Facteurs de Risque

| Rang | Facteur | Importance |
|------|---------|------------|
| 1 | Distance au seuil de validation | 0.2341 |
| 2 | Note sur 20 | 0.1892 |
| 3 | Historique échecs étudiant | 0.1245 |
| 4 | Taux d'échec du module | 0.0987 |
| 5 | Écart par rapport à la promotion | 0.0756 |
| 6 | Moyenne générale étudiant | 0.0654 |
| 7 | Taux d'absentéisme | 0.0543 |
| 8 | Risque combinaison filière-module | 0.0432 |
| 9 | Charge du semestre | 0.0321 |
| 10 | Année d'études | 0.0234 |

---

## 10. Guide d'Utilisation

### 10.1 Cas d'Usage : Identifier un Étudiant à Risque

1. Accéder au **Dashboard** (`/`)
2. Consulter la section **"Étudiants à Risque"**
3. Cliquer sur un étudiant pour voir les détails
4. Analyser les recommandations proposées

### 10.2 Cas d'Usage : Prédire pour un Nouvel Étudiant

1. Accéder à **Prédiction** (`/prediction`)
2. Sélectionner la **filière**
3. Entrer les **notes par module**
4. Cliquer sur **"Analyser"**
5. Consulter le score de risque et les recommandations

### 10.3 Cas d'Usage : Générer un Rapport

1. Accéder à **Rapports** (`/rapports`)
2. Choisir le type : Global, Filière, ou Étudiant
3. Sélectionner les paramètres
4. Cliquer sur **"Télécharger PDF"**

### 10.4 Cas d'Usage : Envoyer une Alerte

1. Accéder à **Alertes** (`/alertes`)
2. Choisir le type d'alerte
3. Entrer les informations (email, code étudiant/module)
4. Cliquer sur **"Envoyer"**

---

## 📞 Support et Contact

Pour toute question technique ou demande d'évolution :

- **Email** : [À configurer]
- **Documentation API** : http://localhost:5000/api/docs

---

## 📜 Changelog

| Version | Date | Modifications |
|---------|------|---------------|
| 2.0.0 | Décembre 2024 | Migration Next.js 14, refonte UI |
| 1.5.0 | Décembre 2024 | Ajout rapports PDF et alertes email |
| 1.0.0 | Décembre 2024 | Version initiale avec ML pipeline |

---

*Documentation générée le 22 Décembre 2024*
*Système de Recommandation de Soutien Pédagogique - Version 2.0*
