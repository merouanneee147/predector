
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report, roc_curve, auc, roc_auc_score

# Configuration
RAW_PATH = Path("raw")
OUTPUT_PATH = Path("visualizations_metrics")
OUTPUT_PATH.mkdir(exist_ok=True)
plt.style.use('seaborn-v0_8-whitegrid')

print("Loading data...")
# Load data similar to main script
try:
    df1 = pd.read_csv(RAW_PATH / "1- one_clean.csv")
    df2 = pd.read_csv(RAW_PATH / "2- two_clean.csv")
    df = pd.concat([df1, df2], ignore_index=True)
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# Cleaning
print("Cleaning data...")
df['ID'] = df['ID'].astype(str)
df = df[~df['ID'].isin(['Unknown', 'unknown', 'nan', 'None', ''])]
df = df[~df['Major'].astype(str).str.lower().str.contains('unknown', na=False)]
df = df[~df['Subject'].astype(str).str.lower().str.contains('unknown', na=False)]
df = df[df['Total'].notna() | (df['Practical'].notna() & df['Theoretical'].notna())].copy()

# Rename
df = df.rename(columns={'Major': 'Filiere', 'Subject': 'Module', 'MajorYear': 'Annee', 'OfficalYear': 'AnneUniversitaire'})
df['Practical'] = pd.to_numeric(df['Practical'], errors='coerce').fillna(0)
df['Theoretical'] = pd.to_numeric(df['Theoretical'], errors='coerce').fillna(0)
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
df['Total'] = df['Total'].fillna(df['Practical'] + df['Theoretical'])

if df['Total'].max() > 20:
    df['Note_sur_20'] = df['Total'] / 5
else:
    df['Note_sur_20'] = df['Total']

# Target creation
status_mapping = {'Pass': 'Validé', 'Fail': 'Non_Validé', 'Absent': 'Absent', 'Debarred': 'Exclu', 'Withdrawal': 'Abandon', 'Withhold': 'En_Attente', 'Exempt': 'Dispensé'}
df['Statut_MA'] = df['Status'].map(status_mapping).fillna(df['Status'])

def needs_support_ma(row):
    if row['Status'] == 'Fail' or row['Statut_MA'] == 'Non_Validé': return 1
    if pd.notna(row['Note_sur_20']) and row['Note_sur_20'] > 0 and row['Note_sur_20'] < 10: return 1
    if pd.notna(row['Total']) and row['Total'] > 0 and row['Total'] < 50: return 1
    if row['Statut_MA'] in ['Absent', 'Exclu', 'Abandon', 'En_Attente']: return 1
    return 0

df['Needs_Support'] = df.apply(needs_support_ma, axis=1)

# Feature Engineering (Unified for speed)
print("Feature Engineering...")
# Student profile
student_profile = df.groupby('ID').agg({
    'Total': ['mean', 'std'],
    'Note_sur_20': ['mean', 'min'],
    'Needs_Support': ['sum', 'mean']
}).reset_index()
student_profile.columns = ['ID', 'stud_mean_total', 'stud_std_total', 'stud_mean_note20', 'stud_min_note20', 'stud_support_sum', 'stud_support_rate']
df = df.merge(student_profile, on='ID', how='left')

# Module profile
module_profile = df.groupby('Module').agg({'Needs_Support': 'mean', 'Note_sur_20': 'mean'}).reset_index()
module_profile.columns = ['Module', 'mod_failure_rate', 'mod_mean_note20']
df = df.merge(module_profile, on='Module', how='left')

# Contextual
df['distance_seuil'] = df['Note_sur_20'] - 10

# Preparation
feature_cols = ['Note_sur_20', 'stud_mean_note20', 'stud_support_rate', 'mod_failure_rate', 'distance_seuil', 'stud_std_total']
X = df[feature_cols].fillna(0)
y = df['Needs_Support']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Training model...")
model = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]

# --- Visualizations ---

