"use client";

import { usePathname } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import AuthGuard from '@/components/AuthGuard';

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const pathname = usePathname();
  
  // Page de login - pas de sidebar, juste le contenu
  if (pathname === '/login') {
    return <AuthGuard>{children}</AuthGuard>;
  }

  // Autres pages - avec sidebar et layout complet
  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:ml-72 transition-all duration-300">
          <main className="pt-20 lg:pt-8 pb-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-[1400px] mx-auto w-full">
              {children}
            </div>
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
