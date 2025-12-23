"""
Assistant IA Simulé - Version de secours sans OpenAI
Répond intelligemment en utilisant pattern matching + vraies données
"""
import pandas as pd
import re
from typing import List, Dict, Optional
from datetime import datetime

class AssistantIASimule:
    def __init__(self, df: pd.DataFrame = None):
        """Initialise l'assistant simulé avec les données"""
        self.df = df
        self.model = "simulé-intelligent"
        
    def get_welcome_message(self) -> str:
        """Message de bienvenue"""
        return """👋 Bonjour ! Je suis votre assistant pédagogique IA.

Je peux vous aider à :
• 📊 Comprendre les prédictions du système ML
• 👨‍🎓 Analyser les profils des étudiants
• 📈 Expliquer les statistiques des modules
• 💡 Proposer des actions de soutien personnalisées

Comment puis-je vous aider aujourd'hui ?"""

    def chat(self, 
             message: str, 
             history: List[Dict[str, str]] = None,
             context: Optional[str] = None) -> Dict:
        """
        Répond au message en utilisant pattern matching intelligent
        """
        try:
            message_lower = message.lower()
            
            # Pattern 1: Questions sur les étudiants à risque
            if any(word in message_lower for word in ['étudiant', 'risque', 'difficulté', 'échec']):
                response = self._reponse_etudiants_risque(message)
            
            # Pattern 2: Questions sur les modules
            elif any(word in message_lower for word in ['module', 'cours', 'matière', 'difficile']):
                response = self._reponse_modules(message)
            
            # Pattern 3: Questions sur le fonctionnement
            elif any(word in message_lower for word in ['comment', 'fonction', 'marche', 'système', 'ml', 'modèle']):
                response = self._reponse_fonctionnement(message)
            
            # Pattern 4: Questions sur les recommandations
            elif any(word in message_lower for word in ['recommand', 'conseil', 'action', 'aide', 'solution']):
                response = self._reponse_recommandations(message)
            
            # Pattern 5: Code étudiant spécifique
            elif re.search(r'\b\d{5,}\b', message):
                response = self._reponse_etudiant_specifique(message)
            
            # Pattern 6: Salutations
            elif any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'hi']):
                response = "Bonjour ! 👋 Comment puis-je vous aider avec le système de soutien pédagogique ?"
            
            # Pattern 7: Remerciements
            elif any(word in message_lower for word in ['merci', 'thanks']):
                response = "De rien ! N'hésitez pas si vous avez d'autres questions. 😊"
            
            # Défaut: Réponse générique
            else:
                response = self._reponse_generale(message)
            
            return {
                'response': response,
                'tokens_used': len(message.split()) + len(response.split()),
                'cost': 0.0,  # Gratuit !
                'success': True
            }
            
        except Exception as e:
            return {
                'response': f"Désolé, je n'ai pas bien compris votre question. Pouvez-vous reformuler ?",
                'tokens_used': 0,
                'cost': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def _reponse_etudiants_risque(self, message: str) -> str:
        """Répond aux questions sur les étudiants à risque"""
        if self.df is not None and 'Needs_Support' in self.df.columns:
            total_etudiants = self.df['ID'].nunique()
            etudiants_risque = self.df[self.df['Needs_Support'] == 1]['ID'].nunique()
            pourcentage = (etudiants_risque / total_etudiants * 100) if total_etudiants > 0 else 0
            
            return f"""📊 **Analyse des Étudiants à Risque**

J'ai identifié **{etudiants_risque:,} étudiants** nécessitant un soutien sur un total de {total_etudiants:,} étudiants ({pourcentage:.1f}%).

**Profils principaux à risque :**
• 🔴 Moyenne < 10/20 (échec académique)
• 🟠 Absentéisme répété
• 🟡 Plusieurs modules en difficulté
• 📉 Tendance à la baisse

**Actions recommandées :**
1. Tutorat individuel pour les cas critiques
2. Sessions de révision en groupe
3. Suivi hebdomadaire par les conseillers
4. Ressources pédagogiques personnalisées

💡 Utilisez la page "Étudiants à Risque" pour voir la liste détaillée !"""
        
        return """Les étudiants à risque sont ceux qui ont :
• Une moyenne inférieure à 10/20
• Des absences répétées
• Plusieurs modules échoués

Le système ML analyse 43 critères pour identifier précisément qui a besoin de soutien."""
    
    def _reponse_modules(self, message: str) -> str:
        """Répond aux questions sur les modules"""
        if self.df is not None and 'Module' in self.df.columns:
            nb_modules = self.df['Module'].nunique()
            
            # Modules avec le plus haut taux d'échec
            if 'Needs_Support' in self.df.columns:
                module_stats = self.df.groupby('Module').agg({
                    'Needs_Support': 'mean',
                    'Note_sur_20': 'mean'
                }).sort_values('Needs_Support', ascending=False)
                
                top_difficiles = module_stats.head(3)
                
                reponse = f"""📚 **Analyse des Modules**

Le système contient **{nb_modules} modules différents**.

**Top 3 des modules les plus difficiles :**\n"""
                
                for i, (module, row) in enumerate(top_difficiles.iterrows(), 1):
                    taux_echec = row['Needs_Support'] * 100
                    moyenne = row['Note_sur_20']
                    reponse += f"{i}. **{module}** - {taux_echec:.1f}% d'échec (Moyenne: {moyenne:.1f}/20)\n"
                
                reponse += """\n**Recommandations :**
• Renforcer le tutorat pour ces modules
• Réviser la pédagogie si taux > 30%
• Proposer des ressources supplémentaires
• Identifier les prérequis manquants

💡 Chaque module a un profil de difficulté analysé parle ML !"""
                return reponse
        
        return """Le système analyse les modules selon :
• Le taux d'échec historique
• La moyenne des étudiants
• La difficulté perçue
• Les prérequis nécessaires

Les modules les plus difficiles reçoivent plus de ressources de soutien."""
    
    def _reponse_fonctionnement(self, message: str) -> str:
        """Explique le fonctionnement du système"""
        return """🤖 **Fonctionnement du Système ML**

Notre plateforme utilise un **modèle XGBoost** avec les caractéristiques suivantes :

**🎯 Prédiction :**
• **43 features** analysées pour chaque étudiant
• **99.96% de précision** sur les données de test
• Prédiction du besoin de soutien (OUI/NON)
• Score de risque en pourcentage (0-100%)

**📊 Features Analysées :**
1. **Performance** - Notes, moyennes, régularité
2. **Contexte Module** - Difficulté, taux d'échec
3. **Comparaison Pairs** - Position dans la promotion
4. **Historique** - Tendances, progression
5. **Domaines** - Forces et faiblesses par matière

**🔄 Processus :**
1. Feature Engineering (calcul des 43 variables)
2. Normalisation (StandardScaler)
3. Prédiction XGBoost
4. Clustering K-Means pour le profil
5. Génération recommandations personnalisées

**💡 Résultat :**
Pour chaque étudiant, vous obtenez :
• Probabilité de réussite/échec
• Profil d'apprentissage
• Recommandations ciblées
• Modules à prioriser

C'est un vrai système ML, pas une simulation ! ✅"""
    
    def _reponse_recommandations(self, message: str) -> str:
        """Donne des recommandations"""
        return """💡 **Recommandations du Système**

**Pour améliorer les chances de réussite :**

**🎯 Niveau Préventif :**
• Identifier les étudiants à risque AVANT l'échec
• Proposer tutorat dès les premiers signes
• Groupes d'étude par niveau
• Ressources pédagogiques adaptées

**📚 Niveau Pédagogique :**
• TD de soutien pour modules difficiles
• Révision des prérequis manquants
• Sessions de questions-réponses
• Exercices supplémentaires ciblés

**👥 Niveau Individuel :**
• Suivi personnalisé par conseiller
• Plan d'étude adapté au profil
• Objectifs progressifs réalisables
• Feedback régulier et encouragements

**📊 Niveau Système :**
• Analyser les patterns d'échec
• Adapter la pédagogie des modules difficiles
• Former les tuteurs aux profils spécifiques
• Mesurer l'impact des interventions

**✨ Le système génère des recommandations personnalisées pour chaque étudiant !**"""

    def _reponse_etudiant_specifique(self, message: str) -> str:
        """Répond sur un étudiant spécifique"""
        # Extraire le code étudiant
        codes = re.findall(r'\b\d{5,}\b', message)
        if codes and self.df is not None:
            code = codes[0]
            student_data = self.df[self.df['ID'].astype(str) == code]
            
            if len(student_data) > 0:
                moyenne = student_data['Note_sur_20'].mean() if 'Note_sur_20' in student_data.columns else 0
                nb_modules = len(student_data)
                filiere = student_data['Filiere'].iloc[0] if 'Filiere' in student_data.columns else 'N/A'
                
                risque = "élevé" if moyenne < 10 else "modéré" if moyenne < 12 else "faible"
                emoji = "🔴" if moyenne < 10 else "🟠" if moyenne < 12 else "🟢"
                
                return f"""📋 **Analyse Étudiant {code}**

**Profil :**
• Filière : {filiere}
• Moyenne : {moyenne:.1f}/20
• Modules suivis : {nb_modules}
• Niveau de risque : {emoji} {risque}

**Analyse :**
{self._analyser_performance(moyenne)}

**Recommandations :**
{self._recommandations_par_niveau(moyenne)}

💡 Consultez la page "Modules Recommandés" pour voir les prédictions pour ses modules futurs !"""
            else:
                return f"❌ Étudiant {code} non trouvé dans la base de données."
        
        return "Pour analyser un étudiant, donnez-moi son code (ex: 191112)."
    
    def _analyser_performance(self, moyenne: float) -> str:
        """Analyse la performance selon la moyenne"""
        if moyenne >= 14:
            return "✨ Excellente performance ! Cet étudiant est dans le top de sa promotion."
        elif moyenne >= 12:
            return "✅ Bon niveau. L'étudiant maîtrise bien le contenu."
        elif moyenne >= 10:
            return "⚠️ Niveau passable. Surveillance recommandée pour éviter la baisse."
        else:
            return "🚨 Performance insuffisante. Intervention urgente nécessaire !"
    
    def _recommandations_par_niveau(self, moyenne: float) -> str:
        """Recommandations selon le niveau"""
        if moyenne >= 14:
            return """• Proposer projet avancé ou tutorat pair
• Ressources d'approfondissement"""
        elif moyenne >= 12:
            return """• Maintenir le rythme actuel
• Ressources complémentaires disponibles"""
        elif moyenne >= 10:
            return """• TD de soutien recommandés
• Suivi régulier conseillé"""
        else:
            return """• Tutorat individuel URGENT
• Révision complète des bases
• Suivi hebdomadaire obligatoire"""
    
    def _reponse_generale(self, message: str) -> str:
        """Réponse générique intelligente"""
        return """Je suis là pour vous aider avec la plateforme de soutien pédagogique !

**Je peux répondre à des questions sur :**
• 👨‍🎓 Les étudiants à risque et leurs profils
• 📚 Les modules difficiles et statistiques
• 🤖 Le fonctionnement du système ML
• 💡 Les recommandations et actions
• 📊 Les analyses et prédictions

**Exemples de questions :**
• "Quels étudiants sont à risque ?"
• "Quels sont les modules les plus difficiles ?"
• "Comment fonctionne la prédiction ?"
• "Analyse l'étudiant 191112"

Que souhaitez-vous savoir ? 😊"""
