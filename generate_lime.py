"""
Génération LIME - Version Adaptée pour CalibratedClassifierCV
Explications locales des prédictions individuelles
"""
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lime import lime_tabular
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
OUTPUT_DIR = Path("documentation_rapport/lime")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = Path("output_projet4/model_soutien_pedagogique.joblib")

print("=" * 70)
print("GÉNÉRATION VISUALISATIONS LIME - VERSION ADAPTÉE")
print("=" * 70)

# 1. Charger le modèle
print("\n1. Chargement du modèle ML...")
model_data = joblib.load(MODEL_PATH)
model = model_data['model']  # Garde le CalibratedClassifier pour predict_proba
feature_columns = model_data['feature_columns']
scaler = model_data['scaler']

print(f"✅ Modèle chargé: {len(feature_columns)} features")
print(f"   Type: {type(model)}")

# 2. Charger les données
print("\n2. Chargement des données...")
df1 = pd.read_csv("raw/1- one_clean.csv", encoding='utf-8')
df2 = pd.read_csv("raw/2- two_clean.csv", encoding='utf-8')
df = pd.concat([df1, df2], ignore_index=True)

# Nettoyage
df['ID'] = df['ID'].astype(str)
df = df[~df['ID'].isin(['Unknown', 'unknown', 'nan', 'None', ''])].copy()
df = df.rename(columns={'Major': 'Filiere', 'Subject': 'Module'})
df['Note_sur_20'] = df['Total'] / 5

print(f"✅ {len(df):,} enregistrements chargés")

# 3. Préparer les données
print("\n3. Préparation des données...")
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
features_df = df[numeric_cols].fillna(0)

# Aligner avec feature_columns
missing_cols = set(feature_columns) - set(features_df.columns)
for col in missing_cols:
    features_df[col] = 0

X = features_df[feature_columns].values
X_scaled = scaler.transform(X)

# Identifier des exemples intéressants
y_pred = model.predict(X_scaled)
risque_idx = np.where(y_pred == 1)[0]
performant_idx = np.where(y_pred == 0)[0]

# Prendre des exemples
idx_risque = risque_idx[0] if len(risque_idx) > 0 else 0
idx_performant = performant_idx[0] if len(performant_idx) > 0 else 1

print(f"✅ Exemple à risque: index {idx_risque}")
print(f"✅ Exemple performant: index {idx_performant}")

# 4. Créer l'explainer LIME
print("\n4. Création de l'explainer LIME...")
explainer = lime_tabular.LimeTabularExplainer(
    X_scaled,
    feature_names=feature_columns,
    class_names=['Pas de Soutien', 'Besoin Soutien'],
    mode='classification',
    random_state=42
)
print("✅ Explainer créé")

# 5. Générer les explications
print("\n5. Génération des explications...")
print("⏳ (Calcul en cours, cela peut prendre 1-2 minutes...)")

# 5.1 Explication pour étudiant à risque
print("   📊 Explication étudiant à risque...")
exp_risque = explainer.explain_instance(
    X_scaled[idx_risque], 
    model.predict_proba,
    num_features=10,
    num_samples=500
)

fig = exp_risque.as_pyplot_figure()
fig.set_size_inches(12, 6)
plt.suptitle("LIME - Explication Prédiction: Étudiant À RISQUE", 
            fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "lime_risque.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ lime_risque.png")

# 5.2 Explication pour étudiant performant
print("   📊 Explication étudiant performant...")
exp_performant = explainer.explain_instance(
    X_scaled[idx_performant],
    model.predict_proba,
    num_features=10,
    num_samples=500
)

fig = exp_performant.as_pyplot_figure()
fig.set_size_inches(12, 6)
plt.suptitle("LIME - Explication Prédiction: Étudiant PERFORMANT", 
            fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "lime_performant.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ lime_performant.png")

