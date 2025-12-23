"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AlertTriangle, Mail, FileText } from 'lucide-react';
import { getEtudiantsRisque, getProfilName, Etudiant } from '@/lib/api';
import { LoadingSpinner, Badge, getProfilVariant, PageHeader, EmptyState } from '@/components/ui';

export default function RisquePage() {
  const [etudiants, setEtudiants] = useState<Etudiant[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getEtudiantsRisque();
        setEtudiants(data);
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <LoadingSpinner size="lg" text="Chargement des étudiants à risque..." />;
  }

  const getRiskLevel = (prob: number) => {
    if (prob >= 0.8) return { label: 'Critique', color: 'text-red-700 bg-red-100' };
    if (prob >= 0.6) return { label: 'Élevé', color: 'text-orange-700 bg-orange-100' };
    if (prob >= 0.4) return { label: 'Modéré', color: 'text-amber-700 bg-amber-100' };
    return { label: 'Faible', color: 'text-yellow-700 bg-yellow-100' };
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Étudiants à Risque"
        description={`${etudiants.length} étudiants nécessitent une attention particulière`}
        action={
          <div className="flex gap-3">
            <Link
              href="/alertes"
              className="px-4 py-2 bg-amber-500 text-white font-medium rounded-lg hover:bg-amber-600 transition-colors flex items-center gap-2"
            >
              <Mail className="w-4 h-4" />
              Envoyer Alertes
            </Link>
            <Link
              href="/rapports"
              className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Générer Rapport
            </Link>
          </div>
        }
      />

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-red-50 rounded-xl border border-red-200 p-4">
          <p className="text-sm text-red-600 font-medium">Risque Critique</p>
          <p className="text-2xl font-bold text-red-700">
            {etudiants.filter(e => (e.score_risque || 0) >= 0.8).length}
          </p>
        </div>
        <div className="bg-orange-50 rounded-xl border border-orange-200 p-4">
          <p className="text-sm text-orange-600 font-medium">Risque Élevé</p>
          <p className="text-2xl font-bold text-orange-700">
            {etudiants.filter(e => (e.score_risque || 0) >= 0.6 && (e.score_risque || 0) < 0.8).length}
          </p>
        </div>
        <div className="bg-amber-50 rounded-xl border border-amber-200 p-4">
          <p className="text-sm text-amber-600 font-medium">Risque Modéré</p>
          <p className="text-2xl font-bold text-amber-700">
            {etudiants.filter(e => (e.score_risque || 0) >= 0.4 && (e.score_risque || 0) < 0.6).length}
          </p>
        </div>
        <div className="bg-yellow-50 rounded-xl border border-yellow-200 p-4">
          <p className="text-sm text-yellow-600 font-medium">Risque Faible</p>
          <p className="text-2xl font-bold text-yellow-700">
            {etudiants.filter(e => (e.score_risque || 0) < 0.4).length}
          </p>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {etudiants.length === 0 ? (
          <EmptyState 
            icon={AlertTriangle}
            title="Aucun étudiant à risque"
            description="Tous les étudiants ont un profil stable"
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left py-4 px-6 font-semibold text-slate-600">Code</th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-600">Filière</th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-600">Modules</th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-600">Moyenne</th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-600">Profil</th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-600">Probabilité</th>
                  <th className="text-left py-4 px-6 font-semibold text-slate-600">Niveau</th>
                </tr>
              </thead>
              <tbody>
                {etudiants.map((etudiant) => {
                  const risk = getRiskLevel(etudiant.score_risque || 0);
                  return (
                    <tr 
                      key={etudiant.id}
                      className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
                    >
                      <td className="py-4 px-6">
                        <Link 
                          href={`/etudiants/${etudiant.id}`}
                          className="text-blue-600 hover:underline font-medium"
                        >
                          {etudiant.id}
                        </Link>
                      </td>
                      <td className="py-4 px-6 text-slate-600">{etudiant.filiere}</td>
                      <td className="py-4 px-6 text-slate-600">{etudiant.nb_modules}</td>
                      <td className="py-4 px-6">
                        <span className={`font-medium ${
                          etudiant.moyenne < 10 ? 'text-red-600' : 'text-slate-700'
                        }`}>
                          {etudiant.moyenne?.toFixed(2)}/20
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <Badge variant={getProfilVariant(getProfilName(etudiant.profil))}>
                          {getProfilName(etudiant.profil)}
                        </Badge>
                      </td>
                      <td className="py-4 px-6">
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-slate-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                (etudiant.score_risque || 0) >= 0.8 ? 'bg-red-500' :
                                (etudiant.score_risque || 0) >= 0.6 ? 'bg-orange-500' :
                                (etudiant.score_risque || 0) >= 0.4 ? 'bg-amber-500' : 'bg-yellow-500'
                              }`}
                              style={{ width: `${(etudiant.score_risque || 0) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium text-slate-600">
                            {((etudiant.score_risque || 0) * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${risk.color}`}>
                          {risk.label}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
