"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

// ChartDataContextProviderの代替実装
const ChartDataContext = createContext<any>(null);

export function ChartDataProviderOverride({ children }: { children: React.ReactNode }) {
  // 無限ループ検出を無効化して、通常の動作に戻す
  const contextValue = {
    // ダミーデータを提供
    data: [],
    loading: false,
    error: null,
    // 無限ループを防ぐためのメソッド
    setData: () => {},
    setLoading: () => {},
    setError: () => {},
  };

  return (
    <ChartDataContext.Provider value={contextValue}>
      {children}
    </ChartDataContext.Provider>
  );
}

export function useChartData() {
  const context = useContext(ChartDataContext);
  if (!context) {
    return {
      data: [],
      loading: false,
      error: null,
      setData: () => {},
      setLoading: () => {},
      setError: () => {},
    };
  }
  return context;
}
