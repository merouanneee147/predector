"use client";

import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { PageHeader } from '@/components/ui';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    tokens?: number;
    cost?: number;
}

export default function AssistantIAPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Charger le message de bienvenue au démarrage
    useEffect(() => {
        loadWelcomeMessage();
    }, []);

    const loadWelcomeMessage = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/chat/welcome');
            setMessages([{
                role: 'assistant',
                content: response.data.message,
                timestamp: response.data.timestamp
            }]);
        } catch (error) {
            console.error('Erreur chargement bienvenue:', error);
            setError('Assistant IA non disponible');
        }
    };

    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const userMessage: Message = {
            role: 'user',
            content: input,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);
        setError('');

        try {
            // Construire l'historique pour OpenAI
            const history = messages.map(m => ({
                role: m.role,
                content: m.content
            }));

            const response = await axios.post('http://localhost:5000/api/chat/message', {
                message: input,
                history: history
            });

            const assistantMessage: Message = {
                role: 'assistant',
                content: response.data.response,
                timestamp: response.data.timestamp,
                tokens: response.data.tokens_used,
                cost: response.data.cost
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (error: any) {
            console.error('Erreur:', error);
            setError(error.response?.data?.error || 'Erreur de connexion');

            // Message d'erreur de l'assistant
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Désolé, une erreur s'est produite. ${error.response?.data?.details || 'Veuillez réessayer.'}`,
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const quickQuestions = [
        "Quels étudiants sont à risque ?",
        "Quels sont les modules les plus difficiles ?",
        "Comment fonctionne le système de prédiction ?",
        "Comment améliorer les chances de réussite ?"
    ];

    return (
        <div className="h-screen flex flex-col">
            <PageHeader
                title="Assistant IA"
                description="Posez vos questions sur les étudiants, modules et recommandations"
            />

            {error && (
                <div className="mx-6 mt-4 bg-red-50 border border-red-200 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-red-700">
                        <AlertCircle className="w-5 h-5" />
                        <span>{error}</span>
                    </div>
                </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4" data-scrollable="true">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        {message.role === 'assistant' && (
                            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                                <Bot className="w-6 h-6 text-white" />
                            </div>
                        )}

                        <div className={`max-w-2xl rounded-2xl p-4 ${message.role === 'user'
                                ? 'bg-blue-600 text-white'
                                : 'bg-white border border-slate-200 shadow-sm'
                            }`}>
                            <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                                {message.content}
                            </div>
                            <div className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-100' : 'text-slate-400'
                                }`}>
                                {new Date(message.timestamp).toLocaleTimeString('fr-FR', {
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                                {message.tokens && (
                                    <span className="ml-2">• {message.tokens} tokens</span>
                                )}
                            </div>
                        </div>

                        {message.role === 'user' && (
                            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center shadow-lg">
                                <User className="w-6 h-6 text-white" />
                            </div>
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="flex gap-3">
                        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                            <Bot className="w-6 h-6 text-white" />
                        </div>
                        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                            <div className="flex items-center gap-2 text-slate-600">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span>L'assistant réfléchit...</span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Quick Questions */}
            {messages.length === 1 && (
                <div className="px-6 py-3">
                    <div className="text-sm text-slate-600 mb-2">Questions rapides :</div>
                    <div className="flex flex-wrap gap-2">
                        {quickQuestions.map((q, i) => (
                            <button
                                key={i}
                                onClick={() => {
                                    setInput(q);
                                    setTimeout(() => sendMessage(), 100);
                                }}
                                className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm transition-colors"
                            >
                                {q}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Input */}
            <div className="border-t border-slate-200 bg-white p-6">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Posez votre question..."
                        disabled={loading}
                        className="flex-1 px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!input.trim() || loading}
                        className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-lg"
                    >
                        {loading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                <Send className="w-5 h-5" />
                                <span>Envoyer</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
