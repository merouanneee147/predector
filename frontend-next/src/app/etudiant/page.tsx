'use client';

import { useState, useEffect } from 'react';
import {
    TrendingUp,
    AlertTriangle,
    BookOpen,
    Target,
    Award,
    ChevronRight,
    MessageSquare,
    FileText,
    Calendar,
    BarChart3,
    Brain
} from 'lucide-react';

export default function EtudiantDashboard() {
    const [loading, setLoading] = useState(true);
    const [etudiant, setEtudiant] = useState<any>(null);

    useEffect(() => {
        // Simuler chargement données étudiant
        setTimeout(() => {
            setEtudiant({
                code: '191112',
                nom: 'Ahmed Benali',
                filiere: 'EEA',
                annee: 2,
                moyenne: 11.2,
                profil: 'En Difficulté',
                risque: 78.5,
                modules_total: 27,
                modules_reussis: 23,
                modules_echoues: 4,
                recommandations: [
                    'Tutorat individuel URGENT',
                    'Révision des bases en Thermodynamique',
                    'Suivi hebdomadaire avec tuteur',
                ]
            });
            setLoading(false);
        }, 500);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-600 font-medium">Chargement...</p>
                </div>
            </div>
        );
    }

    const getProfilColor = (profil: string) => {
        if (profil === 'Excellence') return 'from-emerald-500 to-teal-600';
        if (profil === 'Régulier') return 'from-blue-500 to-indigo-600';
        if (profil === 'Passable') return 'from-amber-500 to-orange-500';
        return 'from-red-500 to-rose-600';
    };

    const getProfilIcon = (profil: string) => {
        if (profil === 'Excellence') return '⭐';
        if (profil === 'Régulier') return '✅';
        if (profil === 'Passable') return '⚠️';
        return '🔴';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 text-white">
                <div className="max-w-7xl mx-auto px-6 py-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold mb-2">
                                Bonjour, {etudiant.nom} 👋
                            </h1>
                            <p className="text-blue-100">
                                {etudiant.filiere} - Année {etudiant.annee} • Code: {etudiant.code}
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-sm text-blue-100 mb-1">Moyenne Générale</div>
                            <div className="text-4xl font-bold">{etudiant.moyenne}/20</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Profil et Risque */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                    {/* Carte Profil */}
                    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                        <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${getProfilColor(etudiant.profil)} flex items-center justify-center text-3xl mb-4`}>
                            {getProfilIcon(etudiant.profil)}
                        </div>
                        <h3 className="text-sm font-semibold text-gray-500 mb-2">Votre Profil</h3>
                        <p className="text-2xl font-bold text-gray-900 mb-1">{etudiant.profil}</p>
                        <p className="text-sm text-gray-600">Basé sur vos performances</p>
                    </div>

                    {/* Carte Niveau de Risque */}
                    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center mb-4">
                            <AlertTriangle className="w-8 h-8 text-white" />
                        </div>
                        <h3 className="text-sm font-semibold text-gray-500 mb-2">Niveau de Risque</h3>
                        <p className="text-2xl font-bold text-red-600 mb-1">{etudiant.risque}%</p>
                        <p className="text-sm text-gray-600">Prédiction IA</p>
                    </div>

                    {/* Carte Modules */}
                    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mb-4">
                            <BookOpen className="w-8 h-8 text-white" />
                        </div>
                        <h3 className="text-sm font-semibold text-gray-500 mb-2">Modules</h3>
                        <p className="text-2xl font-bold text-gray-900 mb-1">{etudiant.modules_reussis}/{etudiant.modules_total}</p>
                        <p className="text-sm text-gray-600">{etudiant.modules_echoues} échecs</p>
                    </div>
                </div>

                {/* Recommandations */}
                <div className="bg-gradient-to-br from-amber-50 to-orange-50 border-l-4 border-orange-500 rounded-xl p-6 mb-8">
                    <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center flex-shrink-0">
                            <Target className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-bold text-gray-900 mb-3">
                                💡 Recommandations pour Vous
                            </h3>
                            <ul className="space-y-2">
                                {etudiant.recommandations.map((reco: string, idx: number) => (
                                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                                        <ChevronRight className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                                        <span>{reco}</span>
                                    </li>
                                ))}
                            </ul>
                            <button className="mt-4 px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg font-semibold text-sm hover:shadow-lg transition-all">
                                Prendre rendez-vous avec un tuteur
                            </button>
                        </div>
                    </div>
                </div>

                {/* Actions Rapides */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <button className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-200 border border-gray-100 text-left group">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <MessageSquare className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="font-bold text-gray-900 mb-1">Assistant IA</h3>
                        <p className="text-sm text-gray-600">Posez vos questions</p>
                    </button>

                    <button className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-200 border border-gray-100 text-left group">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <Brain className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="font-bold text-gray-900 mb-1">Modules Futurs</h3>
                        <p className="text-sm text-gray-600">Recommandés pour vous</p>
                    </button>

                    <button className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-200 border border-gray-100 text-left group">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <BarChart3 className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="font-bold text-gray-900 mb-1">Mes Notes</h3>
                        <p className="text-sm text-gray-600">Voir détails</p>
                    </button>

                    <button className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-all duration-200 border border-gray-100 text-left group">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                            <Calendar className="w-6 h-6 text-white" />
                        </div>
                        <h3 className="font-bold text-gray-900 mb-1">Planning</h3>
                        <p className="text-sm text-gray-600">Séances de soutien</p>
                    </button>
                </div>

                {/* Progression */}
                <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
                    <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-blue-600" />
                        Votre Progression
                    </h3>

                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="font-semibold text-gray-700">Modules Réussis</span>
                                <span className="font-bold text-gray-900">{Math.round((etudiant.modules_reussis / etudiant.modules_total) * 100)}%</span>
                            </div>
                            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full transition-all duration-1000"
                                    style={{ width: `${(etudiant.modules_reussis / etudiant.modules_total) * 100}%` }}
                                ></div>
                            </div>
                        </div>

                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="font-semibold text-gray-700">Performance Globale</span>
                                <span className="font-bold text-gray-900">{(etudiant.moyenne / 20 * 100).toFixed(0)}%</span>
                            </div>
                            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-1000"
                                    style={{ width: `${etudiant.moyenne / 20 * 100}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-6 pt-6 border-t border-gray-200">
                        <p className="text-sm text-gray-600 mb-4">
                            <strong className="text-gray-900">Conseil :</strong> Votre niveau de risque est élevé.
                            Nous vous recommandons fortement de prendre rendez-vous avec un tuteur cette semaine.
                        </p>
                        <button className="text-sm text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1">
                            Voir mon historique complet
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
