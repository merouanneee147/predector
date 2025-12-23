"use client";

import { useState, useEffect } from 'react';
import { Mail, Send, Users, User, Calendar, Loader2, CheckCircle, AlertTriangle } from 'lucide-react';
import { getFilieres, sendAlerteEtudiant, sendAlerteModule, sendRapportHebdo } from '@/lib/api';
import { PageHeader } from '@/components/ui';

export default function AlertesPage() {
  const [filieres, setFilieres] = useState<string[]>([]);
  const [loading, setLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // États des formulaires
  const [etudiantCode, setEtudiantCode] = useState('');
  const [etudiantEmail, setEtudiantEmail] = useState('');
  const [moduleCode, setModuleCode] = useState('');
  const [moduleEmails, setModuleEmails] = useState('');
  const [adminEmail, setAdminEmail] = useState('');

  useEffect(() => {
    getFilieres().then(setFilieres).catch(console.error);
  }, []);

  const handleAlerteEtudiant = async () => {
    if (!etudiantCode || !etudiantEmail) {
      setMessage({ type: 'error', text: 'Veuillez remplir tous les champs' });
      return;
    }
    setLoading('etudiant');
    setMessage(null);
    try {
      await sendAlerteEtudiant(etudiantCode, etudiantEmail);
      setMessage({ type: 'success', text: `Alerte envoyée pour l'étudiant ${etudiantCode}!` });
      setEtudiantCode('');
      setEtudiantEmail('');
    } catch (error) {
      console.error(error);
      setMessage({ type: 'error', text: "Erreur lors de l'envoi de l'alerte étudiant" });
    } finally {
      setLoading(null);
    }
  };

  const handleAlerteModule = async () => {
    if (!moduleCode || !moduleEmails) {
      setMessage({ type: 'error', text: 'Veuillez remplir tous les champs' });
      return;
    }
    setLoading('module');
    setMessage(null);
    try {
      const emails = moduleEmails.split(',').map(e => e.trim()).filter(e => e);
      await sendAlerteModule(moduleCode, emails);
      setMessage({ type: 'success', text: `Alerte envoyée pour le module ${moduleCode}!` });
      setModuleCode('');
      setModuleEmails('');
    } catch (error) {
      console.error(error);
      setMessage({ type: 'error', text: "Erreur lors de l'envoi de l'alerte module" });
    } finally {
      setLoading(null);
    }
  };

  const handleRapportHebdo = async () => {
    if (!adminEmail) {
      setMessage({ type: 'error', text: 'Veuillez entrer une adresse email' });
      return;
    }
    setLoading('hebdo');
    setMessage(null);
    try {
      await sendRapportHebdo(adminEmail);
      setMessage({ type: 'success', text: 'Rapport hebdomadaire envoyé!' });
      setAdminEmail('');
    } catch (error) {
      console.error(error);
      setMessage({ type: 'error', text: "Erreur lors de l'envoi du rapport hebdomadaire" });
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Alertes Email"
        description="Envoyez des notifications et alertes aux étudiants et responsables"
      />

      {/* Message */}
      {message && (
        <div className={`p-4 rounded-lg flex items-center gap-3 ${
          message.type === 'success' 
            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
            : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          )}
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Alerte Étudiant */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <User className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800">Alerte Étudiant</h3>
              <p className="text-sm text-slate-500">Notification individuelle</p>
            </div>
          </div>

          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Code Étudiant
              </label>
              <input
                type="text"
                value={etudiantCode}
                onChange={(e) => setEtudiantCode(e.target.value)}
                placeholder="Ex: ETU001"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={etudiantEmail}
                onChange={(e) => setEtudiantEmail(e.target.value)}
                placeholder="etudiant@email.com"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
          </div>

          <button
            onClick={handleAlerteEtudiant}
            disabled={loading === 'etudiant'}
            className="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {loading === 'etudiant' ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Envoi...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Envoyer Alerte
              </>
            )}
          </button>
        </div>

        {/* Alerte Module */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800">Alerte Module</h3>
              <p className="text-sm text-slate-500">Notification groupée</p>
            </div>
          </div>

          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Code Module
              </label>
              <input
                type="text"
                value={moduleCode}
                onChange={(e) => setModuleCode(e.target.value)}
                placeholder="Ex: MATH101"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Emails (séparés par virgule)
              </label>
              <textarea
                value={moduleEmails}
                onChange={(e) => setModuleEmails(e.target.value)}
                placeholder="prof1@univ.ma, prof2@univ.ma"
                rows={2}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 outline-none resize-none"
              />
            </div>
          </div>

          <button
            onClick={handleAlerteModule}
            disabled={loading === 'module'}
            className="w-full py-3 bg-amber-600 text-white font-medium rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {loading === 'module' ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Envoi...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Envoyer Alertes
              </>
            )}
          </button>
        </div>

        {/* Rapport Hebdomadaire */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 bg-violet-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-violet-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800">Rapport Hebdo</h3>
              <p className="text-sm text-slate-500">Synthèse administrative</p>
            </div>
          </div>

          <div className="space-y-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Email Administrateur
              </label>
              <input
                type="email"
                value={adminEmail}
                onChange={(e) => setAdminEmail(e.target.value)}
                placeholder="admin@universite.ma"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none"
              />
            </div>
            <p className="text-sm text-slate-500">
              Envoie un résumé hebdomadaire des étudiants à risque, statistiques et alertes.
            </p>
          </div>

          <button
            onClick={handleRapportHebdo}
            disabled={loading === 'hebdo'}
            className="w-full py-3 bg-violet-600 text-white font-medium rounded-lg hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {loading === 'hebdo' ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Envoi...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Envoyer Rapport
              </>
            )}
          </button>
        </div>
      </div>

      {/* Info */}
      <div className="bg-slate-50 rounded-xl border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <Mail className="w-5 h-5 text-slate-600" />
          Types d'alertes disponibles
        </h3>
        <ul className="space-y-2 text-slate-600">
          <li className="flex items-start gap-2">
            <span className="text-blue-500">•</span>
            <span><strong>Alerte Étudiant:</strong> Notification personnalisée avec profil de risque et recommandations</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-500">•</span>
            <span><strong>Alerte Module:</strong> Rapport sur les étudiants en difficulté pour un module spécifique</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-violet-500">•</span>
            <span><strong>Rapport Hebdomadaire:</strong> Synthèse complète pour l'administration</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
