"use client";

import { useState, useEffect } from 'react';
import {
    Brain,
    TrendingUp,
    AlertTriangle,
    CheckCircle,
    Lightbulb,
    ArrowRight,
    BarChart3,
    Target
} from 'lucide-react';
import { getFilieres } from '@/lib/api';
import { LoadingSpinner, Badge, PageHeader } from '@/components/ui';
import axios from 'axios';

interface ModulePrediction {
    module: string;
    module_traduit: string;
    probabilite_reussite: number;
    probabilite_echec: number;
    besoin_soutien: boolean;
    categorie: {
        niveau: string;
        color: string;
        emoji: string;
    };
    action_preventive: string;
    statistiques_module: {
        moyenne: number;
        taux_echec: number;
        nb_etudiants: number;
    };
}

interface PredictionResult {
    etudiant: string;
    filiere: string;
    annee_actuelle: number;
    annees_futures: number[];
    moyenne_generale: number;
    nb_modules_passes: number;
    nb_modules_futurs: number;
    predictions: ModulePrediction[];
    resume: {
        modules_haut_risque: number;
        modules_risque_modere: number;
        modules_recommandes: number;
    };
    modules_par_categorie: {
        haut_risque: ModulePrediction[];
        risque_modere: ModulePrediction[];
        recommandes: ModulePrediction[];
    };
}