# 1. Confusion Matrix
print("Generating Confusion Matrix...")
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Validé', 'Besoin Soutien'], yticklabels=['Validé', 'Besoin Soutien'])
plt.title('Matrice de Confusion (Confusion Matrix)')
plt.ylabel('Réel')
plt.xlabel('Prédit')
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'confusion_matrix.png')
plt.close()

# 2. Correlation Matrix
print("Generating Correlation Matrix...")
# Combine X and y for correlation
data_corr = X.copy()
data_corr['Target (Needs_Support)'] = y
corr = data_corr.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Matrice de Corrélation (Correlation Matrix)')
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'correlation_matrix.png')
plt.close()

# 3. ROC Curve
print("Generating ROC Curve...")
fpr, tpr, _ = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Taux de Faux Positifs')
plt.ylabel('Taux de Vrais Positifs')
plt.title('Courbe ROC')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'roc_curve.png')
plt.close()

# 4. Accuracy / Report text
print("Saving metrics...")
acc = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

with open(OUTPUT_PATH / 'metrics_summary.txt', 'w', encoding='utf-8') as f:
    f.write(f"Accuracy: {acc:.4f}\n\n")
    f.write("Classification Report:\n")
    f.write(report)
    f.write(f"\nROC AUC: {roc_auc:.4f}\n")

# 5. XGBoost Feature Importance
print("Generating Feature Importance...")
importance = model.feature_importances_
feature_names = X.columns
feat_imp = pd.DataFrame({'feature': feature_names, 'importance': importance}).sort_values('importance', ascending=False).head(15)

plt.figure(figsize=(10, 8))
sns.barplot(x='importance', y='feature', data=feat_imp, palette='viridis')
plt.title('Top 15 Features les plus importantes (XGBoost)')
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'feature_importance.png')
plt.close()

# 6. Target Distribution
print("Generating Target Distribution...")
plt.figure(figsize=(6, 6))
df['Needs_Support'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#66b3ff', '#ff9999'], labels=['Validé (0)', 'Besoin Soutien (1)'])
plt.title('Répartition de la variable cible (Needs_Support)')
plt.ylabel('')
plt.savefig(OUTPUT_PATH / 'class_distribution.png')
plt.close()

# 7. Grade Distribution by Class
print("Generating Grade Distribution...")
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='Note_sur_20', hue='Needs_Support', kde=True, palette={0: 'blue', 1: 'red'}, bins=30, alpha=0.6)
plt.title('Distribution des Notes sur 20 par Classe')
plt.xlabel('Note / 20')
plt.ylabel('Nombre d\'étudiants')
plt.legend(title='Statut', labels=['Besoin Soutien', 'Validé'])
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'grade_distribution.png')
plt.close()

# 8. Precision-Recall Curve
print("Generating Precision-Recall Curve...")
from sklearn.metrics import precision_recall_curve, average_precision_score
precision, recall, _ = precision_recall_curve(y_test, y_proba)
avg_precision = average_precision_score(y_test, y_proba)

plt.figure(figsize=(8, 6))
plt.plot(recall, precision, color='purple', lw=2, label=f'AP = {avg_precision:.4f}')
plt.xlabel('Rappel (Recall)')
plt.ylabel('Précision (Precision)')
plt.title('Courbe Précision-Rappel')
plt.legend(loc="lower left")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'pr_curve.png')
plt.close()

# 9. Learning Curve
print("Generating Learning Curve...")
from sklearn.model_selection import learning_curve

train_sizes, train_scores, test_scores = learning_curve(
    model, X_train_scaled, y_train, cv=5, n_jobs=-1, 
    train_sizes=np.linspace(0.1, 1.0, 5), scoring='accuracy'
)

train_scores_mean = np.mean(train_scores, axis=1)
train_scores_std = np.std(train_scores, axis=1)
test_scores_mean = np.mean(test_scores, axis=1)
test_scores_std = np.std(test_scores, axis=1)

