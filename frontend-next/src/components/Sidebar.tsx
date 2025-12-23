"use client";

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Users,
  BookOpen,
  AlertTriangle,
  Brain,
  FileText,
  Mail,
  GraduationCap,
  ClipboardList,
  FileSpreadsheet,
  LogOut,
  User,
  Shield,
  ChevronDown,
  Menu,
  X,
  Bell,
  Settings,
  Sparkles,
  Target
} from 'lucide-react';
import { getStoredUser, authApi, User as UserType } from '@/lib/auth';

const menuItems = [
  {
    section: 'Principal',
    items: [
      { href: '/', label: 'Tableau de Bord', icon: LayoutDashboard, badge: null },
      { href: '/etudiants', label: 'Étudiants', icon: Users, badge: null },
      { href: '/modules', label: 'Modules', icon: BookOpen, badge: null },
    ]
  },
  {
    section: 'Analyse & Prédiction',
    items: [
      { href: '/assistant', label: 'Assistant IA', icon: Sparkles, badge: 'AI' },
      { href: '/prediction-avancee', label: 'Prédiction IA', icon: Brain, badge: 'AI' },
      { href: '/modules-futurs', label: 'Modules Recommandés', icon: Target, badge: 'NEW' },
      { href: '/risque', label: 'Étudiants à Risque', icon: AlertTriangle, badge: 'urgent' },
      { href: '/interventions', label: 'Interventions', icon: ClipboardList, badge: null },
    ]
  },
  {
    section: 'Rapports & Exports',
    items: [
      { href: '/rapports', label: 'Rapports PDF', icon: FileText, badge: null },
      { href: '/exports', label: 'Exports Excel', icon: FileSpreadsheet, badge: null },
      { href: '/alertes', label: 'Alertes Email', icon: Mail, badge: null },
    ]
  }
];

const roleConfig: Record<string, { color: string; gradient: string; icon: React.ElementType }> = {
  admin: {
    color: 'from-rose-500 to-red-600',
    gradient: 'bg-gradient-to-br from-rose-500 to-red-600',
    icon: Shield
  },
  enseignant: {
    color: 'from-blue-500 to-indigo-600',
    gradient: 'bg-gradient-to-br from-blue-500 to-indigo-600',
    icon: GraduationCap
  },
  tuteur: {
    color: 'from-emerald-500 to-teal-600',
    gradient: 'bg-gradient-to-br from-emerald-500 to-teal-600',
    icon: Users
  },
};

