"use client";

import React from 'react';
import { HelpCircle, Info, AlertTriangle, CheckCircle, X } from 'lucide-react';
import EnhancedTooltip from './EnhancedTooltip';

export type InfoIconType = 'info' | 'warning' | 'success' | 'error' | 'help';

interface InfoIconProps {
  content: React.ReactNode;
  type?: InfoIconType;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
  persistent?: boolean;
}

const InfoIcon: React.FC<InfoIconProps> = ({
  content,
  type = 'info',
  size = 'md',
  className = '',
  position = 'top',
  persistent = false,
}) => {
  const getIcon = () => {
    const iconClass = {
      sm: 'h-3 w-3',
      md: 'h-4 w-4',
      lg: 'h-5 w-5',
    }[size];

    switch (type) {
      case 'warning':
        return <AlertTriangle className={`${iconClass} text-themed-warning`} />;
      case 'success':
        return <CheckCircle className={`${iconClass} text-themed-success`} />;
      case 'error':
        return <X className={`${iconClass} text-themed-error`} />;
      case 'help':
        return <HelpCircle className={`${iconClass} text-themed-info`} />;
      default:
        return <Info className={`${iconClass} text-themed-info`} />;
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'p-1';
      case 'md':
        return 'p-1.5';
      case 'lg':
        return 'p-2';
      default:
        return 'p-1.5';
    }
  };

  return (
    <EnhancedTooltip
      content={content}
      type={type}
      position={position}
      persistent={persistent}
      className={className}
    >
      <div
        className={`
          inline-flex items-center justify-center rounded-full
          bg-themed-background-secondary hover:bg-themed-background-tertiary
          text-themed-text-secondary hover:text-themed-text-primary
          transition-colors duration-200 cursor-help
          ${getSizeStyles()}
        `}
        role="button"
        tabIndex={0}
        aria-label="詳細情報を表示"
      >
        {getIcon()}
      </div>
    </EnhancedTooltip>
  );
};

export default InfoIcon;
