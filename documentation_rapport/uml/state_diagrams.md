# Diagramme d'États - Cycle de Vie

## Vue d'ensemble

Ce diagramme représente les états et transitions d'une prédiction dans le système.

## Diagramme d'États: Prédiction

```mermaid
stateDiagram-v2
    [*] --> Initiée : Requête Prédiction
    
    Initiée --> EnCours : Données Récupérées
    
    state EnCours {
        [*] --> CalculFeatures
        CalculFeatures --> Normalisation
        Normalisation --> PrédictionML
        PrédictionML --> [*]
    }
    
    EnCours --> Calculée : Résultat Obtenu
    
    state IfRisque <<choice>>
    Calculée --> IfRisque
    
    IfRisque --> FaibleRisque : Probabilité < 50%
    IfRisque --> RisqueModéré : 50% ≤ P < 75%
    IfRisque --> HautRisque : Probabilité ≥ 75%
    
    FaibleRisque --> Sauvegardée : Enregistrement BD
    RisqueModéré --> Sauvegardée
    HautRisque --> AlerteEnvoyée : Email Automatique
    
    AlerteEnvoyée --> Sauvegardée
    
    Sauvegardée --> Active : Prédiction Active
    
    Active --> Périmée : Après 30 jours
    Active --> Révisée : Nouvelles Données
    
    Révisée --> EnCours : Recalcul
    
    Périmée --> Archivée
    Archivée --> [*]
    
    note right of EnCours
        Calcul des 43 features
        + Normalisation
        + XGBoost Prediction
    end note
    
    note right of AlerteEnvoyée
        Email automatique
        si risque élevé
    end note
```

---

## Diagramme d'États: Intervention Pédagogique

```mermaid
stateDiagram-v2
    [*] --> Planifiée : Création Intervention
    
    Planifiée --> Confirmée : Tuteur Accepte
    Planifiée --> Annulée : Étudiant/Tuteur Annule
    
    Confirmée --> EnCours : Date Atteinte
    
    state EnCours {
        [*] --> SessionDémarrée
        SessionDémarrée --> DiscussionEnCours
        DiscussionEnCours --> NotesEnregistrées
        NotesEnregistrées --> [*]
    }
    
    EnCours --> Terminée : Session Complétée
    
    state évaluation <<choice>>
    Terminée --> évaluation
    
    évaluation --> Réussie : Progrès Constatés
    évaluation --> SuiviNécessaire : Besoin Continuer
    
    SuiviNécessaire --> Planifiée : Nouvelle Session
    
    Réussie --> Archivée
    Annulée --> Archivée
    Archivée --> [*]
    
    note right of EnCours
        Session de tutorat
        ou intervention
    end note
```

---

## Diagramme d'États: Utilisateur (Session)

```mermaid
stateDiagram-v2
    [*] --> Anonyme
    
    Anonyme --> Authentification : Clic "Se Connecter"
    
    state Authentification {
        [*] --> SaisieCredentials
        SaisieCredentials --> Validation
        Validation --> [*]
    }
    
    state IfAuthenticated <<choice>>
    Authentification --> IfAuthenticated
    
    IfAuthenticated --> Authentifié : Credentials Valides
    IfAuthenticated --> Anonyme : Échec Auth
    
    state Authentifié {
        [*] --> Dashboard
        Dashboard --> ConsultePrédictions
        Dashboard --> EnvoieAlertes
        Dashboard --> GénèreRapports
        Dashboard --> UtiliseAssistant
        
        ConsultePrédictions --> Dashboard
        EnvoieAlertes --> Dashboard
        GénèreRapports --> Dashboard
        UtiliseAssistant --> Dashboard
    }
    
    Authentifié --> SessionExpirée : Timeout (30 min)
    Authentifié --> Déconnecté : Clic "Déconnexion"
    
    SessionExpirée --> Anonyme
    Déconnecté --> Anonyme
    
    Anonyme --> [*] : Ferme Navigateur
```

---

## Diagramme d'États: Email Alert

```mermaid
stateDiagram-v2
    [*] --> Créé : Demande Envoi
    
    Créé --> EnAttente : Ajouté à Queue
    
    EnAttente --> Traitement : Worker Disponible
    
    state Traitement {
        [*] --> GénérationHTML
        GénérationHTML --> ConnexionSMTP
        ConnexionSMTP --> Envoi
        Envoi --> [*]
    }
    
    state IfEnvoyé <<choice>>
    Traitement --> IfEnvoyé
    
    IfEnvoyé --> Envoyé : Succès
    IfEnvoyé --> Échec : Erreur SMTP
    
    Échec --> ReEssai : Tentative < 3
    Échec --> ÉchecDéfinitif : Tentatives Épuisées
    
    ReEssai --> EnAttente
    
    Envoyé --> Livré : Confirmé par Serveur
    Envoyé --> NonOuvert : Non Lu (24h)
    
    Livré --> Lu : Étudiant Ouvre
    Livré --> NonOuvert : Pas Ouvert (48h)
    
    Lu --> Archivé
    NonOuvert --> Relance : Reminder Auto
    ÉchecDéfinitif --> Archivé
    
    Relance --> EnAttente
    
    Archivé --> [*]
    
    note right of Traitement
        Génération contenu
        personnalisé + envoi SMTP
    end note
```

---

## Légende

### États

| Type | Description |
|------|-------------|
| **État Simple** | Rectangle simple |
| **État Composite** | Rectangle avec sous-états |
| **État de Choix** | Losange (condition) |
| **État Initial** | Cercle plein noir |
| **État Final** | Cercle avec contour |

### Transitions

| Notation | Signification |
|----------|---------------|
| → | Transition |
| Label | Événement déclencheur |
| [Condition] | Condition de transition |

---

## Description des États Clés

### Prédiction
- **Initiée** : Requête reçue
- **EnCours** : Calculs ML en cours
- **Calculée** : Score obtenu
- **Active** : Valide et utilisable
- **Périmée** : Plus à jour
- **Archivée** : Historique

### Intervention
- **Planifiée** : Créée mais pas confirmée
- **Confirmée** : Tuteur a accepté
- **EnCours** : Session en direct
- **Terminée** : Session complétée
- **Réussie** : Progrès observés

### Session Utilisateur
- **Anonyme** : Non connecté
- **Authentifié** : Connecté et actif
- **SessionExpirée** : Timeout atteint
- **Déconnecté** : Logout volontaire

---

## Transitions Automatiques

Certaines transitions se déclenchent automatiquement :

1. **Prédiction** : Active → Périmée (après 30 jours)
2. **Session** : Authentifié → SessionExpirée (après 30 min d'inactivité)
3. **Email** : Envoyé → NonOuvert (après 24h sans lecture)
4. **Intervention** : Confirmée → EnCours (à la date/heure prévue)

---

## Événements Métier

| Événement | Impact |
|-----------|---------|
| Nouvelles notes entrées | Prédiction Active → Révisée |
| Email bounce | Envoyé → Échec |
| Étudiant se connecte | Permet de tracker "Lu" |
| Fin de semestre | Interventions → Archivées |

---

**Note:** Ces diagrammes peuvent être visualisés sur https://mermaid.live
