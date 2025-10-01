"use client";

import React from "react";

interface ResponsiveTableProps {
  children: React.ReactNode;
  className?: string;
  striped?: boolean;
  hover?: boolean;
  bordered?: boolean;
  size?: "sm" | "md" | "lg";
}

const ResponsiveTable: React.FC<ResponsiveTableProps> = ({
  children,
  className = "",
  striped = false,
  hover = true,
  bordered = false,
  size = "md",
}) => {
  const sizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg",
  };

  const tableClasses = `
    w-full
    ${sizeClasses[size]}
    ${striped ? "divide-y divide-gray-200 dark:divide-gray-700" : ""}
    ${bordered ? "border border-gray-200 dark:border-gray-700" : ""}
    ${className}
  `;

  return (
    <div className="overflow-x-auto -mx-4 sm:mx-0">
      <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
        <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
          <table className={tableClasses}>
            {children}
          </table>
        </div>
      </div>
    </div>
  );
};

interface ResponsiveTableHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const ResponsiveTableHeader: React.FC<ResponsiveTableHeaderProps> = ({
  children,
  className = "",
}) => {
  return (
    <thead className="bg-gray-50 dark:bg-gray-800">
      <tr className={className}>
        {children}
      </tr>
    </thead>
  );
};

interface ResponsiveTableBodyProps {
  children: React.ReactNode;
  className?: string;
  striped?: boolean;
  hover?: boolean;
}

export const ResponsiveTableBody: React.FC<ResponsiveTableBodyProps> = ({
  children,
  className = "",
  striped = false,
  hover = true,
}) => {
  return (
    <tbody
      className={`
        bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700
        ${striped ? "divide-y divide-gray-200 dark:divide-gray-700" : ""}
        ${className}
      `}
    >
      {children}
    </tbody>
  );
};

interface ResponsiveTableRowProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

export const ResponsiveTableRow: React.FC<ResponsiveTableRowProps> = ({
  children,
  className = "",
  hover = true,
  onClick,
}) => {
  return (
    <tr
      className={`
        ${hover ? "hover:bg-gray-50 dark:hover:bg-gray-800" : ""}
        ${onClick ? "cursor-pointer" : ""}
        transition-colors duration-150
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </tr>
  );
};

interface ResponsiveTableCellProps {
  children: React.ReactNode;
  className?: string;
  header?: boolean;
  align?: "left" | "center" | "right";
  colSpan?: number;
}

export const ResponsiveTableCell: React.FC<ResponsiveTableCellProps> = ({
  children,
  className = "",
  header = false,
  align = "left",
  colSpan,
}) => {
  const alignClasses = {
    left: "text-left",
    center: "text-center",
    right: "text-right",
  };

  const baseClasses = `
    px-6 py-4 whitespace-nowrap
    ${alignClasses[align]}
    ${header 
      ? "text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider" 
      : "text-sm text-gray-900 dark:text-gray-100"
    }
  `;

  const Component = header ? "th" : "td";

  return (
    <Component
      className={`${baseClasses} ${className}`}
      colSpan={colSpan}
    >
      {children}
    </Component>
  );
};

export default ResponsiveTable;
