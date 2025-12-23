"""
Assistant IA utilisant OpenAI GPT-3.5-Turbo
Service pour gérer les conversations avec contexte des données pédagogiques
"""
import os
from openai import OpenAI
from typing import List, Dict, Optional
import pandas as pd

class AssistantIA:
    def __init__(self, df: pd.DataFrame = None):
        """
        Initialise l'assistant IA avec la clé OpenAI
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY non trouvée dans les variables d'environnement")
        
        self.client = OpenAI(api_key=api_key)
        self.df = df
        self.model = "gpt-3.5-turbo"  # Économique et rapide
        
        # System prompt optimisé pour le contexte pédagogique
        self.system_prompt = """Tu es un assistant pédagogique expert pour un système de recommandation de soutien 
pédagogique dans les universités marocaines.

TON RÔLE:
- Aider les enseignants et tuteurs à comprendre les prédictions du système ML
- Expliquer de manière claire pourquoi un étudiant est à risque
- Proposer des actions concrètes et personnalisées
- Répondre aux questions sur les modules, filières et statistiques

STYLE DE RÉPONSE:
- Professionnel mais accessible
- Concis et actionnable (maximum 3-4 paragraphes)
- Utilise des emojis pour rendre les réponses plus engageantes
- Structure tes réponses avec des points clés
- Toujours en français

DONNÉES DISPONIBLES:
Le système contient des données réelles sur:
- Profils étudiants (notes, moyennes, historique académique)
- Prédictions ML (probabilités de risque, profils d'apprentissage)
- Statistiques modules (taux d'échec, difficultés, moyennes)
- Recommandations automatiques générées par IA

IMPORTANT:
- Base tes réponses sur les données fournies dans le contexte
- Si les données ne sont pas disponibles, dis-le clairement
- Sois encourageant et propose toujours des solutions"""

    def get_context_from_data(self, message: str) -> str:
        """
        Extrait du contexte pertinent depuis les données selon la question
        """
        if self.df is None:
            return ""
        
        context_parts = []
        message_lower = message.lower()
        
        # Si mention d'un code étudiant (chiffres)
        import re
        student_codes = re.findall(r'\b\d{5,}\b', message)
        if student_codes:
            for code in student_codes[:1]:  # Limiter à 1 pour éviter trop de contexte
                student_data = self.df[self.df['ID'].astype(str) == code]
                if len(student_data) > 0:
                    moyenne = student_data['Note_sur_20'].mean() if 'Note_sur_20' in student_data.columns else 0
                    nb_modules = len(student_data)
                    filiere = student_data['Filiere'].iloc[0] if 'Filiere' in student_data.columns else 'N/A'
                    context_parts.append(f"Étudiant {code}: Filière {filiere}, Moyenne {moyenne:.1f}/20, {nb_modules} modules")
        
        # Statistiques générales si demandées
        if any(word in message_lower for word in ['statistique', 'combien', 'nombre', 'total']):
            total_students = self.df['ID'].nunique() if 'ID' in self.df.columns else 0
            context_parts.append(f"Total étudiants dans le système: {total_students}")
        
        # Informations sur les modules
        if 'module' in message_lower and 'Module' in self.df.columns:
            modules = self.df['Module'].unique()[:5]  # Top 5 modules
            context_parts.append(f"Modules disponibles: {', '.join(modules)}")
        
        return "\n\n".join(context_parts) if context_parts else ""

    def chat(self, 
             message: str, 
             history: List[Dict[str, str]] = None,
             context: Optional[str] = None) -> Dict:
        """
        Envoie un message à l'assistant et retourne la réponse
        
        Args:
            message: Message de l'utilisateur
            history: Historique de conversation (liste de {role, content})
            context: Contexte additionnel (données étudiant, stats, etc.)
        
        Returns:
            Dict avec 'response', 'tokens_used', 'cost'
        """
        try:
            # Construire l'historique des messages
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Ajouter contexte des données si disponible
            data_context = self.get_context_from_data(message)
            if data_context:
                messages.append({
                    "role": "system", 
                    "content": f"Données pertinentes:\n{data_context}"
                })
            
            # Ajouter contexte supplémentaire si fourni
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Contexte additionnel:\n{context}"
                })
            
            # Ajouter historique de conversation
            if history:
                messages.extend(history[-10:])  # Garder les 10 derniers messages max
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": message})
            
            # Appel à l'API OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,  # Limite pour économiser
            )
            
            # Extraire la réponse
            assistant_message = response.choices[0].message.content
            
            # Calculer le coût (GPT-3.5-turbo: $0.50/1M input, $1.50/1M output)
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            cost = (input_tokens * 0.50 / 1_000_000) + (output_tokens * 1.50 / 1_000_000)
            
            return {
                'response': assistant_message,
                'tokens_used': total_tokens,
                'cost': cost,
                'success': True
            }
            
        except Exception as e:
            return {
                'response': f"Désolé, une erreur s'est produite: {str(e)}",
                'tokens_used': 0,
                'cost': 0,
                'success': False,
                'error': str(e)
            }

    def get_welcome_message(self) -> str:
        """Message de bienvenue de l'assistant"""
        return """👋 Bonjour ! Je suis votre assistant pédagogique IA.

Je peux vous aider à :
• 📊 Comprendre les prédictions du système ML
• 👨‍🎓 Analyser les profils desétudiants
• 📈 Expliquer les statistiques des modules
• 💡 Proposer des actions de soutien personnalisées

Comment puis-je vous aider aujourd'hui ?"""
