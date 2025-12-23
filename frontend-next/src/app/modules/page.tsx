"use client";

import { useEffect, useState, useCallback } from 'react';
import { Search, ChevronLeft, ChevronRight, BookOpen } from 'lucide-react';
import { getModules, Module } from '@/lib/api';
import { LoadingSpinner, Badge, PageHeader, EmptyState } from '@/components/ui';

export default function ModulesPage() {
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const limit = 20;

  const fetchModules = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getModules({ page, limit, search });
      setModules(data.modules);
      setTotal(data.total);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    fetchModules();
  }, [fetchModules]);

  const totalPages = Math.ceil(total / limit);

  const getTauxEchecVariant = (taux: number) => {
    if (taux >= 50) return 'risque';
    if (taux >= 30) return 'difficulte';
    if (taux >= 15) return 'progression';
    return 'regulier';
  };

  return (
    <div className="space-y-6">
      <PageHeader 
        title="Gestion des Modules"
        description={`${total} modules disponibles`}
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
                placeholder="Rechercher un module..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <LoadingSpinner text="Chargement des modules..." />
        ) : modules.length === 0 ? (
          <EmptyState 
            icon={BookOpen}
            title="Aucun module trouvé"
            description="Essayez de modifier vos critères de recherche"
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Module</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Nom (FR)</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Étudiants</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Moyenne</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Taux Échec</th>
                    <th className="text-left py-4 px-6 font-semibold text-slate-600">Difficulté</th>
                  </tr>
                </thead>
                <tbody>
                  {modules.map((module, index) => (
                    <tr 
                      key={`${module.nom}-${index}`}
                      className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
                    >
                      <td className="py-4 px-6 font-medium text-slate-800" dir="rtl">
                        {module.nom}
                      </td>
                      <td className="py-4 px-6 text-slate-600">{module.nom_fr}</td>
                      <td className="py-4 px-6 text-slate-600">{module.nb_etudiants}</td>
                      <td className="py-4 px-6">
                        <span className={`font-medium ${
                          module.moyenne < 10 ? 'text-red-600' : 
                          module.moyenne >= 14 ? 'text-emerald-600' : 'text-slate-700'
                        }`}>
                          {module.moyenne?.toFixed(2)}/20
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <Badge variant={getTauxEchecVariant(module.taux_echec)} size="sm">
                          {module.taux_echec?.toFixed(1)}%
                        </Badge>
                      </td>
                      <td className="py-4 px-6">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          module.difficulte?.color === 'red' ? 'bg-red-100 text-red-700' :
                          module.difficulte?.color === 'orange' ? 'bg-orange-100 text-orange-700' :
                          module.difficulte?.color === 'yellow' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-green-100 text-green-700'
                        }`}>
                          {module.difficulte?.niveau || 'N/A'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200">
              <p className="text-sm text-slate-500">
                Affichage de {((page - 1) * limit) + 1} à {Math.min(page * limit, total)} sur {total} modules
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
