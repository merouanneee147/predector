"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  User,
  BookOpen,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Lightbulb
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { getEtudiant, EtudiantDetail, getProfilName } from '@/lib/api';
import { LoadingSpinner, Badge, getProfilVariant, PageHeader } from '@/components/ui';

export default function EtudiantDetailPage() {
  const params = useParams();
  const code = params.id as string;
  const [etudiant, setEtudiant] = useState<EtudiantDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEtudiant = async () => {
      try {
        const data = await getEtudiant(code);
        setEtudiant(data);
      } catch (err) {
        setError('Étudiant non trouvé');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    if (code) fetchEtudiant();
  }, [code]);

  if (loading) {
    return <LoadingSpinner size="lg" text="Chargement du profil..." />;
  }

  if (error || !etudiant) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-16 h-16 mx-auto text-amber-500 mb-4" />
        <h2 className="text-xl font-semibold text-slate-700">{error}</h2>
        <Link
          href="/etudiants"
          className="text-blue-600 hover:underline mt-4 inline-block"
        >
          Retour à la liste
        </Link>
      </div>
    );
  }

  const chartData = etudiant.modules?.map(m => ({
    module: m.Code_Module,
    note: m.Note,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        href="/etudiants"
        className="inline-flex items-center gap-2 text-slate-600 hover:text-blue-600 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Retour à la liste
      </Link>

      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">{etudiant.Code}</h1>
              <p className="text-slate-500">Filière: {etudiant.Filiere}</p>
            </div>
          </div>
          <div className="text-right">
            <Badge variant={getProfilVariant(getProfilName(etudiant.profil || ''))} size="md">
              {getProfilName(etudiant.profil) || 'Non défini'}
            </Badge>
            {etudiant.risque && (
              <div className="mt-2">
                <Badge variant="risque" size="sm">
                  Risque: {((etudiant.probabilite_risque || 0) * 100).toFixed(0)}%
                </Badge>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Moyenne Générale</p>
              <p className={`text-xl font-bold ${etudiant.Moyenne < 10 ? 'text-red-600' :
                etudiant.Moyenne >= 14 ? 'text-emerald-600' : 'text-slate-800'
                }`}>
                {etudiant.Moyenne?.toFixed(2)}/20
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-100 rounded-lg">
              <BookOpen className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Modules Inscrits</p>
              <p className="text-xl font-bold text-slate-800">{etudiant.nb_modules}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-100 rounded-lg">
              <CheckCircle className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Total Points</p>
              <p className="text-xl font-bold text-slate-800">{etudiant.Total?.toFixed(0)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${etudiant.risque ? 'bg-red-100' : 'bg-emerald-100'}`}>
              <AlertTriangle className={`w-5 h-5 ${etudiant.risque ? 'text-red-600' : 'text-emerald-600'}`} />
            </div>
            <div>
              <p className="text-sm text-slate-500">Statut</p>
              <p className={`text-xl font-bold ${etudiant.risque ? 'text-red-600' : 'text-emerald-600'}`}>
                {etudiant.risque ? 'À Risque' : 'Stable'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Notes par module */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Notes par Module</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis
                dataKey="module"
                stroke="#64748B"
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={12}
              />
              <YAxis stroke="#64748B" domain={[0, 20]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E2E8F0',
                  borderRadius: '8px'
                }}
              />
              <ReferenceLine y={10} stroke="#EF4444" strokeDasharray="5 5" label="Seuil" />
              <Bar
                dataKey="note"
                fill="#3B82F6"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recommandations */}
      {etudiant.recommandations && etudiant.recommandations.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-amber-500" />
            Recommandations Personnalisées
          </h2>
          <ul className="space-y-3">
            {etudiant.recommandations.map((rec, index) => (
              <li
                key={index}
                className="flex items-start gap-3 p-4 bg-slate-50 rounded-lg border border-slate-200"
              >
                <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                <span className="text-slate-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Liste des modules */}
      {etudiant.modules && etudiant.modules.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Détail des Modules</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="text-left py-3 px-4 font-semibold text-slate-600">Module</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-600">Année</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-600">Semestre</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-600">Note</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-600">Statut</th>
                </tr>
              </thead>
              <tbody>
                {etudiant.modules.map((module, index) => (
                  <tr key={index} className="border-b border-slate-100">
                    <td className="py-3 px-4 font-medium text-slate-700">{module.Code_Module}</td>
                    <td className="py-3 px-4 text-slate-600">{module.Annee}</td>
                    <td className="py-3 px-4 text-slate-600">S{module.Semestre}</td>
                    <td className="py-3 px-4">
                      <span className={`font-medium ${module.Note < 10 ? 'text-red-600' :
                        module.Note >= 14 ? 'text-emerald-600' : 'text-slate-700'
                        }`}>
                        {module.Note.toFixed(2)}/20
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      {module.Note >= 10 ? (
                        <Badge variant="regulier" size="sm">Validé</Badge>
                      ) : (
                        <Badge variant="risque" size="sm">Non Validé</Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
