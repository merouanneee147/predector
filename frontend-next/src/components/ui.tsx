import { ReactNode } from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';

// ============================================================
// 📊 Stat Card - Carte de statistiques améliorée
// ============================================================

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBgColor?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconColor = 'text-blue-600',
  iconBgColor = 'bg-blue-100',
  trend,
  className = '',
}: StatCardProps) {
  return (
    <div className={`bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6 hover:shadow-lg hover:border-slate-300 transition-all duration-300 group ${className}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-slate-500 mb-1 truncate">{title}</p>
          <p className="text-2xl sm:text-3xl font-bold text-slate-800 tracking-tight">{value}</p>
          {subtitle && (
            <p className="text-xs sm:text-sm text-slate-400 mt-1.5 truncate">{subtitle}</p>
          )}
          {trend && (
            <div className={`inline-flex items-center gap-1 mt-2 text-xs sm:text-sm font-medium ${trend.isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
              {trend.isPositive ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              {Math.abs(trend.value)}%
            </div>
          )}
        </div>
        <div className={`p-3 sm:p-3.5 rounded-xl ${iconBgColor} group-hover:scale-110 transition-transform duration-300 flex-shrink-0`}>
          <Icon className={`w-5 h-5 sm:w-6 sm:h-6 ${iconColor}`} />
        </div>
      </div>
    </div>
  );
}

// ============================================================
// 🏷️ Badge - Labels et tags
// ============================================================

interface BadgeProps {
  children: ReactNode;
  variant?: 'excellence' | 'regulier' | 'progression' | 'difficulte' | 'risque' | 'default' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
}

export function Badge({ children, variant = 'default', size = 'md', icon: Icon }: BadgeProps) {
  const variants = {
    excellence: 'bg-gradient-to-r from-emerald-50 to-emerald-100 text-emerald-700 border border-emerald-200',
    regulier: 'bg-gradient-to-r from-blue-50 to-blue-100 text-blue-700 border border-blue-200',
    progression: 'bg-gradient-to-r from-amber-50 to-amber-100 text-amber-700 border border-amber-200',
    difficulte: 'bg-gradient-to-r from-orange-50 to-orange-100 text-orange-700 border border-orange-200',
    risque: 'bg-gradient-to-r from-red-50 to-red-100 text-red-700 border border-red-200',
    success: 'bg-emerald-100 text-emerald-700 border border-emerald-200',
    warning: 'bg-amber-100 text-amber-700 border border-amber-200',
    danger: 'bg-red-100 text-red-700 border border-red-200',
    info: 'bg-blue-100 text-blue-700 border border-blue-200',
    default: 'bg-slate-100 text-slate-700 border border-slate-200',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs sm:text-sm',
    lg: 'px-3 py-1.5 text-sm',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 font-semibold rounded-lg ${variants[variant]} ${sizes[size]}`}>
      {Icon && <Icon className="w-3.5 h-3.5" />}
      {children}
    </span>
  );
}

export function getProfilVariant(profil: string): BadgeProps['variant'] {
  const profilLower = profil.toLowerCase();
  if (profilLower.includes('excellence')) return 'excellence';
  if (profilLower.includes('regulier') || profilLower.includes('régulier')) return 'regulier';
  if (profilLower.includes('progression')) return 'progression';
  if (profilLower.includes('difficulte') || profilLower.includes('difficulté')) return 'difficulte';
  if (profilLower.includes('risque') || profilLower.includes('critique')) return 'risque';
  return 'default';
}

// ============================================================
// ⏳ Loading Spinner
// ============================================================

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

export function LoadingSpinner({ size = 'md', text }: LoadingSpinnerProps) {
  const sizes = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 animate-fadeIn">
      <div className={`${sizes[size]} border-blue-200 border-t-blue-600 rounded-full animate-spin`} />
      {text && <p className="mt-4 text-slate-500 font-medium text-sm sm:text-base">{text}</p>}
    </div>
  );
}

// ============================================================
// 📭 Empty State
// ============================================================

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center px-4 animate-fadeIn">
      {Icon && (
        <div className="w-16 h-16 sm:w-20 sm:h-20 bg-slate-100 rounded-2xl flex items-center justify-center mb-4">
          <Icon className="w-8 h-8 sm:w-10 sm:h-10 text-slate-400" />
        </div>
      )}
      <h3 className="text-lg sm:text-xl font-semibold text-slate-700">{title}</h3>
      {description && <p className="text-slate-500 mt-2 max-w-md text-sm sm:text-base">{description}</p>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

// ============================================================
// 📄 Page Header
// ============================================================

interface PageHeaderProps {
  title: string;
  description?: string;
  action?: ReactNode;
  breadcrumb?: Array<{ label: string; href?: string }>;
}

export function PageHeader({ title, description, action, breadcrumb }: PageHeaderProps) {
  return (
    <div className="mb-6 sm:mb-8 animate-fadeIn">
      {breadcrumb && breadcrumb.length > 0 && (
        <nav className="flex items-center gap-2 text-sm text-slate-500 mb-3">
          {breadcrumb.map((item, index) => (
            <span key={index} className="flex items-center gap-2">
              {index > 0 && <span>/</span>}
              {item.href ? (
                <a href={item.href} className="hover:text-blue-600 transition-colors">
                  {item.label}
                </a>
              ) : (
                <span className="text-slate-700 font-medium">{item.label}</span>
              )}
            </span>
          ))}
        </nav>
      )}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-800 tracking-tight">{title}</h1>
          {description && <p className="text-slate-500 mt-1.5 text-sm sm:text-base lg:text-lg">{description}</p>}
        </div>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>
    </div>
  );
}

// ============================================================
// 📊 Progress Bar
// ============================================================

interface ProgressBarProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'red' | 'amber' | 'auto';
  showLabel?: boolean;
  className?: string;
}

export function ProgressBar({ 
  value, 
  max = 100, 
  size = 'md', 
  color = 'auto',
  showLabel = false,
  className = ''
}: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100);
  
  const sizes = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  };

  const getColor = () => {
    if (color !== 'auto') {
      const colors = {
        blue: 'bg-gradient-to-r from-blue-500 to-blue-600',
        green: 'bg-gradient-to-r from-emerald-500 to-emerald-600',
        red: 'bg-gradient-to-r from-red-500 to-red-600',
        amber: 'bg-gradient-to-r from-amber-500 to-amber-600',
      };
      return colors[color];
    }
    // Auto color based on value
    if (percentage >= 80) return 'bg-gradient-to-r from-red-500 to-red-600';
    if (percentage >= 60) return 'bg-gradient-to-r from-orange-500 to-orange-600';
    if (percentage >= 40) return 'bg-gradient-to-r from-amber-500 to-amber-600';
    return 'bg-gradient-to-r from-emerald-500 to-emerald-600';
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className={`flex-1 bg-slate-200 rounded-full overflow-hidden ${sizes[size]}`}>
        <div 
          className={`h-full rounded-full transition-all duration-500 ${getColor()}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-sm font-semibold text-slate-700 min-w-[3rem] text-right">
          {percentage.toFixed(0)}%
        </span>
      )}
    </div>
  );
}

