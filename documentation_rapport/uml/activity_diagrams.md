# Diagrammes d'Activité - Flux de Travail

## Vue d'ensemble

Ces diagrammes illustrent les processus métier et les flux de travail du système.

---

## 1. Processus Complet de Soutien Pédagogique

```mermaid
flowchart TD
    Start([Début du Semestre])
    
    Start --> CollectData[Collecter Données<br/>Étudiants]
    CollectData --> ImportCSV[Importer CSV<br/>dans Système]
    
    ImportCSV --> RunPredictions{Pour chaque<br/>Étudiant}
    RunPredictions --> CalcFeatures[Calculer 43 Features]
    
    CalcFeatures --> MLPredict[Prédiction ML<br/>XGBoost]
    MLPredict --> GetProba[Obtenir Probabilité<br/>de Risque]
    
    GetProba --> CheckRisk{Risque > 50%?}
    
    CheckRisk -->|Non| LowRisk[Profil: Performant<br/>Pas d'action]
    CheckRisk -->|Oui| HighRisk[Profil: À Risque]
    
    HighRisk --> SendAlert[Envoyer Alerte Email<br/>à l'Étudiant]
    SendAlert --> NotifyTuteur[Notifier Tuteur<br/>Assigné]
    
    NotifyTuteur --> ScheduleIntervention[Planifier<br/>Intervention]
    
    ScheduleIntervention --> Intervention{Type<br/>Intervention}
    Intervention -->|Tutorat| Tutoring[Session Tutorat<br/>Individuel]
    Intervention -->|Groupe| GroupSession[Session de<br/>Groupe]
    Intervention -->|Ressources| Resources[Fournir<br/>Ressources]
    
    Tutoring --> RecordAction[Enregistrer<br/>Intervention]
    GroupSession --> RecordAction
    Resources --> RecordAction
    
    LowRisk --> MonitorProgress[Monitoring<br/>Passif]
    RecordAction --> MonitorProgress
    
    MonitorProgress --> WaitPeriod[Attendre Période<br/>2-4 semaines]
    
    WaitPeriod --> ReEvaluate{Ré-évaluation<br/>Nécessaire?}
    ReEvaluate -->|Oui| RunPredictions
    ReEvaluate -->|Non| EndSemester{Fin de<br/>Semestre?}
    
    EndSemester -->|Non| WaitPeriod
    EndSemester -->|Oui| GenerateReport[Générer Rapport<br/>Final]
    
    GenerateReport --> End([Fin])
    
    style Start fill:#10B981
    style End fill:#EF4444
    style HighRisk fill:#FEE2E2,stroke:#DC2626
    style LowRisk fill:#D1FAE5,stroke:#059669
    style MLPredict fill:#DBEAFE,stroke:#2563EB
```

---

## 2. Flux de Prédiction ML Détaillé

```mermaid
flowchart LR
    Start([Requête<br/>Prédiction])
    
    Start --> GetStudent[Récupérer<br/>Historique Étudiant]
    GetStudent --> CheckData{Données<br/>Suffisantes?}
    
    CheckData -->|Non| Error[Erreur: Données<br/>Insuffisantes]
    CheckData -->|Oui| ExtractFeatures
    
    subgraph "Feature Engineering"
        ExtractFeatures[Extraire Features<br/>Numériques]
        ExtractFeatures --> CalcPerf[Calculer Performance<br/>Étudiant]
        CalcPerf --> CalcModule[Statistiques<br/>Module]
        CalcModule --> Compare[Comparaison<br/>avec Pairs]
        Compare --> BuildVector[Construire Vecteur<br/>43 Features]
    end
    
    BuildVector --> Normalize[Normalisation<br/>StandardScaler]
    
    subgraph "ML Prediction"
        Normalize --> XGB[XGBoost<br/>Predict]
        XGB --> Calibrate[Calibration<br/>Probabilités]
        Calibrate --> Cluster[K-Means<br/>Profil]
    end
    
    Cluster --> FormatResult[Formater<br/>Résultat]
    FormatResult --> SaveDB[(Sauvegarder<br/>en BD)]
    
    SaveDB --> Return([Retourner<br/>Prédiction])
    Error --> Return
    
    style ExtractFeatures fill:#FEF3C7
    style CalcPerf fill:#FEF3C7
    style CalcModule fill:#FEF3C7
    style Compare fill:#FEF3C7
    style BuildVector fill:#FEF3C7
    style XGB fill:#DBEAFE
    style Calibrate fill:#DBEAFE
    style Cluster fill:#DBEAFE
```

---

## 3. Processus d'Envoi d'Alerte Email

