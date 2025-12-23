# Diagrammes de Séquence - Système de Soutien Pédagogique

## Vue d'ensemble

Ces diagrammes illustrent les flux d'interaction pour les scénarios clés du système.

---

## 1. Prédiction de Risque pour un Étudiant

```mermaid
sequenceDiagram
    participant E as Enseignant
    participant UI as Interface Web
    participant API as Backend API
    participant ML as MLModel
    participant DB as Base de Données
    
    E->>UI: Sélectionne étudiant (code: 191112)
    UI->>API: POST /api/predict {code_etudiant}
    
    API->>DB: Récupérer historique étudiant
    DB-->>API: Notes, modules, filière
    
    API->>API: Calculer 43 features
    note over API: moyenne, taux échec,<br/>comparaison pairs, etc.
    
    API->>ML: predict(features)
    ML->>ML: StandardScaler.transform()
    ML->>ML: XGBoost.predict_proba()
    ML->>ML: KMeans.predict() (profil)
    ML-->>API: {proba: 0.78, profil: "En Difficulté"}
    
    API->>DB: Sauvegarder prédiction
    DB-->>API: OK
    
    API-->>UI: {risque: true, proba: 78%, recommandations:[...]}
    UI-->>E: Affiche dashboard avec alerte rouge
    
    E->>UI: Demande explication SHAP
    UI->>API: GET /api/predict/explain/{id}
    API->>ML: explainPrediction()
    ML->>ML: SHAP TreeExplainer
    ML-->>API: {features_impact: {...}}
    API-->>UI: Graphique SHAP
    UI-->>E: Visualisation importance features
```

---

## 2. Envoi d'Alerte Email

```mermaid
sequenceDiagram
    participant T as Tuteur
    participant UI as Interface Web
    participant API as Backend API
    participant DB as Base de Données
    participant ML as MLModel
    participant SMTP as Serveur Gmail
    participant Et as Étudiant
    
    T->>UI: Page Alertes
    UI-->>T: Formulaire (code, email)
    
    T->>UI: Envoyer alerte (code: 191112)
    UI->>API: POST /api/alertes/test-email
    
    API->>DB: Chercher étudiant 191112
    DB-->>API: Données étudiant
    
    API->>API: Calculer statistiques
    note over API: moyenne, nb échecs,<br/>modules à risque
    
    API->>API: Déterminer profil
    alt Moyenne >= 14
        API->>API: profil = "Excellence"
    else Moyenne >= 12
        API->>API: profil = "Régulier"
    else Moyenne >= 10
        API->>API: profil = "Passable"
    else Moyenne < 10
        API->>API: profil = "En Difficulté"
    end
    
    API->>API: Générer recommandations personnalisées
    API->>API: Créer template HTML
    
    API->>SMTP: Envoyer email via Gmail
    note over SMTP: perfumeshabibi10@gmail.com<br/>App Password
    SMTP->>SMTP: Authentification TLS
    SMTP->>Et: Email HTML (profil, risques, reco)
    SMTP-->>API: Email envoyé
    
    API-->>UI: {success: true}
    UI-->>T: ✅ Email envoyé avec succès
    
    Et->>Et: Reçoit email
    Et->>Et: Consulte profil et recommandations
```

---

## 3. Recommandation de Modules Futurs

```mermaid
sequenceDiagram
    participant E as Enseignant
    participant UI as Interface Web
    participant API as Backend API
    participant DB as Base de Données
    participant ML as MLModel
    
    E->>UI: Page Modules Futurs
    UI-->>E: Formulaire (code étudiant)
    
    E->>UI: Entrer code 191112
    UI->>API: POST /api/predict/modules-futurs
    
    API->>DB: Récupérer historique complet
    DB-->>API: Tous les modules passés
    
    API->>API: Détection auto filière & année
    note over API: filière = EEA<br/>année_actuelle = 2
    
    API->>DB: Récupérer modules filière EEA
    DB-->>API: Tous modules EEA (années 1-5)
    
    API->>API: Identifier modules non passés
    API->>API: Filtrer années futures (3,4,5)
    
    loop Pour chaque module futur (max 25)
        API->>ML: predict_with_ml_model(étudiant, module)
        ML->>ML: Calculer 43 features spécifiques
        note over ML: performance étudiant +<br/>difficulté module +<br/>stats comparatives
        ML->>ML: XGBoost.predict_proba()
        ML-->>API: {proba_echec: 0.67}
        
        API->>API: Déterminer catégorie
        alt proba_echec > 60%
            API->>API: categorie = "TRÈS RISQUÉ"
        else proba_echec > 40%
            API->>API: categorie = "RISQUÉ"
        else proba_echec > 25%
            API->>API: categorie = "MODÉRÉ"
        else
            API->>API: categorie = "BON/EXCELLENT"
        end
    end
    
    API->>API: Trier par probabilité réussite
    API->>API: Grouper par catégorie
    
    API-->>UI: {predictions: [...], resume: {...}}
    UI-->>E: Affiche tableau modules
    
    E->>UI: Consulte détails module "Mécanique Fluides"
    UI-->>E: 32% réussite, recommandation: tutorat préventif
```

