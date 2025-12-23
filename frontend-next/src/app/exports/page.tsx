'use client';

import { useState, useEffect } from 'react';
import { 
  Download, 
  FileSpreadsheet, 
  Users, 
  AlertTriangle, 
  BookOpen,
  ClipboardList,
  FileText,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { isAuthenticated, getStoredToken } from '@/lib/auth';
import { useRouter } from 'next/navigation';

const API_BASE_URL = 'http://localhost:5000/api';

interface ExportOption {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  endpoint: string;
  adminOnly?: boolean;
}

const EXPORT_OPTIONS: ExportOption[] = [
  {
    id: 'etudiants',
    title: 'Liste des Étudiants',
    description: 'Export complet de tous les étudiants avec moyennes et profils',
    icon: <Users className="w-6 h-6" />,
    color: 'blue',
    endpoint: '/export/etudiants',
  },
  {
    id: 'etudiants-risque',
    title: 'Étudiants à Risque',
    description: 'Liste des étudiants nécessitant un suivi prioritaire',
    icon: <AlertTriangle className="w-6 h-6" />,
    color: 'red',
    endpoint: '/export/etudiants-risque',
  },
  {
    id: 'modules',
    title: 'Statistiques Modules',
    description: 'Analyse des modules avec taux d\'échec et difficulté',
    icon: <BookOpen className="w-6 h-6" />,
    color: 'green',
    endpoint: '/export/modules',
  },
  {
    id: 'interventions',
    title: 'Historique Interventions',
    description: 'Suivi de toutes les actions pédagogiques',
    icon: <ClipboardList className="w-6 h-6" />,
    color: 'purple',
    endpoint: '/export/interventions',
  },
  {
    id: 'rapport-complet',
    title: 'Rapport Complet',
    description: 'Export multi-onglets avec toutes les données (Admin)',
    icon: <FileText className="w-6 h-6" />,
    color: 'orange',
    endpoint: '/export/rapport-complet',
    adminOnly: true,
  },
];

export default function ExportsPage() {
  const router = useRouter();
  const [downloading, setDownloading] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  const handleDownload = async (option: ExportOption) => {
    const token = getStoredToken();
    if (!token) {
      router.push('/login');
      return;
    }

    setDownloading(option.id);
    setSuccess(null);

    try {
      const response = await fetch(`${API_BASE_URL}${option.endpoint}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Erreur lors du téléchargement');
      }

      // Récupérer le blob et créer un lien de téléchargement
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Récupérer le nom du fichier depuis le header ou générer un nom
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `${option.id}_${new Date().toISOString().split('T')[0]}.xlsx`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?(.+)"?/);
        if (match) filename = match[1];
      }
      
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccess(option.id);
      setTimeout(() => setSuccess(null), 3000);
    } catch (error) {
      console.error('Erreur téléchargement:', error);
      alert(error instanceof Error ? error.message : 'Erreur lors du téléchargement');
    } finally {
      setDownloading(null);
    }
  };

  const getColorClasses = (color: string) => {
    const colors: Record<string, { bg: string; border: string; icon: string; button: string }> = {
      blue: {
        bg: 'bg-blue-50',
        border: 'border-blue-200',
        icon: 'text-blue-600',
        button: 'bg-blue-600 hover:bg-blue-700',
      },
      red: {
        bg: 'bg-red-50',
        border: 'border-red-200',
        icon: 'text-red-600',
        button: 'bg-red-600 hover:bg-red-700',
      },
      green: {
        bg: 'bg-green-50',
        border: 'border-green-200',
        icon: 'text-green-600',
        button: 'bg-green-600 hover:bg-green-700',
      },
      purple: {
        bg: 'bg-purple-50',
        border: 'border-purple-200',
        icon: 'text-purple-600',
        button: 'bg-purple-600 hover:bg-purple-700',
      },
      orange: {
        bg: 'bg-orange-50',
        border: 'border-orange-200',
        icon: 'text-orange-600',
        button: 'bg-orange-600 hover:bg-orange-700',
      },
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
          <FileSpreadsheet className="w-7 h-7 text-green-600" />
          Exports Excel
        </h1>
        <p className="text-slate-500 mt-1">
          Téléchargez les rapports au format Excel (.xlsx)
        </p>
      </div>

      {/* Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
        <FileSpreadsheet className="w-5 h-5 text-blue-600 mt-0.5" />
        <div>
          <p className="text-blue-800 font-medium">Format Excel (.xlsx)</p>
          <p className="text-blue-600 text-sm mt-1">
            Les fichiers sont générés avec des colonnes formatées et prêts à être utilisés dans Excel, Google Sheets ou LibreOffice.
          </p>
        </div>
      </div>

      {/* Export Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {EXPORT_OPTIONS.map((option) => {
          const colors = getColorClasses(option.color);
          const isDownloading = downloading === option.id;
          const isSuccess = success === option.id;

          return (
            <div
              key={option.id}
              className={`${colors.bg} border ${colors.border} rounded-xl p-6 transition-all hover:shadow-md`}
            >
              <div className={`inline-flex p-3 rounded-xl ${colors.bg} ${colors.icon} mb-4`}>
                {option.icon}
              </div>
              
              <h3 className="text-lg font-semibold text-slate-800 mb-2">
                {option.title}
                {option.adminOnly && (
                  <span className="ml-2 text-xs bg-orange-200 text-orange-700 px-2 py-0.5 rounded-full">
                    Admin
                  </span>
                )}
              </h3>
              
              <p className="text-slate-600 text-sm mb-4">
                {option.description}
              </p>

              <button
                onClick={() => handleDownload(option)}
                disabled={isDownloading}
                className={`w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg text-white font-medium transition-colors ${colors.button} disabled:opacity-50`}
              >
                {isDownloading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Génération...
                  </>
                ) : isSuccess ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Téléchargé !
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Télécharger
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {/* Note */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-sm text-slate-600">
        <p>
          <strong>Note:</strong> Les exports volumineux peuvent prendre quelques secondes à générer. 
          Assurez-vous d&apos;avoir le module <code className="bg-slate-200 px-1 rounded">openpyxl</code> installé 
          sur le serveur (<code className="bg-slate-200 px-1 rounded">pip install openpyxl</code>).
        </p>
      </div>
    </div>
  );
}