export default function ModulesFutursPage() {
    const [filieres, setFilieres] = useState<string[]>([]);
    const [codeEtudiant, setCodeEtudiant] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<PredictionResult | null>(null);

    useEffect(() => {
        getFilieres().then(setFilieres).catch(console.error);
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!codeEtudiant) {
            alert('Veuillez entrer un code étudiant');
            return;
        }

        setLoading(true);
        setResult(null);

        try {
            const response = await axios.post('http://localhost:5000/api/predict/modules-futurs', {
                code_etudiant: codeEtudiant
                // Plus besoin de filiere NI annee_actuelle !
                // Tout est automatique !
            });

            setResult(response.data);
        } catch (error: any) {
            console.error('Erreur:', error);
            const errorMsg = error.response?.data?.error || 'Erreur lors de la prédiction. Vérifiez le code étudiant.';
            alert(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    const getCategoryColor = (niveau: string) => {
        const colors: Record<string, string> = {
            'EXCELLENT': 'bg-emerald-100 text-emerald-700 border-emerald-300',
            'BON': 'bg-green-100 text-green-700 border-green-300',
            'MODÉRÉ': 'bg-yellow-100 text-yellow-700 border-yellow-300',
            'RISQUÉ': 'bg-orange-100 text-orange-700 border-orange-300',
            'TRÈS RISQUÉ': 'bg-red-100 text-red-700 border-red-300'
        };
        return colors[niveau] || 'bg-slate-100 text-slate-700 border-slate-300';
    };

    return (
        <div className="space-y-6">
            <PageHeader
                title="Modules Recommandés"
                description="Prédiction préventive pour les modules futurs basée sur l'historique"
            />

            {/* Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-start gap-3">
                    <Lightbulb className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-blue-800">
                        <p className="font-semibold mb-1">Prédiction Préventive</p>
                        <p>
                            Entrez le code d'un étudiant pour voir les modules qu'il devrait prendre ou éviter
                            basé sur son historique académique et les étudiants similaires.
                        </p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Formulaire */}
                <div className="lg:col-span-1">
                    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">
                                    Code Étudiant *
                                </label>
                                <input
                                    type="text"
                                    value={codeEtudiant}
                                    onChange={(e) => setCodeEtudiant(e.target.value)}
                                    placeholder="Ex: 191112"
                                    required
                                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                                />
                                <button
                                    type="button"
                                    onClick={() => setCodeEtudiant('191112')}
                                    className="mt-2 text-xs text-blue-600 hover:text-blue-700 hover:underline"
                                >
                                    Utiliser code de test (191112)
                                </button>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                        Analyse...
                                    </>
                                ) : (
                                    <>
                                        <Brain className="w-5 h-5" />
                                        Analyser les Modules
                                    </>
                                )}
                            </button>
                        </form>
                    </div>
                </div>

                {/* Résultats */}
                <div className="lg:col-span-2 space-y-6">
                    {loading && (
                        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                            <LoadingSpinner text="Analyse des modules futurs..." />
                        </div>
                    )}

                    {result && (
                        <>
                            {/* Info Détection Automatique */}
                            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
                                <div className="text-sm text-blue-600 font-semibold mb-3">✨ Détection Automatique</div>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                    <div className="bg-white/60 rounded-lg p-3 border border-blue-100">
                                        <div className="text-xs text-slate-500 mb-1">Filière</div>
                                        <div className="text-lg font-bold text-slate-800">{result.filiere}</div>
                                    </div>
                                    <div className="bg-white/60 rounded-lg p-3 border border-blue-100">
                                        <div className="text-xs text-slate-500 mb-1">Année Actuelle</div>
                                        <div className="text-lg font-bold text-slate-800">{result.annee_actuelle}e année</div>
                                    </div>
                                    <div className="bg-white/60 rounded-lg p-3 border border-blue-100">
                                        <div className="text-xs text-slate-500 mb-1">Prédiction Pour</div>
                                        <div className="text-lg font-bold text-slate-800">
                                            {result.annees_futures && result.annees_futures.length > 0
                                                ? `Année(s) ${result.annees_futures.join(', ')}`
                                                : 'Années futures'}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Stats */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
                                    <div className="text-2xl font-bold text-blue-600">{result.moyenne_generale}/20</div>
                                    <div className="text-sm text-slate-600 mt-1">Moyenne Générale</div>
                                </div>
                                <div className="bg-emerald-50 rounded-xl shadow-sm border border-emerald-200 p-4">
                                    <div className="text-2xl font-bold text-emerald-600">{result.resume.modules_recommandes}</div>
                                    <div className="text-sm text-slate-600 mt-1">Modules Recommandés</div>
                                </div>
                                <div className="bg-orange-50 rounded-xl shadow-sm border border-orange-200 p-4">
                                    <div className="text-2xl font-bold text-orange-600">{result.resume.modules_risque_modere}</div>
                                    <div className="text-sm text-slate-600 mt-1">Risque Modéré</div>
                                </div>
                                <div className="bg-red-50 rounded-xl shadow-sm border border-red-200 p-4">
                                    <div className="text-2xl font-bold text-red-600">{result.resume.modules_haut_risque}</div>
                                    <div className="text-sm text-slate-600 mt-1">Haut Risque</div>
                                </div>
                            </div>

                            {/* Modules à Haut Risque */}
                            {result.modules_par_categorie.haut_risque.length > 0 && (
                                <div className="bg-white rounded-xl shadow-sm border border-red-200 p-6">
                                    <h3 className="text-lg font-semibold text-red-700 mb-4 flex items-center gap-2">
                                        <AlertTriangle className="w-5 h-5" />
                                        Modules à Haut Risque
                                    </h3>
                                    <div className="space-y-3">
                                        {result.modules_par_categorie.haut_risque.map((pred, idx) => (
                                            <div key={idx} className="p-4 bg-red-50 border border-red-200 rounded-lg">
                                                <div className="flex items-start justify-between mb-2">
                                                    <div className="flex-1">
                                                        <div className="font-medium text-slate-800">{pred.module_traduit}</div>
                                                        <div className="text-sm text-slate-500">{pred.module}</div>
                                                    </div>
                                                    <div className="text-right">
                                                        <div className="text-2xl font-bold text-red-600">{pred.probabilite_reussite}%</div>
                                                        <div className="text-xs text-slate-500">Réussite</div>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2 text-sm">
                                                    <span className="text-red-700 font-medium">{pred.categorie.emoji} {pred.action_preventive}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Modules Recommandés */}
                            {result.modules_par_categorie.recommandes.length > 0 && (
                                <div className="bg-white rounded-xl shadow-sm border border-emerald-200 p-6">
                                    <h3 className="text-lg font-semibold text-emerald-700 mb-4 flex items-center gap-2">
                                        <CheckCircle className="w-5 h-5" />
                                        Modules Recommandés
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                        {result.modules_par_categorie.recommandes.map((pred, idx) => (
                                            <div key={idx} className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex-1">
                                                        <div className="font-medium text-slate-800 text-sm">{pred.module_traduit}</div>
                                                        <div className="text-xs text-slate-500">{pred.probabilite_reussite}% réussite</div>
                                                    </div>
                                                    <div className="text-2xl">{pred.categorie.emoji}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Tous les Modules */}
                            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                                <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                                    <BarChart3 className="w-5 h-5" />
                                    Tous les Modules Futurs ({result.nb_modules_futurs})
                                </h3>
                                <div className="space-y-2">
                                    {result.predictions.map((pred, idx) => (
                                        <div key={idx} className={`p-3 border rounded-lg ${getCategoryColor(pred.categorie.niveau)}`}>
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1">
                                                    <div className="font-medium">{pred.module_traduit}</div>
                                                    <div className="text-xs opacity-75 mt-1">{pred.action_preventive}</div>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <div className="text-right">
                                                        <div className="font-bold">{pred.probabilite_reussite}%</div>
                                                        <div className="text-xs opacity-75">Réussite</div>
                                                    </div>
                                                    <div className="text-2xl">{pred.categorie.emoji}</div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}

                    {!loading && !result && (
                        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                            <div className="text-center py-8">
                                <Target className="w-16 h-16 mx-auto text-slate-300 mb-4" />
                                <h3 className="text-lg font-semibold text-slate-700">Prêt pour l'analyse</h3>
                                <p className="text-slate-500 mt-1">
                                    Entrez un code étudiant pour voir les modules recommandés
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
