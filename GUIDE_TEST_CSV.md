# 📊 Guide d'Utilisation des Fichiers CSV de Test

## Fichiers Créés

### 1. `test_etudiants.csv` (Simple)
- **15 étudiants** fictifs
- **5 matières** : Math, Physique, Info, Électronique, Anglais
- **3 filières** : EEA, EEC, EED
- Profils variés : Excellence, À Risque, Moyenne

### 2. `test_etudiants_complet.csv` (Complet)
- **20 étudiants** fictifs
- **7 matières** : Math, Physique, Info, Électronique, Électricité, Anglais, Français
- **3 filières** : EEA, EEC, EED
- Plus de diversité dans les profils

---

## 🎯 Comment Tester

### Méthode 1: Via l'Interface Web

1. **Ouvrir l'application**
   - Allez sur http://localhost:3000

2. **Accéder à la Prédiction Avancée**
   - Cliquez sur "Prédiction Avancée" dans le menu

3. **Charger le fichier CSV**
   - Sélectionnez une filière (EEA, EEC, ou EED)
   - Cliquez sur la zone d'upload
   - Choisissez `test_etudiants.csv` ou `test_etudiants_complet.csv`
   - Cliquez sur "Analyser le Fichier"

4. **Voir les résultats**
   - Statistiques globales (total étudiants, à risque, stables)
   - Liste détaillée avec profils et recommandations
   - Export possible en CSV

---

### Méthode 2: Via l'API (Test Direct)

Pour tester l'API directement:

```powershell
# Test simple - 1 étudiant
$body = @{
    filiere = "EEA"
    modules = @(
        @{ code = "MATH101"; note = 8.5 },
        @{ code = "PHYS101"; note = 9.0 },
        @{ code = "INFO101"; note = 12.0 }
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/predict" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

---

## 📋 Profils Attendus dans les Fichiers

### test_etudiants.csv

| Code | Nom | Moyenne | Profil Attendu |
|------|-----|---------|----------------|
| ETU001 | Ahmed Benali | 9.6 | En Difficulté ⚠️ |
| ETU002 | Fatima Zahra | 14.8 | Excellence ⭐ |
| ETU004 | Zineb Idrissi | 6.7 | À Risque 🔴 |
| ETU007 | Karim El Fassi | 15.9 | Excellence ⭐ |
| ETU011 | Rachid Bouali | 6.4 | À Risque 🔴 |
| ETU014 | Laila Berrada | 16.4 | Excellence ⭐ |

### test_etudiants_complet.csv

| Code | Nom | Moyenne | Profil Attendu |
|------|-----|---------|----------------|
| STU2024001 | Ali Benkirane | 16.7 | Excellence ⭐ |
| STU2024002 | Meryem Tazi | 6.1 | À Risque 🔴 |
| STU2024008 | Imane Filali | 4.9 | À Risque 🔴 |
| STU2024012 | Salma Bouazza | 4.8 | À Risque 🔴 |
| STU2024015 | Walid Naciri | 17.1 | Excellence ⭐ |

---

## 🎨 Ce que Vous Devriez Voir

### Sur la Page de Prédiction Avancée

**Statistiques Générales:**
```
Total Étudiants: 15 (ou 20)
À Risque: 3-5 étudiants
Stables: 10-17 étudiants
Taux de Risque: 20-30%
```

**Pour Chaque Étudiant:**
- ✅ Badge de profil (couleur selon le risque)
- 📊 Barre de progression du score de risque
- 💡 Recommandations personnalisées
- 📈 Niveau de priorité

**Exemples de Recommandations:**

- **À Risque (< 7/20):**
  - 🚨 Tutorat individuel URGENT
  - 📞 Convocation conseiller pédagogique
  - 📚 Séances de rattrapage obligatoires

- **En Difficulté (7-10/20):**
  - 📝 Inscription TD de soutien
  - 📅 Suivi hebdomadaire recommandé
  - 📖 Révision des fondamentaux

- **Excellence (> 14/20):**
  - 🌟 Excellent travail !
  - 📈 Ressources avancées disponibles
  - 👨‍🏫 Possibilité de tutorat pair

---

## 💡 Conseils de Test

1. **Testez d'abord le fichier simple** (`test_etudiants.csv`)
2. **Vérifiez que tous les profils sont détectés**
3. **Exportez les résultats** pour voir le format CSV généré
4. **Testez ensuite le fichier complet** avec plus de données

---

## 🔍 Validation

Le système devrait automatiquement:
- ✅ Calculer la moyenne de chaque étudiant
- ✅ Assigner un profil (Excellence, Régulier, En Progression, En Difficulté, À Risque)
- ✅ Générer des recommandations appropriées
- ✅ Calculer un score de risque (probabilité)
- ✅ Permettre l'export en CSV

---

## 📊 Format CSV Attendu

Le système est flexible et accepte différents formats:

**Colonnes Minimales:**
```csv
code_etudiant,nom,filiere,[matiere1]_note,[matiere2]_note,...
```

**Exemple:**
```csv
ETU001,Ahmed,EEA,12.5,9.0,14.5
```

Les noms de colonnes peuvent varier (math, mathematiques, Math, etc.)

---

**🎉 Vous êtes prêt à tester ! Les fichiers sont dans le dossier principal du projet.**
