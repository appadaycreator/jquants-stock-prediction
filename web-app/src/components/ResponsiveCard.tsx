"use client";

import React from "react";

interface ResponsiveCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  variant?: "default" | "outlined" | "elevated";
  size?: "sm" | "md" | "lg";
}

const ResponsiveCard: React.FC<ResponsiveCardProps> = ({
  children,
  className = "",
  title,
  subtitle,
  actions,
  variant = "default",
  size = "md",
}) => {
  const baseClasses = "rounded-lg transition-all duration-200";
  
  const variantClasses = {
    default: "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm",
    outlined: "bg-transparent border-2 border-gray-200 dark:border-gray-700",
    elevated: "bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700",
  };

  const sizeClasses = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  return (
    <div
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {(title || subtitle || actions) && (
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            {title && (
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {subtitle}
              </p>
            )}
          </div>
          {actions && (
            <div className="ml-4 flex-shrink-0">
              {actions}
            </div>
          )}
        </div>
      )}
      
      <div className="text-gray-700 dark:text-gray-300">
        {children}
      </div>
    </div>
  );
};

export default ResponsiveCard;
