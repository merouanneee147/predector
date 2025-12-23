'use client';

import { useState, useEffect } from 'react';
import { 
  ClipboardList, 
  Plus, 
  Search, 
  Filter, 
  Calendar, 
  User, 
  Phone, 
  Mail, 
  MessageSquare,
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  ChevronDown,
  FileText,
  Download
} from 'lucide-react';
import { interventionsApi, exportApi, isAuthenticated } from '@/lib/auth';
import { useRouter } from 'next/navigation';

interface Intervention {
  id: number;
  etudiant_id: string;
  etudiant_nom?: string;
  type: string;
  titre: string;
  description?: string;
  statut: string;
  priorite: string;
  date: string;
  heure?: string;
  created_by: string;
  created_at: string;
  notes?: Array<{ texte: string; auteur: string; date: string }>;
  resultat?: string;
}

interface Stats {
  total: number;
  par_statut: Record<string, number>;
  par_type: Record<string, number>;
  par_priorite: Record<string, number>;
  recentes_7j: number;
  etudiants_suivis: number;
}

const TYPE_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  tutorat: { label: 'Tutorat', icon: <User className="w-4 h-4" />, color: 'blue' },
  email: { label: 'Email', icon: <Mail className="w-4 h-4" />, color: 'green' },
  appel: { label: 'Appel', icon: <Phone className="w-4 h-4" />, color: 'purple' },
  reunion: { label: 'Réunion', icon: <Calendar className="w-4 h-4" />, color: 'orange' },
  autre: { label: 'Autre', icon: <MessageSquare className="w-4 h-4" />, color: 'gray' },
};

const STATUT_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  planifié: { label: 'Planifié', icon: <Clock className="w-4 h-4" />, color: 'blue' },
  en_cours: { label: 'En cours', icon: <AlertCircle className="w-4 h-4" />, color: 'yellow' },
  terminé: { label: 'Terminé', icon: <CheckCircle2 className="w-4 h-4" />, color: 'green' },
  annulé: { label: 'Annulé', icon: <XCircle className="w-4 h-4" />, color: 'red' },
};

const PRIORITE_CONFIG: Record<string, { label: string; color: string }> = {
  basse: { label: 'Basse', color: 'gray' },
  normale: { label: 'Normale', color: 'blue' },
  haute: { label: 'Haute', color: 'orange' },
  urgente: { label: 'Urgente', color: 'red' },
};