const roleLabels: Record<string, string> = {
  admin: 'Administrateur',
  enseignant: 'Enseignant',
  tuteur: 'Tuteur',
};

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<UserType | null>(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const storedUser = getStoredUser();
    if (storedUser) {
      setUser(storedUser);
    }
  }, [pathname]);

  useEffect(() => {
    if (mobileOpen) {
      setMobileOpen(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  const handleLogout = async () => {
    await authApi.logout();
    router.push('/login');
  };

  if (pathname === '/login') {
    return null;
  }

  const userRoleConfig = user ? roleConfig[user.role] || roleConfig.tuteur : roleConfig.tuteur;
  const UserIcon = userRoleConfig.icon;

  return (
    <>
      {/* Header Mobile */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-xl border-b border-slate-200/50 z-30 lg:hidden">
        <div className="flex items-center justify-between h-full px-4">
          <button
            onClick={() => setMobileOpen(true)}
            className="p-2.5 hover:bg-slate-100 rounded-xl transition-all duration-200 active:scale-95"
            aria-label="Menu"
          >
            <Menu className="w-6 h-6 text-slate-700" />
          </button>

          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
                <GraduationCap className="w-5 h-5 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center">
                <Sparkles className="w-2.5 h-2.5 text-white" />
              </div>
            </div>
            <div>
              <h1 className="font-bold text-slate-800 text-sm">Soutien Pédagogique</h1>
              <p className="text-[10px] text-slate-500 font-medium">Système Intelligent</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button className="relative p-2.5 hover:bg-slate-100 rounded-xl transition-all duration-200">
              <Bell className="w-5 h-5 text-slate-600" />
              <span className="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white" />
            </button>
          </div>
        </div>
      </header>

      {/* Overlay mobile */}
      <div
        className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300 ${mobileOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
          }`}
        onClick={() => setMobileOpen(false)}
      />

      {/* Sidebar - THÈME CLAIR */}
      <aside
        className={`
          fixed left-0 top-0 h-screen w-72 
          bg-white border-r border-gray-200
          z-50 
          flex flex-col
          transform transition-all duration-300 ease-out
          ${mobileOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'}
          lg:shadow-lg lg:shadow-gray-200/50
        `}
      >

        <button
          onClick={() => setMobileOpen(false)}
          className="absolute top-4 right-4 p-2 rounded-lg bg-white/5 hover:bg-white/10 lg:hidden transition-all duration-200 active:scale-95"
          aria-label="Fermer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Logo Header - PLEINE LARGEUR CORRIGÉE */}
        <div className="w-full bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-700 overflow-hidden">
          <div className="px-3 py-4">
            <div className="flex items-center gap-2">
              <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-lg border border-white/30">
                <GraduationCap className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h1 className="text-xs font-bold text-white leading-tight">
                  Soutien
                </h1>
                <h1 className="text-xs font-bold text-white leading-tight -mt-0.5">
                  Pédagogique
                </h1>
                <p className="text-[9px] text-blue-100 leading-tight mt-0.5">
                  Universités Marocaines
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation - THÈME CLAIR */}
        <nav className="flex-1 overflow-y-auto py-5 px-3 bg-white">
          {menuItems.map((section, sectionIndex) => (
            <div key={section.section} className={sectionIndex > 0 ? 'mt-6' : ''}>
              <h3 className="px-3 mb-2 text-[11px] font-bold text-gray-500 uppercase tracking-wide">
                {section.section}
              </h3>
              <ul className="space-y-1">
                {section.items.map((item) => {
                  const isActive = pathname === item.href ||
                    (item.href !== '/' && pathname.startsWith(item.href));
                  const Icon = item.icon;

                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className={`
                          relative flex items-center gap-3 px-4 py-2.5 rounded-xl 
                          transition-all duration-200 group
                          ${isActive
                            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-600/25'
                            : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                          }
                        `}
                      >
                        {isActive && (
                          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-white rounded-r-full shadow-lg shadow-white/50" />
                        )}
                        <div className={`
                          w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200
                          ${isActive
                            ? 'bg-white/20'
                            : 'bg-blue-50 group-hover:bg-blue-100'
                          }
                        `}>
                          <Icon className={`w-[18px] h-[18px] ${isActive ? 'text-white' : 'text-blue-600'}`} />
                        </div>
                        <span className="font-medium text-[13px] flex-1">{item.label}</span>
                        {item.badge === 'AI' && (
                          <span className="px-2 py-0.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-[10px] font-bold rounded-full shadow-lg shadow-purple-500/30">
                            AI
                          </span>
                        )}
                        {item.badge === 'NEW' && (
                          <span className="px-2 py-0.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-[10px] font-bold rounded-full shadow-lg shadow-emerald-500/30">
                            NEW
                          </span>
                        )}
                        {item.badge === 'urgent' && (
                          <span className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse shadow-lg shadow-red-500/50" />
                        )}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {/* User Section */}
        {user && (
          <div className="relative p-3 border-t border-white/10 bg-gradient-to-t from-black/40 to-transparent">
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className={`
                  w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-200
                  ${showUserMenu ? 'bg-white/10' : 'hover:bg-white/5'}
                `}
              >
                <div className={`w-11 h-11 ${userRoleConfig.gradient} rounded-xl flex items-center justify-center shadow-lg flex-shrink-0`}>
                  <UserIcon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 text-left min-w-0">
                  <p className="text-sm font-semibold text-white truncate">
                    {user.nom || user.username}
                  </p>
                  <p className="text-xs text-slate-400 font-medium">
                    {roleLabels[user.role] || user.role}
                  </p>
                </div>
                <div className={`p-1.5 rounded-lg transition-all duration-200 ${showUserMenu ? 'bg-white/10' : ''}`}>
                  <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${showUserMenu ? 'rotate-180' : ''}`} />
                </div>
              </button>

              <div className={`
                absolute bottom-full left-0 right-0 mb-2 
                bg-slate-800/95 backdrop-blur-xl rounded-xl 
                shadow-2xl border border-white/10 
                overflow-hidden
                transition-all duration-200 origin-bottom
                ${showUserMenu ? 'opacity-100 scale-100' : 'opacity-0 scale-95 pointer-events-none'}
              `}>
                <div className="px-4 py-3 bg-gradient-to-r from-slate-700/50 to-slate-800/50 border-b border-white/10">
                  <p className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Compte</p>
                  <p className="text-sm font-semibold text-white mt-0.5">{user.username}</p>
                  <p className="text-xs text-slate-400 mt-0.5 truncate">{user.email}</p>
                </div>
                <div className="p-2 space-y-1">
                  <button
                    className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-300 hover:bg-white/5 hover:text-white rounded-lg transition-all duration-200"
                  >
                    <Settings className="w-4 h-4" />
                    <span className="text-sm font-medium">Paramètres</span>
                  </button>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-3 py-2.5 text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded-lg transition-all duration-200"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="text-sm font-medium">Déconnexion</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="px-6 py-3 border-t border-white/5 bg-black/30">
          <p className="text-[10px] text-slate-500 text-center font-medium">
            Version 2.0 • © 2025 PFA
          </p>
        </div>
      </aside>
    </>
  );
}
