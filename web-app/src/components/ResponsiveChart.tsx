"use client";

import React, { useEffect, useRef, useState } from "react";

interface ResponsiveChartProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  height?: number | "auto";
  aspectRatio?: number;
  loading?: boolean;
  error?: string | null;
  actions?: React.ReactNode;
}

const ResponsiveChart: React.FC<ResponsiveChartProps> = ({
  children,
  className = "",
  title,
  subtitle,
  height = "auto",
  aspectRatio = 16 / 9,
  loading = false,
  error = null,
  actions,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });

  // コンテナサイズの監視
  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setContainerSize({ width, height });
      }
    };

    updateSize();
    window.addEventListener("resize", updateSize);
    return () => window.removeEventListener("resize", updateSize);
  }, []);

  const chartHeight = height === "auto" 
    ? Math.max(200, containerSize.width / aspectRatio)
    : height;

  return (
    <div
      ref={containerRef}
      className={`
        bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700
        shadow-sm overflow-hidden
        ${className}
      `}
    >
      {/* ヘッダー */}
      {(title || subtitle || actions) && (
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {title && (
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
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
        </div>
      )}

      {/* チャートコンテンツ */}
      <div className="relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white dark:bg-gray-800 bg-opacity-75 z-10">
            <div className="flex flex-col items-center space-y-2">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-sm text-gray-600 dark:text-gray-400">読み込み中...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center p-8">
            <div className="text-center">
              <div className="text-red-500 text-4xl mb-2">⚠️</div>
              <p className="text-red-600 dark:text-red-400 font-medium">エラーが発生しました</p>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{error}</p>
            </div>
          </div>
        )}

        {!loading && !error && (
          <div
            className="w-full"
            style={{ height: chartHeight }}
          >
            {children}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResponsiveChart;
