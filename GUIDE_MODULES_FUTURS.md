# 🔮 Guide de Test - Modules Recommandés

## 🎯 Nouvelle Fonctionnalité Ajoutée !

Système de **prédiction préventive** pour recommander les modules futurs basé sur l'historique de l'étudiant.

---

## 📍 Accéder à la Fonctionnalité

1. **Ouvrez l'application** → http://localhost:3000

2. **Dans le menu de gauche**, cliquez sur :
   ```
   Analyse & Prédiction
    → Modules Recommandés 🆕
   ```

3. **Badge vert "NEW"** pour indiquer la nouvelle fonctionnalité !

---

## 🧪 Codes Étudiants pour Tester

Utilisez ces codes réels du système :

| Code Étudiant | Pourquoi le tester ? |
|---------------|----------------------|
| **191112** | Étudiant avec historique complet |
| **197110** | Bon pour tester différentes filières |
| **191167** | Profil moyen, bonne diversité |
| **191003** | Performance variée |

---

## 📝 Comment Tester ?

### Test 1 : Étudiant Existant

1. **Code Étudiant** : `191112`
2. **Filière** : EEA (ou celle disponible)
3. **Année Actuelle** : 1ère ou 2ème année
4. **Cliquer** sur "Analyser les Modules"

### Résultat Attendu :

✅ **Statistiques** : Moyenne générale, nb modules recommandés/à risque  
✅ **Modules à Haut Risque** (rouge) : Liste des modules difficiles avec actions préventives  
✅ **Modules Recommandés** (vert) : Liste des modules où l'étudiant devrait réussir  
✅ **Tous les Modules** : Vue complète avec % de réussite pour chaque module

---

## 🎨 Ce que Vous Devriez Voir

### Statistiques en Haut

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 12.5/20      │     8        │      3       │      2       │
│ Moyenne      │ Recommandés  │ Risque Modéré│ Haut Risque  │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

### Modules à Haut Risque (Rouge)

```
🔴 Mécanique des Fluides
   Code: MEC201
   Réussite: 25%
   ❌ Reporter si possible ou tutorat intensif
```

### Modules Recommandés (Vert)

```
✅ Mathématiques 3       85% réussite
✅ Électronique 2        78% réussite
✅ Algorithmique        92% réussite
```

### Liste Complète avec Code Couleur

- 🔴 **Rouge** : Très risqué (< 20% réussite)
- 🟠 **Orange** : Risqué (20-40%)
- 🟡 **Jaune** : Modéré (40-60%)
- 🟢 **Vert clair** : Bon (60-80%)
- ✅ **Vert** : Excellent (> 80%)

---

## 🔍 Fonctionnalités du Système

### 1. Prédiction ML

Le système utilise :
- ✅ **Historique de l'étudiant** (notes passées)
- ✅ **Statistiques du module** (difficulté, taux d'échec)
- ✅ **Collaborative Filtering** (étudiants similaires)
- ✅ **Modèle XGBoost** (43 features)

### 2. Catégorisation Intelligente

Chaque module est classé selon :
- **Probabilité de réussite** (0-100%)
- **Besoin de soutien** (OUI/NON)
- **Action préventive** (tutorat, reporter, aucune...)

### 3. Recommandations Personnalisées

**Pour chaque module :**
- ✅ "Aucune action nécessaire"
- 🟢 "Suivi normal"
- 🟡 "Tutorat préventif recommandé"
- 🟠 "Tutorat préventif nécessaire"
- 🔴 "Reporter si possible ou tutorat intensif"

---

## 📊 Cas d'Usage Pratiques

### Scénario 1 : Planning de Semestre

**Question** : "Quels modules inscrire pour le semestre prochain ?"

**Solution** :
1. Analyser les modules futurs
2. Sélectionner les modules avec > 60% de réussite
3. Pour les modules entre 40-60% : tutorat préventif
4. Reporter les modules < 40% si possible

### Scénario 2 : Intervention Préventive

**Question** : "Comment éviter l'échec avant qu'il arrive ?"

**Solution** :
1. Identifier modules à haut risque
2. Proposer tutorat AVANT l'inscription
3. Réviser prérequis faibles
4. Former groupes de soutien préventif

### Scénario 3 : Optimisation du Parcours

**Question** : "Quel ordre pour maximiser les chances de réussite ?"

**Solution** :
1. Commencer par modules recommandés (> 70%)
2. Prendre 1-2 modules modérés avec soutien
3. Reporter modules très risqués
4. Renforcer bases avant modules difficiles

---

## 🚀 API Endpoint

Pour les développeurs, l'endpoint est accessible :

```bash
POST http://localhost:5000/api/predict/modules-futurs

Body:
{
  "code_etudiant": "191112",
  "filiere": "EEA",
  "annee_actuelle": 1
}

Response:
{
  "etudiant": "191112",
  "moyenne_generale": 12.5,
  "nb_modules_futurs": 15,
  "predictions": [...],
  "modules_par_categorie": {
    "haut_risque": [...],
    "risque_modere": [...],
    "recommandes": [...]
  }
}
```

---

## ✅ Checklist de Test

- [ ] Page accessible via menu "Modules Recommandés"
- [ ] Badge "NEW" affiché
- [ ] Formulaire fonctionne (code étudiant, filière, année)
- [ ] Résultats affichés avec statistiques
- [ ] Modules catégorisés (haut risque, modéré, recommandés)
- [ ] Code couleur correct (rouge → vert)
- [ ] Actions préventives affichées
- [ ] Interface responsive (mobile/desktop)

---

## 🎉 Résumé

**Nouvelle Fonctionnalité Complète :**
- ✅ Endpoint API `/api/predict/modules-futurs`
- ✅ Page Frontend "Modules Recommandés"
- ✅ Intégration menu navigation
- ✅ Badge "NEW" pour mise en évidence
- ✅ Prédictions ML avec XGBoost
- ✅ Catégorisation intelligente
- ✅ Recommandations personnalisées

**Le système peut maintenant prédire AVANT que l'étudiant passe le module !**
