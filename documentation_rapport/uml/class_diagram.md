# Diagramme de Classes - Système de Soutien Pédagogique

## Vue d'ensemble

Ce diagramme représente l'architecture orientée objet du système avec les classes principales et leurs relations.

## Diagramme

```mermaid
classDiagram
    %% Classes Utilisateurs
    class User {
        <<abstract>>
        +int id
        +string username
        +string password_hash
        +string email
        +string role
        +string nom
        +string prenom
        +datetime created_at
        +login()
        +logout()
        +updateProfile()
    }
    
    class Admin {
        +manageUsers()
        +manageSystem()
        +generateGlobalReports()
        +exportAllData()
    }
    
    class Enseignant {
        +string departement
        +consultPredictions()
        +sendAlerts()
        +recordIntervention()
        +generateReports()
    }
    
    class Tuteur {
        +list~Etudiant~ assignedStudents
        +trackProgress()
        +conductSession()
        +viewHistory()
    }
    
    %% Classes Métier
    class Etudiant {
        +string code_etudiant
        +string filiere
        +int annee_actuelle
        +float moyenne_generale
        +int nb_modules_passes
        +list~Module~ modules
        +getPrediction()
        +getRecommendations()
        +viewHistory()
    }
    
    class Module {
        +string code_module
        +string nom
        +string filiere
        +int annee
        +int credits
        +float difficulte
        +float taux_echec
        +getStatistiques()
    }
    
    class Note {
        +int id
        +Etudiant etudiant
        +Module module
        +float note_sur_20
        +string Status statut
        +datetime date
        +bool needs_support
    }
    
    %% Classes ML
    class MLModel {
        <<singleton>>
        +XGBoostModel xgboost
        +StandardScaler scaler
        +KMeans kmeans
        +list~string~ feature_columns
        +loadModel()
        +predict(etudiant)
        +explainPrediction(etudiant)
    }
    
    class Prediction {
        +int id
        +Etudiant etudiant
        +float probabilite_risque
        +string profil
        +datetime date_prediction
        +list~string~ recommandations
        +dict features_importantes
        +generateExplanation()
    }
    
    class ModuleFutur {
        +Module module
        +float proba_reussite
       +float proba_echec
        +bool besoin_soutien
        +string categorie
        +string action_preventive
    }
    
    %% Classes Communication
    class EmailAlert {
        +int id
        +Etudiant destinataire
        +string sujet
        +string contenu_html
        +datetime date_envoi
        +bool envoye
        +send()
        +generateContent()
    }
    
    %% Classes Intervention
    class Intervention {
        +int id
        +Etudiant etudiant
        +User responsable
        +string type_intervention
        +string description
        +datetime date
        +string statut
        +record()
        +update()
    }
    
    %% Classes Rapports
    class Rapport {
        <<abstract>>
        +int id
        +User generateur
        +datetime date_generation
        +string format
        +generate()
        +export()
    }
    
    class RapportPDF {
        +generatePDF()
    }
    
    class ExportExcel {
        +generateExcel()
    }
    
    %% Relations d'héritage
    User <|-- Admin
    User <|-- Enseignant
    User <|-- Tuteur
    Rapport <|-- RapportPDF
    Rapport <|-- ExportExcel
    
    %% Relations associations
    Etudiant "1" --> "*" Note : a
    Module "1" --> "*" Note : évalué par
    Etudiant "1" --> "*" Prediction : reçoit
    MLModel "1" --> "*" Prediction : génère
    Etudiant "1" --> "*" ModuleFutur : recommandations
    Module "1" --> "*" ModuleFutur : concerne
    
    Enseignant "*" --> "*" Etudiant : supervise
    Tuteur "1" --> "*" Etudiant : accompagne
    Etudiant "1" --> "*" Intervention : bénéficie
    User "1" --> "*" Intervention : effectue
    
    Etudiant "1" --> "*" EmailAlert : destinataire
    User "1" --> "*" EmailAlert : expéditeur
    Prediction "1" --> "1" EmailAlert : déclenche
    
    User "1" --> "*" Rapport : génère
    
    %% Relations compositions
    Prediction *-- "*" ModuleFutur : contient
    EmailAlert *-- "1" Prediction : inclut
```

## Description des Classes Principales

### 👤 User (Classe Abstraite)
**Responsabilité:** Gestion de l'authentification et profil utilisateur de base  
**Attributs clés:**
- `role` : admin, enseignant, tuteur
- `password_hash` : Stockage sécurisé du mot de passe

**Sous-classes:** Admin, Enseignant, Tuteur

### 👨‍🎓 Etudiant
**Responsabilité:** Représente un étudiant avec son parcours académique  
**Attributs clés:**
- `code_etudiant` : Identifiant unique
- `moyenne_generale` : Performance globale
- `modules` : Liste des modules suivis

**Méthodes:** `getPrediction()`, `getRecommendations()`

### 📚 Module
**Responsabilité:** Représente un cours/module académique  
**Attributs clés:**
- `difficulte` : Niveau de difficulté calculé
- `taux_echec` : Statistique historique

**Méthodes:** `getStatistiques()` - Calcule taux de réussite, moyenne, etc.

### 🤖 MLModel (Singleton)
**Responsabilité:** Gestion du modèle de Machine Learning  
**Pattern:** Singleton (une seule instance)  
**Attributs clés:**
- `xgboost` : Modèle XGBoost entraîné
- `scaler` : StandardScaler pour normalisation
- `feature_columns` : 43 features utilisées

**Méthodes:**
- `predict()` : Génère une prédiction
- `explainPrediction()` : Utilise SHAP/LIME

### 🔮 Prediction
**Responsabilité:** Stocke le résultat d'une prédiction ML  
**Attributs clés:**
- `probabilite_risque` : Score 0-100%
- `profil` : Excellence, Régulier, En Difficulté
- `features_importantes` : Dict des features SHAP

**Méthodes:** `generateExplanation()` - Génère texte explicatif

### 📧 EmailAlert
**Responsabilité:** Gestion des alertes email  
**Attributs clés:**
- `contenu_html` : Template HTML personnalisé
- `envoye` : Status d'envoi

**Méthodes:**
- `send()` : Envoi via SMTP Gmail
- `generateContent()` : Crée HTML à partir de Prediction

### 🎯 Intervention
**Responsabilité:** Traçabilité des actions pédagogiques  
**Attributs clés:**
- `type_intervention` : Tutorat, Conseil, Alerte
- `statut` : En cours, Terminé

## Relations

### Héritage
- `Admin`, `Enseignant`, `Tuteur` héritent de `User`
- `RapportPDF`, `ExportExcel` héritent de `Rapport`

### Association
- Un `Etudiant` a plusieurs `Note`
- Un `Etudiant` reçoit plusieurs `Prediction`
- Un `MLModel` génère plusieurs `Prediction`

### Composition (strong ownership)
- Une `Prediction` contient plusieurs `ModuleFutur`
- Un `EmailAlert` inclut une `Prediction`

### Agrégation
- Un `Tuteur` accompagne plusieurs `Etudiant`

## Patterns de Conception

1. **Singleton** : `MLModel` - Une seule instance du modèle
2. **Factory** : `Rapport` - Création de différents types de rapports
3. **Strategy** : Différentes stratégies d'export (PDF, Excel)

---

**Note:** Ce diagramme peut être visualisé avec Mermaid Live Editor (https://mermaid.live)
