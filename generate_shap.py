"""
Génération SHAP - Version Adaptée pour CalibratedClassifierCV
Extrait le modèle XGBoost et génère les visualisations
"""
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
OUTPUT_DIR = Path("documentation_rapport/shap")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = Path("output_projet4/model_soutien_pedagogique.joblib")

print("=" * 70)
print("GÉNÉRATION VISUALISATIONS SHAP - VERSION ADAPTÉE")
print("=" * 70)

# 1. Charger et préparer le modèle
print("\n1. Chargement du modèle ML...")
model_data = joblib.load(MODEL_PATH)
calibrated_model = model_data['model']

# Extraire le XGBoost du CalibratedClassifierCV
print("   Type de modèle:", type(calibrated_model))

# CalibratedClassifierCV stocke les estimateurs dans .calibrated_classifiers_
if hasattr(calibrated_model, 'calibrated_classifiers_'):
    # Prendre le premier estimateur calibré
    calibrated_clf = calibrated_model.calibrated_classifiers_[0]
    # L'estimateur de base est dans .estimator (pas base_estimator)
    xgb_model = calibrated_clf.estimator
    print(f"✅ XGBoost extrait: {type(xgb_model)}")
elif hasattr(calibrated_model, 'estimator'):
    xgb_model = calibrated_model.estimator
    print(f"✅ Estimateur extrait: {type(xgb_model)}")
else:
    # Si rien ne marche, utiliser le modèle tel quel
    xgb_model = calibrated_model
    print(f"✅ Modèle direct: {type(xgb_model)}")

feature_columns = model_data['feature_columns']
scaler = model_data['scaler']

print(f"✅ Modèle chargé: {len(feature_columns)} features")

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

# 3. Préparer échantillon
print("\n3. Préparation échantillon pour SHAP...")
sample_size = 100
df_sample = df.sample(n=min(sample_size, len(df)), random_state=42)

# Préparer features
numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()
features_sample = df_sample[numeric_cols].fillna(0)

# Aligner avec feature_columns
missing_cols = set(feature_columns) - set(features_sample.columns)
for col in missing_cols:
    features_sample[col] = 0

X_sample = features_sample[feature_columns]
X_sample_scaled = scaler.transform(X_sample)

print(f"✅ Échantillon préparé: {len(X_sample)} exemples")

# 4. Créer explainer SHAP
print("\n4. Création de l'explainer SHAP...")
print("⏳ Calcul des SHAP values (peut prendre 2-3 minutes)...")

explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_sample_scaled)

print("✅ SHAP values calculées")

# 5. Générer visualisations
print("\n5. Génération des visualisations...")

# 5.1 Summary Plot
print("   📊 Summary Plot...")
plt.figure(figsize=(12, 8))
shap.summary_plot(shap_values, X_sample_scaled, feature_names=feature_columns, show=False)
plt.title("SHAP Summary Plot - Importance Globale des Features", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "shap_summary.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ shap_summary.png")

# 5.2 Feature Importance (Bar)
print("   📊 Feature Importance...")
plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_sample_scaled, feature_names=feature_columns, 
                 plot_type="bar", show=False)
plt.title("SHAP Feature Importance - Classement des Features", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "shap_importance.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ shap_importance.png")

# 5.3 Force Plot
print("   📊 Force Plot...")
try:
    shap.force_plot(explainer.expected_value, shap_values[0], X_sample_scaled[0], 
                   feature_names=feature_columns, matplotlib=True, show=False)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "shap_force.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✅ shap_force.png")
except Exception as e:
    print(f"   ⚠️ Force plot non généré: {e}")

# 5.4 Waterfall Plot
print("   📊 Waterfall Plot...")
try:
    plt.figure(figsize=(10, 8))
    shap.plots._waterfall.waterfall_legacy(explainer.expected_value, shap_values[0], 
                                           feature_names=feature_columns, show=False)
    plt.title("SHAP Waterfall - Contribution de Chaque Feature", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "shap_waterfall.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✅ shap_waterfall.png")
except Exception as e:
    print(f"   ⚠️ Waterfall plot non généré: {e}")

# 5.5 Dependence Plots (top 3 features)
print("   📊 Dependence Plots (top 3 features)...")
feature_importance = np.abs(shap_values).mean(0)
top_features_idx = np.argsort(feature_importance)[-3:]

for idx in top_features_idx:
    feature_name = feature_columns[idx]
    safe_name = feature_name.replace('/', '_').replace(' ', '_').replace('(', '').replace(')', '')
    
    try:
        plt.figure(figsize=(8, 6))
        shap.dependence_plot(idx, shap_values, X_sample_scaled, 
                            feature_names=feature_columns, show=False)
        plt.title(f"SHAP Dependence - {feature_name}", fontsize=12, fontweight='bold')
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"shap_dependence_{safe_name}.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"   ✅ shap_dependence_{safe_name}.png")
    except Exception as e:
        print(f"   ⚠️ Erreur pour {feature_name}: {e}")

# 6. Créer un récapitulatif des features importantes
print("\n6. Génération du récapitulatif...")
feature_importance_dict = {
    feature_columns[i]: abs(shap_values).mean(0)[i]
    for i in range(len(feature_columns))
}
sorted_features = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)

with open(OUTPUT_DIR / "feature_importance.txt", 'w', encoding='utf-8') as f:
    f.write("SHAP Feature Importance - Top 20 Features\n")
    f.write("=" * 60 + "\n\n")
    for i, (feature, importance) in enumerate(sorted_features[:20], 1):
        f.write(f"{i:2d}. {feature:40s} {importance:.6f}\n")

print("   ✅ feature_importance.txt")

# 7. Résumé
print("\n" + "=" * 70)
print("✅ VISUALISATIONS SHAP GÉNÉRÉES AVEC SUCCÈS !")
print("=" * 70)
print(f"\n📁 Dossier: {OUTPUT_DIR.absolute()}")
print("\nFichiers créés:")
files_created = list(OUTPUT_DIR.glob("*.png")) + list(OUTPUT_DIR.glob("*.txt"))
for f in sorted(files_created):
    print(f"  ✅ {f.name}")
print(f"\nTotal: {len(files_created)} fichiers")
print("\n💡 Ces images sont prêtes pour votre rapport PFA !")
print("=" * 70)
