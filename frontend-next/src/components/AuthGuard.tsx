'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { isAuthenticated, getStoredUser, User } from '@/lib/auth';
import { Loader2, GraduationCap } from 'lucide-react';

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [checking, setChecking] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const checkAuth = () => {
      // Pages publiques (pas besoin d'auth)
      if (pathname === '/login') {
        setChecking(false);
        return;
      }

      // Vérifier l'authentification
      if (!isAuthenticated()) {
        router.push('/login');
        return;
      }

      // Récupérer l'utilisateur
      const storedUser = getStoredUser();
      setUser(storedUser);
      setChecking(false);
    };

    checkAuth();
  }, [pathname, router]);

  // Page de login - afficher directement sans wrapper
  if (pathname === '/login') {
    return <>{children}</>;
  }

  // Afficher un loader pendant la vérification
  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-lg mb-4">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-3" />
          <p className="text-slate-500">Chargement...</p>
        </div>
      </div>
    );
  }

  // Non authentifié - ne rien afficher (redirection en cours)
  if (!user) {
    return null;
  }

  // Authentifié - afficher le contenu normal
  return <>{children}</>;
}
