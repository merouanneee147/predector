"""
Liste toutes les routes Flask enregistrées
"""
from app import app

print("="*70)
print("ROUTES FLASK ENREGISTRÉES")
print("="*70)

routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
        'route': str(rule)
    })

# Trier par route
routes.sort(key=lambda x: x['route'])

# Grouper par type
api_routes = [r for r in routes if r['route'].startswith('/api')]
other_routes = [r for r in routes if not r['route'].startswith('/api')]

print(f"\n📍 ROUTES /api/* ({len(api_routes)} routes)")
print("-"*70)
for route in api_routes:
    print(f"{route['methods']:20} {route['route']}")

# Chercher spécifiquement les routes alertes
print(f"\n🔍 ROUTES ALERTES")
print("-"*70)
alertes = [r for r in api_routes if 'alerte' in r['route'].lower()]
if alertes:
    for route in alertes:
        print(f"✅ {route['methods']:20} {route['route']}")
else:
    print("❌ Aucune route /alerte* trouvée !")

print("\n" + "="*70)
