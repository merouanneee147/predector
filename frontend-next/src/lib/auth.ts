// Gestion de l'authentification
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export interface User {
  username: string;
  role: 'admin' | 'enseignant' | 'tuteur';
  nom: string;
  email: string;
  permissions: string[];
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}

// Clés localStorage
const TOKEN_KEY = 'soutien_token';
const USER_KEY = 'soutien_user';

// Récupérer le token stocké
export const getStoredToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
};

// Récupérer l'utilisateur stocké
export const getStoredUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
};

// Sauvegarder l'authentification
export const saveAuth = (token: string, user: User): void => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

// Effacer l'authentification
export const clearAuth = (): void => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

// Vérifier si authentifié
export const isAuthenticated = (): boolean => {
  return !!getStoredToken();
};

// Créer un client axios avec authentification
export const createAuthenticatedApi = () => {
  const token = getStoredToken();
  const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  // Intercepteur pour gérer les erreurs 401
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Token expiré ou invalide - rediriger vers login
        clearAuth();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
      return Promise.reject(error);
    }
  );

  return api;
};

// API d'authentification
export const authApi = {
  login: async (username: string, password: string) => {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, {
      username,
      password,
    });
    if (response.data.success) {
      saveAuth(response.data.token, response.data.user);
    }
    return response.data;
  },

  logout: async () => {
    const api = createAuthenticatedApi();
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // Ignorer les erreurs de déconnexion
    }
    clearAuth();
  },

  getCurrentUser: async () => {
    const api = createAuthenticatedApi();
    const response = await api.get('/auth/me');
    return response.data.user;
  },

  getUsers: async () => {
    const api = createAuthenticatedApi();
    const response = await api.get('/auth/users');
    return response.data.users;
  },

  register: async (userData: {
    username: string;
    password: string;
    role: string;
    nom: string;
    email: string;
  }) => {
    const api = createAuthenticatedApi();
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
};

// API des interventions
export const interventionsApi = {
  getAll: async (filters?: {
    etudiant_id?: string;
    type?: string;
    statut?: string;
    limit?: number;
  }) => {
    const api = createAuthenticatedApi();
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, String(value));
      });
    }
    const response = await api.get(`/interventions?${params.toString()}`);
    return response.data;
  },

  getById: async (id: number) => {
    const api = createAuthenticatedApi();
    const response = await api.get(`/interventions/${id}`);
    return response.data.intervention;
  },

  getByEtudiant: async (etudiantId: string) => {
    const api = createAuthenticatedApi();
    const response = await api.get(`/interventions/etudiant/${etudiantId}`);
    return response.data;
  },

  create: async (intervention: {
    etudiant_id: string;
    etudiant_nom?: string;
    type: string;
    titre: string;
    description?: string;
    priorite?: string;
  }) => {
    const api = createAuthenticatedApi();
    const response = await api.post('/interventions', intervention);
    return response.data;
  },

  update: async (id: number, data: {
    statut?: string;
    resultat?: string;
    nouvelle_note?: string;
  }) => {
    const api = createAuthenticatedApi();
    const response = await api.put(`/interventions/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const api = createAuthenticatedApi();
    const response = await api.delete(`/interventions/${id}`);
    return response.data;
  },

  getStats: async () => {
    const api = createAuthenticatedApi();
    const response = await api.get('/interventions/stats');
    return response.data;
  },
};

// API d'export
export const exportApi = {
  downloadEtudiants: () => {
    const token = getStoredToken();
    window.open(`${API_BASE_URL}/export/etudiants?token=${token}`, '_blank');
  },

  downloadEtudiantsRisque: () => {
    const token = getStoredToken();
    window.open(`${API_BASE_URL}/export/etudiants-risque?token=${token}`, '_blank');
  },

  downloadModules: () => {
    const token = getStoredToken();
    window.open(`${API_BASE_URL}/export/modules?token=${token}`, '_blank');
  },

  downloadInterventions: () => {
    const token = getStoredToken();
    window.open(`${API_BASE_URL}/export/interventions?token=${token}`, '_blank');
  },

  downloadRapportComplet: () => {
    const token = getStoredToken();
    window.open(`${API_BASE_URL}/export/rapport-complet?token=${token}`, '_blank');
  },
};
