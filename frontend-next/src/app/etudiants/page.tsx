"use client";

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { Search, Filter, ChevronLeft, ChevronRight, Users } from 'lucide-react';
import { getEtudiants, getFilieres, getProfilName, Etudiant } from '@/lib/api';
import { LoadingSpinner, Badge, getProfilVariant, PageHeader, EmptyState } from '@/components/ui';

export default function EtudiantsPage() {
  const [etudiants, setEtudiants] = useState<Etudiant[]>([]);
  const [filieres, setFilieres] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filiere, setFiliere] = useState('');
  const limit = 20;

  const fetchEtudiants = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getEtudiants({ page, limit, filiere, search });
      setEtudiants(data.etudiants);
      setTotal(data.total);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  }, [page, filiere, search]);

  useEffect(() => {
    fetchEtudiants();
  }, [fetchEtudiants]);

  useEffect(() => {
    getFilieres().then(setFilieres).catch(console.error);
  }, []);

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Gestion des Étudiants"
        description={`${total.toLocaleString()} étudiants enregistrés`}
      />

      {/* Filtres */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
        <div className="flex flex-wrap gap-4">
          {/* Recherche */}
          <div className="flex-1 min-w-[250px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Rechercher par code étudiant..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              />
            </div>
          </div>

          {/* Filière */}
          <div className="min-w-[200px]">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <select
                value={filiere}
                onChange={(e) => {
                  setFiliere(e.target.value);
                  setPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none appearance-none bg-white cursor-pointer"
              >
                <option value="">Toutes les filières</option>
                {filieres.map((f) => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <LoadingSpinner text="Chargement des étudiants..." />
        ) : etudiants.length === 0 ? (
          <EmptyState 
            icon={Users}
            title="Aucun étudiant trouvé"
            description="Essayez de modifier vos critères de recherche"
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Code</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Filière</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Modules</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Moyenne</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Profil</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {etudiants.map((etudiant) => (
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
                          etudiant.moyenne < 10 ? 'text-red-600' : 
                          etudiant.moyenne >= 14 ? 'text-emerald-600' : 'text-slate-700'
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
                        {getProfilName(etudiant.profil) === 'À Risque' ? (
                          <Badge variant="risque" size="sm">À risque</Badge>
                        ) : (
                          <Badge variant="regulier" size="sm">Normal</Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200">
              <p className="text-sm text-slate-500">
                Affichage de {((page - 1) * limit) + 1} à {Math.min(page * limit, total)} sur {total} étudiants
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-2 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="px-4 py-2 text-sm font-medium text-slate-600">
                  Page {page} / {totalPages}
                </span>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="p-2 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
