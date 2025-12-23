"use client";

import { useState, useEffect } from 'react';
import { 
  Brain, 
  Upload,
  Download,
  AlertTriangle, 
  CheckCircle,
  FileSpreadsheet,
  Lightbulb,
  TrendingUp
} from 'lucide-react';
import { getFilieres } from '@/lib/api';
import { LoadingSpinner, Badge, getProfilVariant, PageHeader } from '@/components/ui';

interface EtudiantPrediction {
  id: string;
  nom?: string;
  filiere: string;
  risque: boolean;
  probabilite: number;
  profil: string;
  recommandations: string[];
}

export default function PredictionAvanceePage() {
  const [filieres, setFilieres] = useState<string[]>([]);
  const [filiere, setFiliere] = useState('');
  const [fichierCSV, setFichierCSV] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [resultats, setResultats] = useState<EtudiantPrediction[]>([]);
  const [statistiques, setStatistiques] = useState<{
    total: number;
    risque: number;
    stable: number;
    tauxRisque: number;
  } | null>(null);

  useEffect(() => {
    getFilieres().then(setFilieres).catch(console.error);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFichierCSV(e.target.files[0]);
      setResultats([]);
      setStatistiques(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!fichierCSV || !filiere) {
      alert('Veuillez sélectionner une filière et un fichier CSV');
      return;
    }

    setLoading(true);
    setResultats([]);
    setStatistiques(null);

    try {
      // Simulation de traitement - À remplacer par un vrai appel API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Données simulées pour démonstration
      const mockResults: EtudiantPrediction[] = [
        {
          id: 'ETU001',
          nom: 'Ahmed Benali',
          filiere: filiere,
          risque: true,
          probabilite: 0.78,
          profil: 'En_Difficulté',
          recommandations: [
            'Tutorat intensif recommandé',
            'Suivi personnalisé hebdomadaire',
            'Révision des fondamentaux'
          ]
        },
        {
          id: 'ETU002',
          nom: 'Fatima Zahra',
          filiere: filiere,
          risque: false,
          probabilite: 0.15,
          profil: 'Excellence',
          recommandations: [
            'Continuer sur cette lancée',
            'Proposer des projets avancés'
          ]
        },
        {
          id: 'ETU003',
          nom: 'Mohammed Alami',
          filiere: filiere,
          risque: true,
          probabilite: 0.65,
          profil: 'En_Progression',
          recommandations: [
            'Accompagnement ciblé',
            'Sessions de groupe recommandées'
          ]
        }
      ];

      setResultats(mockResults);
      
      const totalRisque = mockResults.filter(r => r.risque).length;
      setStatistiques({
        total: mockResults.length,
        risque: totalRisque,
        stable: mockResults.length - totalRisque,
        tauxRisque: (totalRisque / mockResults.length) * 100
      });
    } catch (error) {
      console.error('Erreur de prédiction:', error);
      alert('Erreur lors du traitement du fichier');
    } finally {
      setLoading(false);
    }
  };

  const exporterResultats = () => {
    if (resultats.length === 0) return;

    const csvContent = [
      ['ID Étudiant', 'Nom', 'Filière', 'Risque', 'Probabilité (%)', 'Profil', 'Recommandations'],
      ...resultats.map(r => [
        r.id,
        r.nom || '',
        r.filiere,
        r.risque ? 'OUI' : 'NON',
        (r.probabilite * 100).toFixed(1),
        r.profil,
        r.recommandations.join(' | ')
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `predictions_${filiere}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Prédiction Avancée (Batch)"
        description="Analysez plusieurs étudiants simultanément via fichier CSV"
      />

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-1">Format du fichier CSV attendu:</p>
            <code className="bg-blue-100 px-2 py-1 rounded text-xs">
              code_etudiant,nom,module1_note,module2_note,...
            </code>
            <p className="mt-2 text-blue-700">
              Le système analysera automatiquement tous les étudiants et générera des recommandations personnalisées.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Formulaire */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Filière */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Filière *
                </label>
                <select
                  value={filiere}
                  onChange={(e) => setFiliere(e.target.value)}
                  required
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none bg-white cursor-pointer"
                >
                  <option value="">Sélectionnez une filière</option>
                  {filieres.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>

              {/* Upload CSV */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Fichier CSV *
                </label>
                <div className="mt-1">
                  <label className="flex items-center justify-center w-full px-4 py-6 border-2 border-dashed border-slate-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
                    <div className="text-center">
                      <Upload className="w-8 h-8 mx-auto text-slate-400 mb-2" />
                      <span className="text-sm text-slate-600">
                        {fichierCSV ? fichierCSV.name : 'Sélectionner un fichier'}
                      </span>
                      <p className="text-xs text-slate-400 mt-1">CSV uniquement</p>
                    </div>
                    <input
                      type="file"
                      accept=".csv"
                      onChange={handleFileChange}
                      className="hidden"
                      required
                    />
                  </label>
                </div>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Traitement...
                  </>
                ) : (
                  <>
                    <Brain className="w-5 h-5" />
                    Analyser le Fichier
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
              <LoadingSpinner text="Analyse en cours avec le modèle ML..." />
            </div>
          )}

          {/* Statistiques */}
          {statistiques && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
                <div className="text-3xl font-bold text-blue-600">{statistiques.total}</div>
                <div className="text-sm text-slate-600 mt-1">Total Étudiants</div>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-red-200 p-4 bg-red-50">
                <div className="text-3xl font-bold text-red-600">{statistiques.risque}</div>
                <div className="text-sm text-slate-600 mt-1">À Risque</div>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-emerald-200 p-4 bg-emerald-50">
                <div className="text-3xl font-bold text-emerald-600">{statistiques.stable}</div>
                <div className="text-sm text-slate-600 mt-1">Stables</div>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-amber-200 p-4 bg-amber-50">
                <div className="text-3xl font-bold text-amber-600">
                  {statistiques.tauxRisque.toFixed(0)}%
                </div>
                <div className="text-sm text-slate-600 mt-1">Taux de Risque</div>
              </div>
            </div>
          )}

          {/* Liste des résultats */}
          {resultats.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200">
              <div className="p-6 border-b border-slate-200 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-800">
                  Résultats de l'Analyse
                </h3>
                <button
                  onClick={exporterResultats}
                  className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
                >
                  <Download className="w-4 h-4" />
                  Exporter CSV
                </button>
              </div>

              <div className="divide-y divide-slate-200">
                {resultats.map((resultat, index) => (
                  <div key={index} className="p-6 hover:bg-slate-50 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {resultat.risque ? (
                          <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <AlertTriangle className="w-5 h-5 text-red-600" />
                          </div>
                        ) : (
                          <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <CheckCircle className="w-5 h-5 text-emerald-600" />
                          </div>
                        )}
                        <div>
                          <div className="font-semibold text-slate-800">
                            {resultat.nom || resultat.id}
                          </div>
                          <div className="text-sm text-slate-500">{resultat.id}</div>
                        </div>
                      </div>
                      <Badge variant={getProfilVariant(resultat.profil)} size="sm">
                        {resultat.profil}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-4 mb-3">
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${
                            resultat.risque ? 'bg-red-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${resultat.probabilite * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-slate-700">
                        {(resultat.probabilite * 100).toFixed(1)}%
                      </span>
                    </div>

                    {resultat.recommandations.length > 0 && (
                      <div className="mt-3">
                        <div className="text-xs font-medium text-slate-500 mb-2">
                          Recommandations:
                        </div>
                        <ul className="space-y-1">
                          {resultat.recommandations.slice(0, 2).map((rec, i) => (
                            <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                              <TrendingUp className="w-3 h-3 text-blue-500 flex-shrink-0 mt-1" />
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {!loading && resultats.length === 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="text-center py-8">
                <FileSpreadsheet className="w-16 h-16 mx-auto text-slate-300 mb-4" />
                <h3 className="text-lg font-semibold text-slate-700">Prêt pour l'analyse</h3>
                <p className="text-slate-500 mt-1">
                  Chargez un fichier CSV pour commencer l'analyse batch
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
