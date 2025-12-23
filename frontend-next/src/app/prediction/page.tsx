"use client";

import { useState, useEffect } from 'react';
import { 
  Brain, 
  Plus, 
  Trash2, 
  AlertTriangle, 
  CheckCircle,
  Lightbulb,
  Send
} from 'lucide-react';
import { predict, getFilieres, Prediction } from '@/lib/api';
import { LoadingSpinner, Badge, getProfilVariant, PageHeader } from '@/components/ui';

interface ModuleInput {
  code: string;
  note: number;
}

export default function PredictionPage() {
  const [filieres, setFilieres] = useState<string[]>([]);
  const [filiere, setFiliere] = useState('');
  const [codeEtudiant, setCodeEtudiant] = useState('');
  const [modules, setModules] = useState<ModuleInput[]>([{ code: '', note: 0 }]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Prediction | null>(null);

  useEffect(() => {
    getFilieres().then(setFilieres).catch(console.error);
  }, []);

  const addModule = () => {
    setModules([...modules, { code: '', note: 0 }]);
  };

  const removeModule = (index: number) => {
    if (modules.length > 1) {
      setModules(modules.filter((_, i) => i !== index));
    }
  };

  const updateModule = (index: number, field: 'code' | 'note', value: string | number) => {
    const newModules = [...modules];
    newModules[index] = { ...newModules[index], [field]: value };
    setModules(newModules);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!filiere || modules.some(m => !m.code)) {
      alert('Veuillez remplir tous les champs requis');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const prediction = await predict({
        code_etudiant: codeEtudiant || undefined,
        filiere,
        modules: modules.filter(m => m.code),
      });
      setResult(prediction);
    } catch (error) {
      console.error('Erreur de prédiction:', error);
      alert('Erreur lors de la prédiction. Vérifiez les données saisies.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Nouvelle Prédiction"
        description="Évaluez le risque d'échec pour un étudiant"
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Formulaire */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Code étudiant (optionnel) */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Code Étudiant (optionnel)
              </label>
              <input
                type="text"
                value={codeEtudiant}
                onChange={(e) => setCodeEtudiant(e.target.value)}
                placeholder="Ex: ETU001"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>

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

            {/* Modules */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-slate-700">
                  Modules et Notes *
                </label>
                <button
                  type="button"
                  onClick={addModule}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
                >
                  <Plus className="w-4 h-4" /> Ajouter
                </button>
              </div>

              <div className="space-y-3">
                {modules.map((module, index) => (
                  <div key={index} className="flex gap-3">
                    <input
                      type="text"
                      value={module.code}
                      onChange={(e) => updateModule(index, 'code', e.target.value)}
                      placeholder="Code module"
                      required
                      className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    />
                    <input
                      type="number"
                      value={module.note}
                      onChange={(e) => updateModule(index, 'note', parseFloat(e.target.value) || 0)}
                      min="0"
                      max="20"
                      step="0.25"
                      required
                      className="w-24 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    />
                    {modules.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeModule(index)}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    )}
                  </div>
                ))}
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
                  Analyse en cours...
                </>
              ) : (
                <>
                  <Brain className="w-5 h-5" />
                  Lancer la Prédiction
                </>
              )}
            </button>
          </form>
        </div>

        {/* Résultats */}
        <div className="space-y-6">
          {loading && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <LoadingSpinner text="Analyse en cours avec le modèle ML..." />
            </div>
          )}

          {result && (
            <>
              {/* Score de risque */}
              <div className={`rounded-xl shadow-sm border p-6 ${
                result.risque 
                  ? 'bg-gradient-to-r from-red-50 to-orange-50 border-red-200' 
                  : 'bg-gradient-to-r from-emerald-50 to-green-50 border-emerald-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {result.risque ? (
                      <div className="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center">
                        <AlertTriangle className="w-7 h-7 text-red-600" />
                      </div>
                    ) : (
                      <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-7 h-7 text-emerald-600" />
                      </div>
                    )}
                    <div>
                      <h3 className={`text-lg font-bold ${result.risque ? 'text-red-700' : 'text-emerald-700'}`}>
                        {result.risque ? 'Risque Détecté' : 'Profil Stable'}
                      </h3>
                      <p className="text-slate-600">
                        Probabilité de risque: <span className="font-bold">{(result.probabilite * 100).toFixed(1)}%</span>
                      </p>
                    </div>
                  </div>
                  <Badge variant={getProfilVariant(result.profil)} size="md">
                    {result.profil}
                  </Badge>
                </div>
              </div>

              {/* Recommandations */}
              {result.recommandations && result.recommandations.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                  <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-amber-500" />
                    Recommandations
                  </h3>
                  <ul className="space-y-3">
                    {result.recommandations.map((rec, index) => (
                      <li 
                        key={index}
                        className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg"
                      >
                        <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                        <span className="text-slate-700">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Modules similaires */}
              {result.modules_similaires && result.modules_similaires.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">
                    Modules Recommandés (Étudiants Similaires)
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {result.modules_similaires.map((module, index) => (
                      <span 
                        key={index}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                      >
                        {module}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {!loading && !result && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="text-center py-8">
                <Brain className="w-16 h-16 mx-auto text-slate-300 mb-4" />
                <h3 className="text-lg font-semibold text-slate-700">Prêt pour l'analyse</h3>
                <p className="text-slate-500 mt-1">
                  Remplissez le formulaire et lancez la prédiction
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