plt.figure(figsize=(10, 6))
plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                 train_scores_mean + train_scores_std, alpha=0.1, color="r")
plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                 test_scores_mean + test_scores_std, alpha=0.1, color="g")
plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Score d'entraînement")
plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Score de validation croisée")
plt.xlabel("Taille du jeu d'entraînement")
plt.ylabel("Accuracy")
plt.title("Courbe d'apprentissage (Learning Curve)")
plt.legend(loc="best")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'learning_curve.png')
plt.close()

# 10. Calibration Curve
print("Generating Calibration Curve...")
from sklearn.calibration import calibration_curve

prob_true, prob_pred = calibration_curve(y_test, y_proba, n_bins=10)

plt.figure(figsize=(8, 8))
plt.plot([0, 1], [0, 1], "k:", label="Parfaitement calibré")
plt.plot(prob_pred, prob_true, "s-", label="XGBoost Calibré")
plt.xlabel("Probabilité moyenne prédite")
plt.ylabel("Fraction de positifs réels")
plt.title("Courbe de Calibration (Reliability Diagram)")
plt.legend(loc="lower right")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'calibration_curve.png')
plt.close()

# 11. Violin Plot (Total vs Target)
print("Generating Violin Plot...")
plt.figure(figsize=(10, 6))
sns.violinplot(x='Needs_Support', y='Total', data=df, palette=['lightgreen', 'salmon'])
plt.title("Distribution de la Note Totale par Statut")
plt.xlabel("Statut (0: Validé, 1: Besoin Soutien)")
plt.ylabel("Note Totale")
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'violin_plot.png')
plt.close()

plt.savefig(OUTPUT_PATH / 'violin_plot.png')
plt.close()

# 12. Model Comparison
print("Generating Model Comparison...")
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

models = {
    'XGBoost': model,
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42)
}

results = []
for name, clf in models.items():
    if name != 'XGBoost': # XGBoost already trained
        clf.fit(X_train_scaled, y_train)
    
    y_p = clf.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_p)
    if hasattr(clf, "predict_proba"):
        auc_score = roc_auc_score(y_test, clf.predict_proba(X_test_scaled)[:, 1])
    else:
        auc_score = 0
    results.append({'Model': name, 'Accuracy': acc, 'AUC': auc_score})

df_res = pd.DataFrame(results)

plt.figure(figsize=(10, 6))
df_melt = df_res.melt(id_vars='Model', var_name='Métrique', value_name='Score')
sns.barplot(x='Model', y='Score', hue='Métrique', data=df_melt, palette='viridis')
plt.ylim(0.9, 1.01) # Zoom on high performance
plt.title("Comparaison des performances des modèles")
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'model_comparison.png')
plt.close()

# 13. Clustering Visualization (PCA)
print("Generating Cluster Visualization...")
from sklearn.decomposition import PCA

# Fit KMeans
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_train_scaled)

# PCA for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_train_scaled)

plt.figure(figsize=(10, 8))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis', alpha=0.6, s=10)
plt.title("Visualisation des Profils d'Apprenants (PCA)")
plt.xlabel("Composante Principale 1")
plt.ylabel("Composante Principale 2")
plt.colorbar(scatter, label='Cluster')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'cluster_visualization.png')
plt.close()

# 14. Cluster Distribution
print("Generating Cluster Distribution...")
unique, counts = np.unique(clusters, return_counts=True)
cluster_counts = pd.DataFrame({'Cluster': unique, 'Count': counts})

plt.figure(figsize=(8, 6))
sns.barplot(x='Cluster', y='Count', data=cluster_counts, palette='viridis')
plt.title("Répartition des étudiants par Profil (Cluster)")
plt.xlabel("Cluster (Profil)")
plt.ylabel("Nombre d'étudiants")
plt.tight_layout()
plt.savefig(OUTPUT_PATH / 'cluster_distribution.png')
plt.close()

plt.savefig(OUTPUT_PATH / 'cluster_distribution.png')
plt.close()

# End of Visualizations
print(f"\nVisualizations saved to: {OUTPUT_PATH.absolute()}")

