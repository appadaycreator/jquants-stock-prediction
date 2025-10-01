"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface Settings {
  prediction: {
    days: number;
  };
  model: {
    type: string;
    primary_model: string;
    compare_models: boolean;
    auto_retrain: boolean;
    retrain_frequency: string;
  };
  data: {
    refresh_interval: string;
    max_data_points: number;
    include_technical_indicators: boolean;
  };
  features: {
    selected: string[];
  };
  ui: {
    theme: string;
    refresh_rate: number;
    show_tooltips: boolean;
  };
}

interface SettingsContextType {
  settings: Settings;
  updateSettings: (newSettings: Partial<Settings>) => void;
  loadSettings: () => void;
  saveSettings: () => void;
  resetSettings: () => void;
  isLoading: boolean;
  isSaving: boolean;
}

const defaultSettings: Settings = {
  prediction: {
    days: 30,
  },
  model: {
    type: "all",
    primary_model: "xgboost",
    compare_models: true,
    auto_retrain: false,
    retrain_frequency: "weekly",
  },
  data: {
    refresh_interval: "daily",
    max_data_points: 1000,
    include_technical_indicators: true,
  },
  features: {
    selected: ["sma_5", "sma_10", "sma_25", "sma_50", "rsi", "macd"],
  },
  ui: {
    theme: "light",
    refresh_rate: 30,
    show_tooltips: true,
  },
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      const savedSettings = localStorage.getItem("jquants-settings");
      if (savedSettings) {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings(prev => ({
          ...prev,
          ...parsedSettings,
        }));
      }
    } catch (error) {
      console.error("設定の読み込みに失敗:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveSettings = async () => {
    try {
      setIsSaving(true);
      localStorage.setItem("jquants-settings", JSON.stringify(settings));
    } catch (error) {
      console.error("設定保存エラー:", error);
      throw error;
    } finally {
      setIsSaving(false);
    }
  };

  const updateSettings = (newSettings: Partial<Settings>) => {
    setSettings(prev => ({
      ...prev,
      ...newSettings,
    }));
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
  };

  useEffect(() => {
    loadSettings();
  }, []);

  return (
    <SettingsContext.Provider
      value={{
        settings,
        updateSettings,
        loadSettings,
        saveSettings,
        resetSettings,
        isLoading,
        isSaving,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return context;
}
