"""
Test rapide du modèle via l'API
"""
import requests
import json

print("="*60)
print("TEST DU MODELE ML VIA L'API")
print("="*60)

# Test 1: Prédiction simple
print("\n1. Test prédiction pour un étudiant")
print("-"*60)

url = "http://localhost:5000/api/predict"
data = {
    "filiere": "EEA",
    "modules": [
        {"code": "MATH1", "note": 12.5},
        {"code": "PHYS1", "note": 10.0},
        {"code": "INFO1", "note": 14.0}
    ]
}

try:
    response = requests.post(url, json=data, timeout=5)
    if response.status_code == 200:
        result = response.json()
        print(f"OK Prediction reussie!")
        print(f"   Risque: {'OUI' if result.get('risque') else 'NON'}")
        print(f"   Probabilite: {result.get('probabilite')}%")
        print(f"   Profil: {result.get('profil')}")
        print(f"   Note moyenne: {result.get('note_sur_20')}/20")
    else:
        print(f"ERREUR {response.status_code}")
except Exception as e:
    print(f"ERREUR: {e}")

# Test 2: Modules futurs
print("\n2. Test modules futurs pour etudiant 191112")
print("-"*60)

url2 = "http://localhost:5000/api/predict/modules-futurs"
data2 = {"code_etudiant": "191112"}

try:
    response = requests.post(url2, json=data2, timeout=10)
    if response.status_code == 200:
        result = response.json()
        print(f"OK Prediction modules futurs reussie!")
        print(f"   Etudiant: {result.get('etudiant')}")  
        print(f"   Filiere: {result.get('filiere')}")
        print(f"   Annee actuelle: {result.get('annee_actuelle')}")
        print(f"   Modules futurs: {result.get('nb_modules_futurs')}")
        print(f"   Haut risque: {result.get('resume', {}).get('modules_haut_risque', 0)}")
        print(f"   Recommandes: {result.get('resume', {}).get('modules_recommandes', 0)}")
    else:
        print(f"ERREUR {response.status_code}: {response.text}")
except Exception as e:
    print(f"ERREUR: {e}")

print("\n" + "="*60)
print("FIN DES TESTS")
print("="*60)