export default function InterventionsPage() {
  const router = useRouter();
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedIntervention, setSelectedIntervention] = useState<Intervention | null>(null);
  const [filters, setFilters] = useState({ type: '', statut: '', search: '' });

  // Formulaire nouvelle intervention
  const [formData, setFormData] = useState({
    etudiant_id: '',
    etudiant_nom: '',
    type: 'tutorat',
    titre: '',
    description: '',
    priorite: 'normale',
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    loadData();
  }, [router]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [intervData, statsData] = await Promise.all([
        interventionsApi.getAll({ limit: 100 }),
        interventionsApi.getStats(),
      ]);
      setInterventions(intervData.interventions || []);
      setStats(statsData);
    } catch (error: unknown) {
      const axiosError = error as { response?: { status?: number } };
      if (axiosError.response?.status === 401) {
        // Sera géré par l'intercepteur, mais on peut ajouter un message
        console.log('Session expirée, redirection vers login...');
      } else {
        console.error('Erreur chargement:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await interventionsApi.create(formData);
      setShowModal(false);
      setFormData({
        etudiant_id: '',
        etudiant_nom: '',
        type: 'tutorat',
        titre: '',
        description: '',
        priorite: 'normale',
      });
      loadData();
    } catch (error) {
      console.error('Erreur création:', error);
    }
  };

  const handleUpdateStatut = async (id: number, statut: string) => {
    try {
      await interventionsApi.update(id, { statut });
      loadData();
    } catch (error) {
      console.error('Erreur mise à jour:', error);
    }
  };

  const filteredInterventions = interventions.filter((i) => {
    if (filters.type && i.type !== filters.type) return false;
    if (filters.statut && i.statut !== filters.statut) return false;
    if (filters.search) {
      const search = filters.search.toLowerCase();
      return (
        i.etudiant_id?.toLowerCase().includes(search) ||
        i.titre?.toLowerCase().includes(search) ||
        i.etudiant_nom?.toLowerCase().includes(search)
      );
    }
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
            <ClipboardList className="w-7 h-7 text-blue-600" />
            Suivi des Interventions
          </h1>
          <p className="text-slate-500 mt-1">Gérez et tracez les actions pédagogiques</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => exportApi.downloadInterventions()}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 text-slate-700"
          >
            <Download className="w-4 h-4" />
            Exporter Excel
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4" />
            Nouvelle Intervention
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
            <div className="text-2xl font-bold text-slate-800">{stats.total}</div>
            <div className="text-sm text-slate-500">Total interventions</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
            <div className="text-2xl font-bold text-blue-600">{stats.par_statut?.planifié || 0}</div>
            <div className="text-sm text-slate-500">Planifiées</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
            <div className="text-2xl font-bold text-yellow-600">{stats.par_statut?.en_cours || 0}</div>
            <div className="text-sm text-slate-500">En cours</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
            <div className="text-2xl font-bold text-green-600">{stats.par_statut?.terminé || 0}</div>
            <div className="text-sm text-slate-500">Terminées</div>
          </div>
          <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
            <div className="text-2xl font-bold text-purple-600">{stats.etudiants_suivis}</div>
            <div className="text-sm text-slate-500">Étudiants suivis</div>
          </div>
        </div>
      )}

      {/* Filtres */}
      <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Rechercher..."
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
            className="px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tous les types</option>
            {Object.entries(TYPE_CONFIG).map(([key, { label }]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
          <select
            value={filters.statut}
            onChange={(e) => setFilters({ ...filters, statut: e.target.value })}
            className="px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tous les statuts</option>
            {Object.entries(STATUT_CONFIG).map(([key, { label }]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Liste des interventions */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Étudiant</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Titre</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Priorité</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Statut</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredInterventions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-slate-500">
                    <FileText className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                    <p>Aucune intervention trouvée</p>
                  </td>
                </tr>
              ) : (
                filteredInterventions.map((intervention) => {
                  const typeConfig = TYPE_CONFIG[intervention.type] || TYPE_CONFIG.autre;
                  const statutConfig = STATUT_CONFIG[intervention.statut] || STATUT_CONFIG.planifié;
                  const prioriteConfig = PRIORITE_CONFIG[intervention.priorite] || PRIORITE_CONFIG.normale;

                  return (
                    <tr key={intervention.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3">
                        <div className="text-sm font-medium text-slate-800">{intervention.date}</div>
                        <div className="text-xs text-slate-400">{intervention.heure}</div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm font-medium text-slate-800">{intervention.etudiant_id}</div>
                        {intervention.etudiant_nom && (
                          <div className="text-xs text-slate-400">{intervention.etudiant_nom}</div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-${typeConfig.color}-100 text-${typeConfig.color}-700`}>
                          {typeConfig.icon}
                          {typeConfig.label}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-sm text-slate-800 max-w-xs truncate">{intervention.titre}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium bg-${prioriteConfig.color}-100 text-${prioriteConfig.color}-700`}>
                          {prioriteConfig.label}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="relative group">
                          <button className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-${statutConfig.color}-100 text-${statutConfig.color}-700`}>
                            {statutConfig.icon}
                            {statutConfig.label}
                            <ChevronDown className="w-3 h-3" />
                          </button>
                          <div className="absolute top-full left-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                            {Object.entries(STATUT_CONFIG).map(([key, { label }]) => (
                              <button
                                key={key}
                                onClick={() => handleUpdateStatut(intervention.id, key)}
                                className="block w-full px-4 py-2 text-left text-sm hover:bg-slate-50 first:rounded-t-lg last:rounded-b-lg"
                              >
                                {label}
                              </button>
                            ))}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => setSelectedIntervention(intervention)}
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          Détails
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Nouvelle Intervention */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-slate-200">
              <h2 className="text-xl font-bold text-slate-800">Nouvelle Intervention</h2>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Code Étudiant *
                  </label>
                  <input
                    type="text"
                    value={formData.etudiant_id}
                    onChange={(e) => setFormData({ ...formData, etudiant_id: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Nom (optionnel)
                  </label>
                  <input
                    type="text"
                    value={formData.etudiant_nom}
                    onChange={(e) => setFormData({ ...formData, etudiant_nom: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Type *</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {Object.entries(TYPE_CONFIG).map(([key, { label }]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Priorité</label>
                  <select
                    value={formData.priorite}
                    onChange={(e) => setFormData({ ...formData, priorite: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {Object.entries(PRIORITE_CONFIG).map(([key, { label }]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Titre *</label>
                <input
                  type="text"
                  value={formData.titre}
                  onChange={(e) => setFormData({ ...formData, titre: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 border border-slate-200 rounded-lg hover:bg-slate-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Créer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Détails */}
      {selectedIntervention && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4">
            <div className="p-6 border-b border-slate-200 flex justify-between items-start">
              <div>
                <h2 className="text-xl font-bold text-slate-800">{selectedIntervention.titre}</h2>
                <p className="text-sm text-slate-500">
                  {selectedIntervention.date} - Étudiant {selectedIntervention.etudiant_id}
                </p>
              </div>
              <button
                onClick={() => setSelectedIntervention(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <span className="text-xs text-slate-500">Type</span>
                  <div className="font-medium">{TYPE_CONFIG[selectedIntervention.type]?.label}</div>
                </div>
                <div>
                  <span className="text-xs text-slate-500">Statut</span>
                  <div className="font-medium">{STATUT_CONFIG[selectedIntervention.statut]?.label}</div>
                </div>
                <div>
                  <span className="text-xs text-slate-500">Priorité</span>
                  <div className="font-medium">{PRIORITE_CONFIG[selectedIntervention.priorite]?.label}</div>
                </div>
              </div>
              {selectedIntervention.description && (
                <div>
                  <span className="text-xs text-slate-500">Description</span>
                  <p className="text-slate-700 mt-1">{selectedIntervention.description}</p>
                </div>
              )}
              {selectedIntervention.resultat && (
                <div>
                  <span className="text-xs text-slate-500">Résultat</span>
                  <p className="text-slate-700 mt-1">{selectedIntervention.resultat}</p>
                </div>
              )}
              <div className="text-xs text-slate-400">
                Créé par {selectedIntervention.created_by} le {selectedIntervention.created_at?.split('T')[0]}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
