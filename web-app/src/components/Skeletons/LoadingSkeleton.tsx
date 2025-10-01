/**
 * ローディングスケルトンコンポーネント
 * データ読み込み中のUI表示
 */

import React from "react";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <div className={`animate-pulse bg-gray-200 rounded ${className}`} />
  );
}

export function TableSkeleton() {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-4 gap-4">
        <Skeleton className="h-4" />
        <Skeleton className="h-4" />
        <Skeleton className="h-4" />
        <Skeleton className="h-4" />
      </div>
      {[...Array(5)].map((_, i) => (
        <div key={i} className="grid grid-cols-4 gap-4">
          <Skeleton className="h-4" />
          <Skeleton className="h-4" />
          <Skeleton className="h-4" />
          <Skeleton className="h-4" />
        </div>
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-4 w-24" />
      </div>
      <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <Skeleton className="h-8 w-8 mx-auto mb-2" />
          <Skeleton className="h-4 w-24" />
        </div>
      </div>
    </div>
  );
}

export function KpiCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <Skeleton className="h-5 w-20" />
        <Skeleton className="h-4 w-4 rounded-full" />
      </div>
      <Skeleton className="h-8 w-16 mb-2" />
      <Skeleton className="h-4 w-24" />
    </div>
  );
}

export function PredictionsViewSkeleton() {
  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-24" />
      </div>
      
      {/* KPIカード */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <KpiCardSkeleton key={i} />
        ))}
      </div>
      
      {/* テーブル */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <Skeleton className="h-6 w-32 mb-4" />
          <TableSkeleton />
        </div>
      </div>
      
      {/* チャート */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <ChartSkeleton />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <ChartSkeleton />
        </div>
      </div>
    </div>
  );
}

export function OverviewSkeleton() {
  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-10 w-20" />
      </div>
      
      {/* サマリーカード */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <KpiCardSkeleton key={i} />
        ))}
      </div>
      
      {/* メインチャート */}
      <div className="bg-white rounded-lg shadow p-6">
        <ChartSkeleton />
      </div>
      
      {/* モデル比較 */}
      <div className="bg-white rounded-lg shadow p-6">
        <Skeleton className="h-6 w-32 mb-4" />
        <TableSkeleton />
      </div>
    </div>
  );
}
