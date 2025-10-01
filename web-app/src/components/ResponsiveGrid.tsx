"use client";

import React from "react";

interface ResponsiveGridProps {
  children: React.ReactNode;
  className?: string;
  cols?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: "sm" | "md" | "lg" | "xl";
}

const ResponsiveGrid: React.FC<ResponsiveGridProps> = ({
  children,
  className = "",
  cols = { xs: 1, sm: 2, md: 3, lg: 4, xl: 5 },
  gap = "md",
}) => {
  const gapClasses = {
    sm: "gap-2",
    md: "gap-4",
    lg: "gap-6",
    xl: "gap-8",
  };

  const gridColsClasses = {
    xs: `grid-cols-${cols.xs || 1}`,
    sm: `sm:grid-cols-${cols.sm || 2}`,
    md: `md:grid-cols-${cols.md || 3}`,
    lg: `lg:grid-cols-${cols.lg || 4}`,
    xl: `xl:grid-cols-${cols.xl || 5}`,
  };

  return (
    <div
      className={`
        grid
        ${gridColsClasses.xs}
        ${gridColsClasses.sm}
        ${gridColsClasses.md}
        ${gridColsClasses.lg}
        ${gridColsClasses.xl}
        ${gapClasses[gap]}
        ${className}
      `}
    >
      {children}
    </div>
  );
};

export default ResponsiveGrid;
