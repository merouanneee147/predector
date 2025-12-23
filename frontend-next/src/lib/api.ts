import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Stats {
  nb_etudiants: number;
  nb_modules: number;
  nb_filieres: number;
  taux_echec_global: number;
  moyenne_generale: number;
  profils_count: {
    'Excellence': number;
    'Régulier': number;
    'En Progression': number;
    'En Difficulté': number;
    'À Risque': number;
  };
  filieres_stats: {
    [key: string]: {
      ID: number;
      Note_sur_20: number;
      Needs_Support: number;
    };
  };
}

export interface Etudiant {
  id: string;
  filiere: string;
  annee?: number;
  moyenne: number;
  nb_modules: number;
  modules_echec?: number;
  taux_echec?: number;
  profil: string | {
    nom: string;
    color: string;
    emoji: string;
    level: number;
  };
  profil_info?: {
    nom: string;
    color: string;
    emoji: string;
    level: number;
  };
  score_risque?: number;
  probabilite_risque?: number;
}

// Helper pour extraire le nom du profil
export const getProfilName = (profil: Etudiant['profil']): string => {
  if (typeof profil === 'string') return profil;
  if (profil && typeof profil === 'object') return profil.nom;
  return 'Non défini';
};

export interface EtudiantDetail extends Etudiant {
  Code: string;  // ID de l'étudiant
  Filiere: string;
  Moyenne: number;
  Total?: number;
  risque: boolean;
  modules: ModuleEtudiant[];
  recommandations: string[];
}


export interface ModuleEtudiant {
  Code_Module: string;
  Filiere: string;
  Annee: number;
  Semestre: number;
  Note: number;
}

export interface Module {
  nom: string;
  nom_fr: string;
  nb_etudiants: number;
  moyenne: number;
  taux_echec: number;
  difficulte: {
    niveau: string;
    color: string;
  };
}

export interface Prediction {
  etudiant_code: string;
  risque: boolean;
  probabilite: number;
  profil: string;
  recommandations: string[];
  modules_similaires?: string[];
}

// API functions
export const getStats = async (): Promise<Stats> => {
  const response = await api.get('/stats');
  return response.data;
};

export const getEtudiants = async (params?: {
  page?: number;
  limit?: number;
  filiere?: string;
  search?: string;
  risque?: boolean;
}): Promise<{
  etudiants: Etudiant[];
  total: number;
  page: number;
  limit: number;
}> => {
  const response = await api.get('/etudiants', { params });
  return response.data;
};

export const getEtudiant = async (code: string): Promise<EtudiantDetail> => {
  const response = await api.get(`/etudiant/${code}`);
  return response.data;
};

export const getModules = async (params?: {
  page?: number;
  limit?: number;
  search?: string;
}): Promise<{
  modules: Module[];
  total: number;
  page: number;
  limit: number;
}> => {
  const response = await api.get('/modules', { params });
  return response.data;
};

export const predict = async (data: {
  code_etudiant?: string;
  filiere: string;
  modules: { code: string; note: number }[];
}): Promise<Prediction> => {
  const response = await api.post('/predict', data);
  return response.data;
};

export const getEtudiantsRisque = async (): Promise<Etudiant[]> => {
  const response = await api.get('/etudiants-risque');
  return response.data.etudiants || response.data;
};

export const getFilieres = async (): Promise<string[]> => {
  const response = await api.get('/filieres');
  return response.data.filieres;
};

// Rapports
export const generateRapportGlobal = async (): Promise<Blob> => {
  const response = await api.get('/rapports/global', { responseType: 'blob' });
  return response.data;
};

export const generateRapportFiliere = async (filiere: string): Promise<Blob> => {
  const response = await api.get(`/rapports/filiere/${filiere}`, { responseType: 'blob' });
  return response.data;
};

export const generateRapportEtudiant = async (code: string): Promise<Blob> => {
  const response = await api.get(`/rapports/etudiant/${code}`, { responseType: 'blob' });
  return response.data;
};

// Alertes
export const sendAlerteEtudiant = async (code: string, email: string): Promise<{ message: string }> => {
  // Utiliser la route test-email qui fonctionne
  const response = await api.post('/alertes/test-email', { code, email });
  return response.data;
};

export const sendAlerteModule = async (module: string, emails: string[]): Promise<{ message: string }> => {
  // Temporairement désactivé - utilise alerte étudiant à la place
  return Promise.resolve({ message: "Fonctionnalité en cours de développement. Utilisez l'alerte étudiant." });
};

export const sendRapportHebdo = async (email: string): Promise<{ message: string }> => {
  // Temporairement désactivé
  return Promise.resolve({ message: "Fonctionnalité en cours de développement. Utilisez l'alerte étudiant." });
};

export default api;