```mermaid
flowchart TD
    Start([Enseignant/Tuteur<br/>Demande Alerte])
    
    Start --> EnterCode[Entrer Code<br/>Étudiant]
    EnterCode --> Validate{Code<br/>Valide?}
    
    Validate -->|Non| ErrorMsg[Afficher Erreur<br/>Code Invalide]
    Validate -->|Oui| FetchData[Récupérer Données<br/>Étudiant]
    
    FetchData --> CalcStats[Calculer Statistiques<br/>Moyenne, Échecs, etc.]
    
    CalcStats --> DetermineProfile{Moyenne}
    DetermineProfile -->|">= 14"| ProfileExcel[Profil:<br/>Excellence]
    DetermineProfile -->|">= 12"| ProfileRegular[Profil:<br/>Régulier]
    DetermineProfile -->|">= 10"| ProfilePass[Profil:<br/>Passable]
    DetermineProfile -->|"< 10"| ProfileRisk[Profil:<br/>En Difficulté]
    
    ProfileExcel --> GenReco[Générer<br/>Recommandations]
    ProfileRegular --> GenReco
    ProfilePass --> GenReco
    ProfileRisk --> GenReco
    
    GenReco --> BuildHTML[Construire Email<br/>HTML Personnalisé]
    
    BuildHTML --> EmailContent
    subgraph EmailContent["Contenu Email"]
        Header[Header: Profil]
        Stats[Statistiques]
        ModRisk[Modules à Risque]
        Reco[Recommandations]
        CTA[Call-to-Action]
    end
    
    EmailContent --> ConnectSMTP[Connexion<br/>Gmail SMTP]
    
    ConnectSMTP --> Auth{Authentification<br/>Réussie?}
    Auth -->|Non| AuthError[Erreur Auth<br/>Vérifier Password]
    Auth -->|Oui| SendEmail[Envoyer Email<br/>via TLS]
    
    SendEmail --> CheckSent{Email<br/>Envoyé?}
    CheckSent -->|Non| SendError[Erreur Envoi<br/>Réessayer]
    CheckSent -->|Oui| LogDB[(Logger dans BD)]
    
    LogDB --> NotifyUser[Notifier Utilisateur<br/>Succès]
    NotifyUser --> End([Fin])
    
    ErrorMsg --> End
    AuthError --> End
    SendError --> End
    
    style ProfileRisk fill:#FEE2E2,stroke:#DC2626
    style ProfileExcel fill:#D1FAE5,stroke:#059669
    style SendEmail fill:#DBEAFE,stroke:#2563EB
```

---

## 4. Utilisation de l'Assistant IA

```mermaid
flowchart TD
    Start([Utilisateur Ouvre<br/>Chat])
    
    Start --> LoadWelcome[Charger Message<br/>de Bienvenue]
    LoadWelcome --> DisplayChat[Afficher<br/>Interface Chat]
    
    DisplayChat --> WaitInput[Attendre<br/>Message Utilisateur]
    
    WaitInput --> UserInput[Utilisateur<br/>Tape Message]
    UserInput --> SendToAPI[Envoyer à<br/>API Backend]
    
    SendToAPI --> AIProcess[Assistant IA<br/>Traitement]
    
    AIProcess --> PatternMatch{Pattern<br/>Matching}
    
    PatternMatch -->|Mot-clé: Risque| QueryDB1[Query BD:<br/>Étudiants Risque]
    PatternMatch -->|Mot-clé: Module| QueryDB2[Query BD:<br/>Stats Modules]
    PatternMatch -->|Code Étudiant| QueryDB3[Query BD:<br/>Données Étudiant]
    PatternMatch -->|Général| GenericResp[Réponse<br/>Générique]
    
    QueryDB1 --> FormatResp[Formater<br/>Réponse]
    QueryDB2 --> FormatResp
    QueryDB3 --> FormatResp
    GenericResp --> FormatResp
    
    FormatResp --> AddContext[Ajouter Contexte<br/>Vraies Données]
    AddContext --> ReturnAPI[Retourner<br/>à Frontend]
    
    ReturnAPI --> DisplayMsg[Afficher Message<br/>Assistant]
    DisplayMsg --> UpdateHistory[Mettre à jour<br/>Historique]
    
    UpdateHistory --> ContinueChat{Continuer<br/>Conversation?}
    ContinueChat -->|Oui| WaitInput
    ContinueChat -->|Non| End([Fin Session])
    
    style PatternMatch fill:#E9D5FF,stroke:#7C3AED
    style QueryDB1 fill:#FEF3C7,stroke:#D97706
    style QueryDB2 fill:#FEF3C7,stroke:#D97706
    style QueryDB3 fill:#FEF3C7,stroke:#D97706
```

---

## Notation

### Symboles Utilisés

- **Rectangle** : Action/Processus
- **Losange** : Décision/Condition
- **Cylindre** : Base de données
- **Cercle début/fin** : Début/Fin du processus
- **Sous-graphe** : Groupe de processus liés

### Code Couleur

- 🟢 Vert : Succès, Début
- 🔴 Rouge : Erreur, Fin
- 🔵 Bleu : Calcul ML
- 🟡 Jaune : Feature Engineering
- 🟣 Violet : Intelligence

---

**Note:** Ces diagrammes peuvent être visualisés sur https://mermaid.live
