"use client";

import { useState, useEffect } from 'react';
import { FileText, Download, Building2, Users, User, Loader2 } from 'lucide-react';
import { getFilieres, generateRapportGlobal, generateRapportFiliere, generateRapportEtudiant } from '@/lib/api';
import { PageHeader } from '@/components/ui';

export default function RapportsPage() {
  const [filieres, setFilieres] = useState<string[]>([]);
  const [selectedFiliere, setSelectedFiliere] = useState('');
  const [codeEtudiant, setCodeEtudiant] = useState('');
  const [loading, setLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    getFilieres().then(setFilieres).catch(console.error);
  }, []);

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const handleGenerateGlobal = async () => {
    setLoading('global');
    setMessage(null);
    try {
      const blob = await generateRapportGlobal();
      downloadBlob(blob, 'rapport_global_administration.pdf');
      setMessage({ type: 'success', text: 'Rapport global téléchargé avec succès!' });
    } catch (error) {
      console.error(error);
      setMessage({ type: 'error', text: 'Erreur lors de la génération du rapport global' });
    } finally {
      setLoading(null);
    }
  };

  const handleGenerateFiliere = async () => {
    if (!selectedFiliere) {
      setMessage({ type: 'error', text: 'Veuillez sélectionner une filière' });
      return;
    }
    setLoading('filiere');
    setMessage(null);
    try {
      const blob = await generateRapportFiliere(selectedFiliere);
      downloadBlob(blob, `rapport_filiere_${selectedFiliere}.pdf`);
      setMessage({ type: 'success', text: `Rapport de la filière ${selectedFiliere} téléchargé!` });
    } catch (error) {
      console.error(error);
      setMessage({ type: 'error', text: 'Erreur lors de la génération du rapport filière' });
    } finally {
      setLoading(null);
    }
  };

  const handleGenerateEtudiant = async () => {
    if (!codeEtudiant) {
      setMessage({ type: 'error', text: 'Veuillez entrer un code étudiant' });
      return;
    }
    setLoading('etudiant');
    setMessage(null);
    try {
      const blob = await generateRapportEtudiant(codeEtudiant);
      downloadBlob(blob, `rapport_etudiant_${codeEtudiant}.pdf`);
      setMessage({ type: 'success', text: `Rapport de l'étudiant ${codeEtudiant} téléchargé!` });
    } catch (error) {
      console.error(error);
      setMessage({ type: 'error', text: 'Étudiant non trouvé ou erreur de génération' });
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Génération de Rapports PDF"
        description="Créez des rapports détaillés pour l'administration, les filières ou les étudiants"
      />

      {/* Message */}
      {message && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success' 
            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
            : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Rapport Global */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Building2 className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800">Rapport Global</h3>
              <p className="text-sm text-slate-500">Administration générale</p>
            </div>
          </div>
          <p className="text-slate-600 mb-6">
            Rapport complet incluant toutes les statistiques, les analyses par filière et la liste des étudiants à risque.
          </p>
          <button
            onClick={handleGenerateGlobal}
            disabled={loading === 'global'}
            className="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {loading === 'global' ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Génération...
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                Télécharger
              </>
            )}
          </button>
        </div>

        {/* Rapport Filière */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800">Rapport Filière</h3>
              <p className="text-sm text-slate-500">Par département</p>
            </div>
          </div>
          <div className="mb-4">
            <select
              value={selectedFiliere}
              onChange={(e) => setSelectedFiliere(e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none appearance-none bg-white cursor-pointer"
            >
              <option value="">Sélectionnez une filière</option>
              {filieres.map((f) => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
          </div>
          <p className="text-slate-600 mb-6 text-sm">
            Statistiques détaillées et étudiants à risque pour la filière sélectionnée.
          </p>
          <button
            onClick={handleGenerateFiliere}
            disabled={loading === 'filiere' || !selectedFiliere}
            className="w-full py-3 bg-emerald-600 text-white font-medium rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {loading === 'filiere' ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Génération...
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                Télécharger
              </>
            )}
          </button>
        </div>

        {/* Rapport Étudiant */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-violet-100 rounded-lg flex items-center justify-center">
              <User className="w-6 h-6 text-violet-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800">Rapport Étudiant</h3>
              <p className="text-sm text-slate-500">Profil individuel</p>
            </div>
          </div>
          <div className="mb-4">
            <input
              type="text"
              value={codeEtudiant}
              onChange={(e) => setCodeEtudiant(e.target.value)}
              placeholder="Code étudiant"
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none"
            />
          </div>
          <p className="text-slate-600 mb-6 text-sm">
            Fiche complète de l'étudiant avec notes, profil et recommandations.
          </p>
          <button
            onClick={handleGenerateEtudiant}
            disabled={loading === 'etudiant' || !codeEtudiant}
            className="w-full py-3 bg-violet-600 text-white font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {loading === 'etudiant' ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Génération...
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                Télécharger
              </>
            )}
          </button>
        </div>
      </div>

      {/* Info */}
      <div className="bg-slate-50 rounded-xl border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <FileText className="w-5 h-5 text-slate-600" />
          À propos des rapports
        </h3>
        <ul className="space-y-2 text-slate-600">
          <li className="flex items-start gap-2">
            <span className="text-blue-500">•</span>
            <span><strong>Rapport Global:</strong> Vue d'ensemble complète pour l'administration universitaire</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-emerald-500">•</span>
            <span><strong>Rapport Filière:</strong> Analyse détaillée des performances par département</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-violet-500">•</span>
            <span><strong>Rapport Étudiant:</strong> Fiche individuelle avec recommandations personnalisées</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
