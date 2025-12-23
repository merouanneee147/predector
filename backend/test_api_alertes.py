"""
Test direct de l'API Alertes
"""
import requests
import json

print("="*60)
print("TEST API ALERTES")
print("="*60)

# Test 1: Vérifier que l'API répond
print("\n1. Test de connexion à l'API...")
try:
    response = requests.get('http://localhost:5000/api/filieres')
    print(f"✅ API accessible: {response.status_code}")
except Exception as e:
    print(f"❌ API non accessible: {e}")
    exit(1)

# Test 2: Tester la route alertes/etudiant
print("\n2. Test route /api/alertes/etudiant...")
url = 'http://localhost:5000/api/alertes/etudiant'
data = {
    'code': 'ETU001',
    'email': 'perfumeshabibi10@gmail.com'
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("✅ Alerte envoyée avec succès!")
    elif response.status_code == 404:
        print("❌ Route non trouvée (404)")
        print("Vérifiez que Flask a bien chargé toutes les routes")
    else:
        print(f"⚠️ Erreur: {response.status_code}")
        print(response.json())
        
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "="*60)
