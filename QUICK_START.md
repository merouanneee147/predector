# 🚀 Guide de Démarrage Rapide - PFA-V2

## Système de Recommandation de Soutien Pédagogique

---

## 📋 Prérequis

- **Python** ≥ 3.10
- **Node.js** ≥ 18.0
- **npm** ≥ 9.0

---

## ⚡ Installation Rapide

### 1. Installer les Dépendances Python

```bash
# À la racine du projet
pip install -r requirements.txt
```

### 2. Installer les Dépendances Frontend

```bash
cd frontend-next
npm install
```

---

## 🎯 Démarrage

### Option 1: Démarrage Manuel

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```
✅ Backend disponible sur: http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd frontend-next
npm run dev
```
✅ Frontend disponible sur: http://localhost:3000

### Option 2: Démarrage avec Script (Windows)

```bash
# Créer start.bat à la racine du projet:
@echo off
start cmd /k "cd backend && python app.py"
timeout /t 3
start cmd /k "cd frontend-next && npm run dev"
```

Puis exécuter:
```bash
start.bat
```

---

## 🔍 Vérification

### Backend
- Ouvrir http://localhost:5000/api/stats
- Devrait retourner des statistiques JSON

### Frontend  
- Ouvrir http://localhost:3000
- Le dashboard devrait s'afficher

---

## 📊 Structure du Projet

```
PFA-V2/
├── backend/              # API Flask
│   ├── app.py           # Serveur principal
│   └── database.py      # Gestion BDD SQLite
│
├── frontend-next/        # Interface Next.js
│   ├── src/app/         # Pages
│   ├── src/components/  # Composants React
│   └── src/lib/         # API client
│
├── raw/                  # Données CSV sources
│   ├── 1- one_clean.csv
│   └── 2- two_clean.csv
│
├── output_projet4/       # Modèles & Résultats ML
│   ├── model_soutien_pedagogique.joblib
│   ├── scoring_complet.csv
│   └── soutien_pedagogique.db  (SQLite)
│
└── requirements.txt      # Dépendances Python
```

---

## 🎓 Pages Disponibles

| Page | URL | Description |
|------|-----|-------------|
| **Dashboard** | `/` | Vue d'ensemble générale |
| **Étudiants** | `/etudiants` | Liste des étudiants |
| **Modules** | `/modules` | Liste des modules |
| **À Risque** | `/risque` | Étudiants prioritaires |
| **Prédiction** | `/prediction` | Analyse individuelle |
| **Prédiction Avancée** | `/prediction-avancee` | Analyse batch (CSV) |
| **Rapports** | `/rapports` | Génération PDF |
| **Alertes** | `/alertes` | Envoi d'emails |
| **Interventions** | `/interventions` | Suivi des actions |

---

## 🔧 Dépannage Courant

### Erreur: Port 5000 déjà utilisé
```bash
# Trouver le processus
netstat -ano | findstr :5000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

### Erreur: Connexion Backend refusée
- Vérifier que le backend tourne sur port 5000
- Vérifier les logs du terminal backend
- Vérifier `frontend-next/src/lib/api.ts` : `API_BASE_URL`

### Erreur de Build Frontend
```bash
cd frontend-next
npm run build
```
Si erreur, vérifier les messages TypeScript

### Base de Données vide
```bash
# Réentraîner le modèle
python projet4_support_recommendation.py
```

---

## 📦 Production

### Build Frontend
```bash
cd frontend-next
npm run build
npm start  # Port 3000
```

### Variables d'Environnement (Optionnel)

Créer `.env` dans `backend/`:
```
FLASK_ENV=production
JWT_SECRET=your-secret-key-here
EMAIL_ENABLED=false
```

---

## 📞 Support

Pour toute question:
1. Consulter `DOCUMENTATION.md` (documentation complète)
2. Vérifier `TROUBLESHOOTING.md` (guide de dépannage)
3. Examiner les logs dans les terminaux

---

## ✅ Checklist après Installation

- [ ] Backend démarre sans erreur
- [ ] Frontend se compile sans erreur
- [ ] Dashboard affiche des données
- [ ] Navigation entre pages fonctionne
- [ ] API répond (tester `/api/stats`)
- [ ] Base de données existe (`output_projet4/soutien_pedagogique.db`)
- [ ] Modèle ML existe (`output_projet4/model_soutien_pedagogique.joblib`)

---

**🎉 Félicitations ! Votre système est prêt !**
