'use client';

import React from 'react';

interface SkeletonLoaderProps {
  type?: 'text' | 'card' | 'chart' | 'list' | 'table';
  lines?: number;
  height?: number;
  width?: string;
  className?: string;
}

export function SkeletonLoader({ 
  type = 'text', 
  lines = 1, 
  height = 20, 
  width = '100%',
  className = '' 
}: SkeletonLoaderProps) {
  const renderSkeleton = () => {
    switch (type) {
      case 'text':
        return (
          <div className={`animate-pulse ${className}`}>
            {Array.from({ length: lines }).map((_, index) => (
              <div
                key={index}
                className="h-4 bg-gray-300 rounded mb-2"
                style={{ 
                  width: index === lines - 1 ? '75%' : '100%',
                  height: `${height}px`
                }}
              />
            ))}
          </div>
        );

      case 'card':
        return (
          <div className={`bg-white rounded-lg p-4 shadow-sm animate-pulse ${className}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="h-4 bg-gray-300 rounded w-24"></div>
              <div className="h-4 bg-gray-300 rounded w-16"></div>
            </div>
            <div className="h-6 bg-gray-300 rounded w-32 mb-2"></div>
            <div className="h-4 bg-gray-300 rounded w-20"></div>
          </div>
        );

      case 'chart':
        return (
          <div className={`bg-white rounded-lg p-4 shadow-sm animate-pulse ${className}`}>
            <div className="h-4 bg-gray-300 rounded w-32 mb-4"></div>
            <div className="h-48 bg-gray-300 rounded"></div>
          </div>
        );

      case 'list':
        return (
          <div className={`bg-white rounded-lg shadow-sm animate-pulse ${className}`}>
            {Array.from({ length: lines }).map((_, index) => (
              <div key={index} className="p-4 border-b last:border-b-0">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-300 rounded w-24 mb-2"></div>
                    <div className="h-3 bg-gray-300 rounded w-32"></div>
                  </div>
                  <div className="text-right">
                    <div className="h-4 bg-gray-300 rounded w-16 mb-1"></div>
                    <div className="h-3 bg-gray-300 rounded w-12"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'table':
        return (
          <div className={`bg-white rounded-lg shadow-sm animate-pulse ${className}`}>
            <div className="p-4 border-b">
              <div className="h-4 bg-gray-300 rounded w-32"></div>
            </div>
            <div className="divide-y">
              {Array.from({ length: lines }).map((_, index) => (
                <div key={index} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-300 rounded"></div>
                      <div>
                        <div className="h-4 bg-gray-300 rounded w-20 mb-1"></div>
                        <div className="h-3 bg-gray-300 rounded w-16"></div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="h-4 bg-gray-300 rounded w-16 mb-1"></div>
                      <div className="h-3 bg-gray-300 rounded w-12"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return (
          <div 
            className={`animate-pulse bg-gray-300 rounded ${className}`}
            style={{ height: `${height}px`, width }}
          />
        );
    }
  };

  return renderSkeleton();
}

// 特殊化されたスケルトンコンポーネント
export function ChartSkeleton({ className = '' }: { className?: string }) {
  return <SkeletonLoader type="chart" className={className} />;
}

export function CardSkeleton({ className = '' }: { className?: string }) {
  return <SkeletonLoader type="card" className={className} />;
}

export function ListSkeleton({ lines = 5, className = '' }: { lines?: number; className?: string }) {
  return <SkeletonLoader type="list" lines={lines} className={className} />;
}

export function TableSkeleton({ lines = 10, className = '' }: { lines?: number; className?: string }) {
  return <SkeletonLoader type="table" lines={lines} className={className} />;
}

// プログレッシブローディング用のスケルトン
export function ProgressiveSkeleton({ 
  isLoading, 
  children, 
  fallback,
  className = '' 
}: { 
  isLoading: boolean; 
  children: React.ReactNode; 
  fallback?: React.ReactNode;
  className?: string;
}) {
  if (isLoading) {
    return (
      <div className={className}>
        {fallback || <SkeletonLoader type="card" />}
      </div>
    );
  }

  return <>{children}</>;
}