// ============================================================
// 🃏 Card Component
// ============================================================

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({ children, className = '', hover = true, padding = 'md' }: CardProps) {
  const paddingClasses = {
    none: '',
    sm: 'p-3 sm:p-4',
    md: 'p-4 sm:p-6',
    lg: 'p-6 sm:p-8',
  };

  return (
    <div className={`
      bg-white rounded-2xl shadow-sm border border-slate-200
      ${hover ? 'hover:shadow-lg hover:border-slate-300 transition-all duration-300' : ''}
      ${paddingClasses[padding]}
      ${className}
    `}>
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  iconColor?: string;
  iconBgColor?: string;
  action?: ReactNode;
}

export function CardHeader({ title, subtitle, icon: Icon, iconColor = 'text-blue-600', iconBgColor = 'bg-blue-100', action }: CardHeaderProps) {
  return (
    <div className="flex items-center justify-between gap-4 mb-4 sm:mb-6">
      <div className="flex items-center gap-3 min-w-0">
        {Icon && (
          <div className={`p-2 sm:p-2.5 rounded-xl ${iconBgColor} flex-shrink-0`}>
            <Icon className={`w-4 h-4 sm:w-5 sm:h-5 ${iconColor}`} />
          </div>
        )}
        <div className="min-w-0">
          <h2 className="text-base sm:text-lg font-semibold text-slate-800 truncate">{title}</h2>
          {subtitle && <p className="text-xs sm:text-sm text-slate-500 truncate">{subtitle}</p>}
        </div>
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  );
}

// ============================================================
// 🔘 Button Component
// ============================================================

interface ButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  className?: string;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  iconPosition = 'left',
  loading = false,
  disabled = false,
  fullWidth = false,
  className = '',
  onClick,
  type = 'button',
}: ButtonProps) {
  const variants = {
    primary: 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/25 hover:shadow-xl',
    secondary: 'bg-slate-100 text-slate-700 hover:bg-slate-200',
    danger: 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 shadow-lg shadow-red-500/25',
    success: 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white hover:from-emerald-600 hover:to-emerald-700 shadow-lg shadow-emerald-500/25',
    ghost: 'bg-transparent text-slate-600 hover:bg-slate-100',
  };

  const sizes = {
    sm: 'px-3 py-2 text-xs sm:text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        inline-flex items-center justify-center gap-2 
        font-medium rounded-xl transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]}
        ${sizes[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
    >
      {loading ? (
        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : Icon && iconPosition === 'left' ? (
        <Icon className="w-4 h-4" />
      ) : null}
      {children}
      {!loading && Icon && iconPosition === 'right' && <Icon className="w-4 h-4" />}
    </button>
  );
}

// ============================================================
// 📥 Input Component
// ============================================================

interface InputProps {
  label?: string;
  placeholder?: string;
  type?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
  icon?: LucideIcon;
  className?: string;
  disabled?: boolean;
  required?: boolean;
}

export function Input({
  label,
  placeholder,
  type = 'text',
  value,
  onChange,
  error,
  icon: Icon,
  className = '',
  disabled = false,
  required = false,
}: InputProps) {
  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-slate-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            <Icon className="w-5 h-5" />
          </div>
        )}
        <input
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          className={`
            w-full px-4 py-3 
            ${Icon ? 'pl-11' : ''}
            bg-white border rounded-xl
            text-slate-800 placeholder:text-slate-400
            focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500
            transition-all duration-200
            disabled:bg-slate-50 disabled:cursor-not-allowed
            ${error ? 'border-red-300 focus:ring-red-500/20 focus:border-red-500' : 'border-slate-200'}
          `}
        />
      </div>
      {error && <p className="mt-1.5 text-sm text-red-600">{error}</p>}
    </div>
  );
}

