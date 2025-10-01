"use client";

import React from "react";
import ResponsiveHeader from "./ResponsiveHeader";

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  className?: string;
}

const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ 
  children, 
  className = "" 
}) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      <ResponsiveHeader />
      
      <main className={`
        container-responsive py-6
        ${className}
      `}>
        {children}
      </main>
    </div>
  );
};

export default ResponsiveLayout;