# 5.3 Comparaison côte-à-côte
print("   📊 Comparaison features...")
features_risque = exp_risque.as_list()
features_perf = exp_performant.as_list()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# À risque
features_r = sorted(features_risque, key=lambda x: abs(x[1]), reverse=True)[:10]
names_r = [f[0] for f in features_r]
values_r = [f[1] for f in features_r]
colors_r = ['#EF4444' if v > 0 else '#10B981' for v in values_r]

ax1.barh(range(len(names_r)), values_r, color=colors_r, alpha=0.7)
ax1.set_yticks(range(len(names_r)))
ax1.set_yticklabels(names_r, fontsize=9)
ax1.set_xlabel('Impact sur Prédiction "Besoin Soutien"', fontsize=10, fontweight='bold')
ax1.set_title('Étudiant À RISQUE\nFeatures Influentes', fontsize=12, fontweight='bold')
ax1.axvline(x=0, color='black', linestyle='--', alpha=0.3)
ax1.grid(axis='x', alpha=0.3)

# Performant
features_p = sorted(features_perf, key=lambda x: abs(x[1]), reverse=True)[:10]
names_p = [f[0] for f in features_p]
values_p = [f[1] for f in features_p]
colors_p = ['#EF4444' if v > 0 else '#10B981' for v in values_p]

ax2.barh(range(len(names_p)), values_p, color=colors_p, alpha=0.7)
ax2.set_yticks(range(len(names_p)))
ax2.set_yticklabels(names_p, fontsize=9)
ax2.set_xlabel('Impact sur Prédiction "Besoin Soutien"', fontsize=10, fontweight='bold')
ax2.set_title('Étudiant PERFORMANT\nFeatures Influentes', fontsize=12, fontweight='bold')
ax2.axvline(x=0, color='black', linestyle='--', alpha=0.3)
ax2.grid(axis='x', alpha=0.3)

plt.suptitle('LIME - Comparaison Explicabilité Locale', fontsize=14, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "lime_comparaison.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ lime_comparaison.png")

# 6. Créer un rapport texte
print("\n6. Génération du rapport texte...")
with open(OUTPUT_DIR / "explanations.txt", 'w', encoding='utf-8') as f:
    f.write("LIME - Explications Locales\n")
    f.write("=" * 60 + "\n\n")
    
    f.write("ÉTUDIANT À RISQUE\n")
    f.write("-" * 60 + "\n")
    f.write(f"Prédiction: {exp_risque.predict_proba[1]:.2%} de besoin de soutien\n\n")
    f.write("Top 10 Features:\n")
    for feature, impact in features_r:
        direction = "↑ Augmente" if impact > 0 else "↓ Diminue"
        f.write(f"  {direction} le risque: {feature}\n")
        f.write(f"    Impact: {impact:+.4f}\n")
    
    f.write("\n\nÉTUDIANT PERFORMANT\n")
    f.write("-" * 60 + "\n")
    f.write(f"Prédiction: {exp_performant.predict_proba[1]:.2%} de besoin de soutien\n\n")
    f.write("Top 10 Features:\n")
    for feature, impact in features_p:
        direction = "↑ Augmente" if impact > 0 else "↓ Diminue"
        f.write(f"  {direction} le risque: {feature}\n")
        f.write(f"    Impact: {impact:+.4f}\n")

print("   ✅ explanations.txt")

# 7. Résumé
print("\n" + "=" * 70)
print("✅ VISUALISATIONS LIME GÉNÉRÉES AVEC SUCCÈS !")
print("=" * 70)
print(f"\n📁 Dossier: {OUTPUT_DIR.absolute()}")
print("\nFichiers créés:")
files_created = list(OUTPUT_DIR.glob("*.png")) + list(OUTPUT_DIR.glob("*.txt"))
for f in sorted(files_created):
    print(f"  ✅ {f.name}")
print(f"\nTotal: {len(files_created)} fichiers")
print("\n💡 Ces images montrent comment le modèle justifie ses prédictions !")
print("=" * 70)