---

## 4. Génération de Rapport PDF

```mermaid
sequenceDiagram
    participant A as Administrateur
    participant UI as Interface Web
    participant API as Backend API
    participant DB as Base de Données
    participant PDF as Générateur PDF
    participant Storage as Stockage Fichiers
    
    A->>UI: Page Rapports
    UI-->>A: Options (filière, période, type)
    
    A->>UI: Demande rapport "Étudiants à Risque - EEA"
    UI->>API: POST /api/rapports/generer
    
    API->>DB: Query étudiants à risque(filière=EEA)
    DB-->>API: List étudiants + prédictions
    
    API->>API: Calculer statistiques globales
    note over API: nb_risque, taux, moyennes,<br/>évolution temporelle
    
    API->>PDF: Créer document PDF
    PDF->>PDF: Ajouter header/logo
    PDF->>PDF: Générer graphiques (matplotlib)
    note over PDF: Distribution risques,<br/>évolution, top modules
    
    loop Pour chaque étudiant à risque
        PDF->>PDF: Ajouter section
        note over PDF: Code, nom, moyenne,<br/>modules échoués, reco
    end
    
    PDF->>PDF: Ajouter footer et pagination
    PDF-->>API: rapport.pdf (bytes)
    
    API->>Storage: Sauvegarder temporairement
    Storage-->>API: file_path
    
    API-->>UI: {download_url: "/download/rapport_xxx.pdf"}
    UI-->>A: Téléchargement automatique
    
    A->>A: Consulte rapport PDF
```

---

## 5. Utilisation de l'Assistant IA

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant UI as Interface Web
    participant API as Backend API
    participant AI as AssistantIA (Simulé)
    participant DB as Base de Données
    
    U->>UI: Ouvre page /assistant
    UI->>API: GET /api/chat/welcome
    API->>AI: getWelcomeMessage()
    AI-->>API: Message bienvenue
    API-->>UI: {message: "Bonjour! Comment..."}
    UI-->>U: Affiche chat avec message bienvenue
    
    U->>UI: Tape "Quels étudiants sont à risque ?"
    UI->>API: POST /api/chat/message
    note over API: {message: "Quels...",<br/>history: []}
    
    API->>AI: chat(message, history)
    AI->>AI: Pattern matching
    note over AI: Détecte: "étudiant" + "risque"
    
    AI->>DB: Compte étudiants avec Needs_Support=1
    DB-->>AI: 1,234 étudiants à risque
    
    AI->>AI: Générer réponse intelligente
    note over AI: Template + vraies données
    
    AI-->>API: {response: "J'ai identifié 1,234...", tokens: 45}
    API-->>UI: Réponse + metadata
    UI-->>U: Affiche réponse formatée
    
    U->>UI: "Analyse l'étudiant 191112"
    UI->>API: POST /api/chat/message {history: [...]}
    API->>AI: chat(message, history)
    AI->>AI: Extrait code: 191112
    AI->>DB: Chercher étudiant 191112
    DB-->>AI: moyenne=11.2, filière=EEA, 27 modules
    AI->>AI: Analyser performance
    AI-->>API: Réponse détaillée personnalisée
    API-->>UI: Affichage
    UI-->>U: Profil complet de l'étudiant
```

---

## Notes d'Implémentation

### Patterns Utilisés

1. **Pattern Request-Response** : Toutes les interactions UI ↔ API
2. **Pattern MVC** : Séparation UI, API (Controller), DB (Model)
3. **Pattern Singleton** : MLModel (une instance)
4. **Pattern Strategy** : Différents générateurs (PDF, Excel)

### Technologies

- **Frontend → Backend** : Axios HTTP requests
- **Backend → Database** : SQLite avec ORM custom
- **Backend → ML** : joblib model loading
- **Backend → Email** : smtplib via Gmail
- **Backend → AI** : Pattern matching simulé

### Points Clés

- **Asynchrone** : Génération PDF en background
- **Cache** : Prédictions stockées pour éviter recalcul
- **Optimisation** : Features pré-calculées quand possible
- **Sécurité** : Authentification JWT sur toutes les routes sensibles

---

**Note:** Ces diagrammes Mermaid peuvent être visualisés sur https://mermaid.live ou intégrés dans un rapport Markdown.
