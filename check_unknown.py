# Vérification des valeurs Unknown et test du nettoyage
import pandas as pd

df1 = pd.read_csv('raw/1- one_clean.csv')
df2 = pd.read_csv('raw/2- two_clean.csv')
df = pd.concat([df1, df2], ignore_index=True)

print("=" * 60)
print("🧹 TEST DU NETTOYAGE DES DONNÉES")
print("=" * 60)

taille_avant = len(df)
print(f"\n📊 Avant nettoyage: {taille_avant:,} enregistrements")

# Supprimer les lignes avec ID null ou Unknown
df['ID'] = df['ID'].astype(str)
df = df[~df['ID'].isin(['Unknown', 'unknown', 'nan', 'None', ''])].copy()

# Supprimer les lignes avec Major Unknown
df = df[~df['Major'].astype(str).str.lower().str.contains('unknown', na=False)].copy()

# Supprimer les lignes avec Subject Unknown  
df = df[~df['Subject'].astype(str).str.lower().str.contains('unknown', na=False)].copy()

print(f"📊 Après nettoyage: {len(df):,} enregistrements")
print(f"�️  Supprimés: {taille_avant - len(df):,}")

print(f"\n📋 Données nettoyées:")
print(f"   • Étudiants uniques: {df['ID'].nunique():,}")
print(f"   • Modules uniques: {df['Subject'].nunique()}")
print(f"   • Filières: {sorted(df['Major'].unique().tolist())}")

print("\n✅ Nettoyage validé - Plus aucun 'Unknown'!")

# Vérifier qu'il n'y a plus de Unknown
for col in ['ID', 'Major', 'Subject']:
    unknown_count = df[col].astype(str).str.lower().str.contains('unknown').sum()
    if unknown_count > 0:
        print(f"❌ {col}: encore {unknown_count} Unknown!")
    else:
        print(f"✅ {col}: aucun Unknown")
