"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { 
  Users, 
  BookOpen, 
  AlertTriangle, 
  TrendingUp,
  GraduationCap,
  ArrowRight,
  Activity,
  Target,
  Zap,
  Award
} from 'lucide-react';
import { getStats, getEtudiantsRisque, getProfilName, Stats, Etudiant } from '@/lib/api';
import { StatCard, LoadingSpinner, Badge, getProfilVariant, PageHeader, Card, CardHeader, Button, ProgressBar, SkeletonCard, SkeletonTable } from '@/components/ui';
import { FiliereBarChart, ProfilPieChart } from '@/components/Charts';

// Couleurs pour les profils
const PROFIL_COLORS: Record<string, string> = {
  'Excellence': '#10B981',
  'Régulier': '#3B82F6', 
  'Progression': '#F59E0B',
  'Difficulté': '#F97316',
  'Risque': '#EF4444'
};

// Icônes pour les profils (remplacent les emojis)
const PROFIL_ICONS: Record<string, typeof Award> = {
  'Excellence': Award,
  'Régulier': Target,
  'Progression': TrendingUp,
  'Difficulté': AlertTriangle,
  'Risque': Zap
};

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [etudiantsRisque, setEtudiantsRisque] = useState<Etudiant[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, risqueData] = await Promise.all([
          getStats(),
          getEtudiantsRisque()
        ]);
        setStats(statsData);
        setEtudiantsRisque(risqueData.slice(0, 5));
      } catch (error) {
        console.error('Erreur lors du chargement:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader 
          title="Tableau de Bord"
          description="Vue d'ensemble du système de soutien pédagogique"
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          <SkeletonTable rows={3} />
          <SkeletonTable rows={3} />
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center px-4">
        <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-6">
          <AlertTriangle className="w-10 h-10 text-red-500" />
        </div>
        <h2 className="text-xl font-bold text-slate-800 mb-2">Erreur de connexion</h2>
        <p className="text-slate-500 mb-6 max-w-md">
          Impossible de se connecter au serveur. Vérifiez que le backend Flask est en cours d'exécution sur le port 5000.
        </p>
        <Button onClick={() => window.location.reload()}>
          Réessayer
        </Button>
      </div>
    );
  }

  const profilData = [
    { name: 'Excellence', fullName: 'Excellence', value: stats.profils_count['Excellence'] || 0, color: PROFIL_COLORS['Excellence'] },
    { name: 'Régulier', fullName: 'Régulier', value: stats.profils_count['Régulier'] || 0, color: PROFIL_COLORS['Régulier'] },
    { name: 'Progression', fullName: 'En Progression', value: stats.profils_count['En Progression'] || 0, color: PROFIL_COLORS['Progression'] },
    { name: 'Difficulté', fullName: 'En Difficulté', value: stats.profils_count['En Difficulté'] || 0, color: PROFIL_COLORS['Difficulté'] },
    { name: 'Risque', fullName: 'À Risque', value: stats.profils_count['À Risque'] || 0, color: PROFIL_COLORS['Risque'] },
  ].filter(p => p.value > 0);
  
  const totalEtudiants = profilData.reduce((sum, p) => sum + p.value, 0);

  // Données des filières
  const filiereData = Object.entries(stats.filieres_stats).map(([filiere, data]) => ({
    filiere,
    etudiants: data.ID,
    moyenne: Number(data.Note_sur_20.toFixed(1)),
    tauxRisque: Math.round(data.Needs_Support * 100)
  })).sort((a, b) => b.etudiants - a.etudiants);

  return (
    <div className="space-y-6 sm:space-y-8">
      <PageHeader 
        title="Tableau de Bord"
        description="Vue d'ensemble du système de soutien pédagogique"
      />

      {/* Stats Cards - Responsive Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <StatCard
          title="Total Étudiants"
          value={stats.nb_etudiants.toLocaleString()}
          subtitle="Étudiants actifs"
          icon={Users}
          iconColor="text-blue-600"
          iconBgColor="bg-blue-100"
        />
        <StatCard
          title="Modules"
          value={stats.nb_modules}
          subtitle={`${stats.nb_filieres} filières`}
          icon={BookOpen}
          iconColor="text-emerald-600"
          iconBgColor="bg-emerald-100"
        />
        <StatCard
          title="Étudiants à Risque"
          value={stats.profils_count['À Risque'] || 0}
          subtitle={`${((stats.profils_count['À Risque'] || 0) / stats.nb_etudiants * 100).toFixed(1)}% du total`}
          icon={AlertTriangle}
          iconColor="text-amber-600"
          iconBgColor="bg-amber-100"
        />
        <StatCard
          title="Moyenne Globale"
          value={`${stats.moyenne_generale.toFixed(2)}/20`}
          subtitle="Performance moyenne"
          icon={TrendingUp}
          iconColor="text-violet-600"
          iconBgColor="bg-violet-100"
        />
      </div>

      {/* Charts Section - Responsive */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Distribution par Filière */}
        <Card padding="none" className="overflow-hidden">
          <div className="p-4 sm:p-6">
            <CardHeader 
              title="Étudiants par Filière"
              subtitle={`${filiereData.length} filières`}
              icon={Activity}
              iconColor="text-blue-600"
              iconBgColor="bg-blue-100"
            />
            <div className="h-64 sm:h-72">
              <FiliereBarChart data={filiereData} />
            </div>
          </div>
        </Card>

        {/* Distribution par Profil */}
        <Card padding="none" className="overflow-hidden">
          <div className="p-4 sm:p-6">
            <CardHeader 
              title="Répartition des Profils"
              subtitle={`${totalEtudiants.toLocaleString()} étudiants`}
              icon={Target}
              iconColor="text-violet-600"
              iconBgColor="bg-violet-100"
            />
            <div className="flex flex-col sm:flex-row items-center gap-4">
              {/* Pie Chart */}
              <div className="w-full sm:flex-1 h-52 sm:h-56">
                <ProfilPieChart data={profilData} totalEtudiants={totalEtudiants} />
              </div>
              
              {/* Légende personnalisée avec icônes */}
              <div className="flex flex-row sm:flex-col flex-wrap justify-center gap-2 sm:min-w-[150px]">
                {profilData.map((profil, index) => {
                  const percent = totalEtudiants > 0 ? ((profil.value / totalEtudiants) * 100).toFixed(0) : 0;
                  const IconComponent = PROFIL_ICONS[profil.name] || Target;
                  return (
                    <div 
                      key={index}
                      className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer"
                    >
                      <div 
                        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                        style={{ backgroundColor: `${profil.color}20` }}
                      >
                        <IconComponent className="w-4 h-4" style={{ color: profil.color }} />
                      </div>
                      <div className="hidden sm:block">
                        <div className="text-xs font-medium text-slate-700">{profil.name}</div>
                        <div className="text-xs text-slate-500">
                          {profil.value.toLocaleString()} ({percent}%)
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Étudiants à Risque */}
      <Card padding="none" className="overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-100">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-amber-100 rounded-xl">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-800">
                  Étudiants Nécessitant une Attention
                </h2>
                <p className="text-sm text-slate-500">
                  Les {etudiantsRisque.length} cas les plus critiques
                </p>
              </div>
            </div>
            <Link href="/risque">
              <Button variant="secondary" size="sm" icon={ArrowRight} iconPosition="right">
                Voir tout
              </Button>
            </Link>
          </div>
        </div>

        {etudiantsRisque.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[600px]">
              <thead>
                <tr className="bg-slate-50">
                  <th className="text-left py-3 px-4 sm:px-6 font-semibold text-slate-600 text-xs sm:text-sm">Code Étudiant</th>
                  <th className="text-left py-3 px-4 sm:px-6 font-semibold text-slate-600 text-xs sm:text-sm">Filière</th>
                  <th className="text-left py-3 px-4 sm:px-6 font-semibold text-slate-600 text-xs sm:text-sm">Moyenne</th>
                  <th className="text-left py-3 px-4 sm:px-6 font-semibold text-slate-600 text-xs sm:text-sm">Profil</th>
                  <th className="text-left py-3 px-4 sm:px-6 font-semibold text-slate-600 text-xs sm:text-sm">Niveau de Risque</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {etudiantsRisque.map((etudiant, index) => {
                  const risque = (etudiant.score_risque || 0) * 100;
                  return (
                    <tr 
                      key={etudiant.id} 
                      className="hover:bg-blue-50/50 transition-colors"
                    >
                      <td className="py-3 px-4 sm:px-6">
                        <Link 
                          href={`/etudiants/${etudiant.id}`}
                          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
                        >
                          <div className="w-7 h-7 sm:w-8 sm:h-8 bg-blue-100 rounded-full flex items-center justify-center text-xs font-bold text-blue-700">
                            {index + 1}
                          </div>
                          <span className="hidden sm:inline">{etudiant.id}</span>
                          <span className="sm:hidden">{String(etudiant.id).slice(-6)}</span>
                        </Link>
                      </td>
                      <td className="py-3 px-4 sm:px-6">
                        <Badge variant="info" size="sm">{etudiant.filiere}</Badge>
                      </td>
                      <td className="py-3 px-4 sm:px-6">
                        <span className={`font-semibold text-sm ${
                          etudiant.moyenne < 8 ? 'text-red-600' : 
                          etudiant.moyenne < 10 ? 'text-orange-600' : 'text-slate-700'
                        }`}>
                          {etudiant.moyenne?.toFixed(2)}/20
                        </span>
                      </td>
                      <td className="py-3 px-4 sm:px-6">
                        <Badge variant={getProfilVariant(getProfilName(etudiant.profil))} size="sm">
                          {getProfilName(etudiant.profil)}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 sm:px-6">
                        <ProgressBar 
                          value={risque} 
                          showLabel 
                          size="sm"
                          className="max-w-[120px]"
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12 px-4">
            <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <GraduationCap className="w-8 h-8 text-emerald-600" />
            </div>
            <p className="text-slate-600 font-medium">Excellent ! Aucun étudiant à risque critique</p>
            <p className="text-slate-400 text-sm mt-1">Tous les étudiants présentent des performances satisfaisantes</p>
          </div>
        )}
      </Card>
    </div>
  );
}