// ============================================================
// 🔽 Select Component
// ============================================================

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  label?: string;
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export function Select({
  label,
  options,
  value,
  onChange,
  placeholder = 'Sélectionner...',
  className = '',
  disabled = false,
}: SelectProps) {
  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-slate-700 mb-2">{label}</label>
      )}
      <select
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        disabled={disabled}
        className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 cursor-pointer disabled:bg-slate-50 disabled:cursor-not-allowed"
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

// ============================================================
// 📊 Skeleton Loaders
// ============================================================

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="h-4 bg-slate-200 rounded w-24 mb-3" />
          <div className="h-8 bg-slate-200 rounded w-20 mb-2" />
          <div className="h-3 bg-slate-200 rounded w-32" />
        </div>
        <div className="w-12 h-12 bg-slate-200 rounded-xl" />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden animate-pulse">
      <div className="p-6 border-b border-slate-100">
        <div className="h-6 bg-slate-200 rounded w-48" />
      </div>
      <div className="divide-y divide-slate-100">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="px-6 py-4 flex items-center gap-4">
            <div className="w-10 h-10 bg-slate-200 rounded-full" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-slate-200 rounded w-32" />
              <div className="h-3 bg-slate-200 rounded w-24" />
            </div>
            <div className="h-6 bg-slate-200 rounded w-20" />
          </div>
        ))}
      </div>
    </div>
  );
}
