import React from 'react';
import { cn } from '../../utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'soft' | 'default';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  loading?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  className,
  variant = 'primary',
  size = 'md',
  color = 'primary',
  loading = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  disabled,
  children,
  ...props
}) => {
  const baseClasses = `
    inline-flex items-center justify-center font-medium 
    transition-all duration-200 ease-out
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none
    active:scale-[0.98]
  `;
  
  const variantClasses = {
    primary: {
      primary: 'bg-primary text-white hover:bg-primary-700 focus:ring-primary shadow-sm hover:shadow-md hover:-translate-y-0.5',
      secondary: 'bg-secondary text-white hover:bg-secondary/90 focus:ring-secondary shadow-sm hover:shadow-md hover:-translate-y-0.5',
      success: 'bg-success text-white hover:bg-success/90 focus:ring-success shadow-sm hover:shadow-md hover:-translate-y-0.5',
      warning: 'bg-warning text-white hover:bg-warning/90 focus:ring-warning shadow-sm hover:shadow-md hover:-translate-y-0.5',
      error: 'bg-error text-white hover:bg-error/90 focus:ring-error shadow-sm hover:shadow-md hover:-translate-y-0.5',
      info: 'bg-info text-white hover:bg-info/90 focus:ring-info shadow-sm hover:shadow-md hover:-translate-y-0.5',
    },
    secondary: {
      primary: 'bg-primary-50 text-primary hover:bg-primary-100 focus:ring-primary border border-primary/20',
      secondary: 'bg-slate-100 text-slate-700 hover:bg-slate-200 focus:ring-slate-500 border border-slate-200',
      success: 'bg-success/10 text-success hover:bg-success/20 focus:ring-success border border-success/20',
      warning: 'bg-warning/10 text-warning hover:bg-warning/20 focus:ring-warning border border-warning/20',
      error: 'bg-error/10 text-error hover:bg-error/20 focus:ring-error border border-error/20',
      info: 'bg-info/10 text-info hover:bg-info/20 focus:ring-info border border-info/20',
    },
    outline: {
      primary: 'border-2 border-primary text-primary hover:bg-primary hover:text-white focus:ring-primary',
      secondary: 'border-2 border-slate-300 text-slate-600 hover:bg-slate-600 hover:text-white focus:ring-slate-500',
      success: 'border-2 border-success text-success hover:bg-success hover:text-white focus:ring-success',
      warning: 'border-2 border-warning text-warning hover:bg-warning hover:text-white focus:ring-warning',
      error: 'border-2 border-error text-error hover:bg-error hover:text-white focus:ring-error',
      info: 'border-2 border-info text-info hover:bg-info hover:text-white focus:ring-info',
    },
    ghost: {
      primary: 'text-primary hover:bg-primary/10 focus:ring-primary',
      secondary: 'text-slate-600 hover:bg-slate-100 focus:ring-slate-500',
      success: 'text-success hover:bg-success/10 focus:ring-success',
      warning: 'text-warning hover:bg-warning/10 focus:ring-warning',
      error: 'text-error hover:bg-error/10 focus:ring-error',
      info: 'text-info hover:bg-info/10 focus:ring-info',
    },
    soft: {
      primary: 'bg-primary/10 text-primary hover:bg-primary/20 focus:ring-primary',
      secondary: 'bg-slate-100 text-slate-600 hover:bg-slate-200 focus:ring-slate-500',
      success: 'bg-success/10 text-success hover:bg-success/20 focus:ring-success',
      warning: 'bg-warning/10 text-warning hover:bg-warning/20 focus:ring-warning',
      error: 'bg-error/10 text-error hover:bg-error/20 focus:ring-error',
      info: 'bg-info/10 text-info hover:bg-info/20 focus:ring-info',
    },
    default: {
      primary: 'bg-primary text-white hover:bg-primary/90 focus:ring-primary',
      secondary: 'bg-secondary text-white hover:bg-secondary/90 focus:ring-secondary',
      success: 'bg-success text-white hover:bg-success/90 focus:ring-success',
      warning: 'bg-warning text-white hover:bg-warning/90 focus:ring-warning',
      error: 'bg-error text-white hover:bg-error/90 focus:ring-error',
      info: 'bg-info text-white hover:bg-info/90 focus:ring-info',
    },
  };
  
  const sizeClasses = {
    xs: 'px-2.5 py-1 text-xs rounded-md gap-1.5',
    sm: 'px-3 py-1.5 text-sm rounded-lg gap-2',
    md: 'px-4 py-2 text-sm rounded-lg gap-2',
    lg: 'px-5 py-2.5 text-base rounded-xl gap-2.5',
    xl: 'px-6 py-3 text-base rounded-xl gap-3',
  };

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant][color],
        sizeClasses[size],
        fullWidth && 'w-full',
        loading && 'relative text-transparent',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="absolute animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      {!loading && leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
      <span>{children}</span>
      {!loading && rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
    </button>
  );
};

export default Button;