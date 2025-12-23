"""
Test de la nouvelle route /api/alertes/test-email
"""
import requests

print("="*60)
print("TEST NOUVELLE ROUTE EMAIL")
print("="*60)

# Test 1: GET pour vérifier que la route existe
print("\n1. Test GET /api/alertes/test-email")
try:
    response = requests.get('http://localhost:5000/api/alertes/test-email')
    print(f"Status: {response.status_code}")
    print(f"Réponse: {response.json()}")
except Exception as e:
    print(f"Erreur: {e}")

# Test 2: POST pour envoyer un email
print("\n2. Test POST - Envoi d'email")
try:
    response = requests.post('http://localhost:5000/api/alertes/test-email', 
                           json={'email': 'perfumeshabibi10@gmail.com'})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ EMAIL ENVOYÉ !")
        print(f"Détails: {response.json()}")
    else:
        print(f"❌ Erreur: {response.json()}")
except Exception as e:
    print(f"Erreur: {e}")

print("\n" + "="*60)
