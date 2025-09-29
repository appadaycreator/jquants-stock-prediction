"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

export type RiskTolerance = "LOW" | "MEDIUM" | "HIGH";

export interface UserProfile {
  capitalAmount: number;
  riskTolerance: RiskTolerance;
  preferredSectors: string[];
  esgPreference: boolean;
  maxPositions?: number;
  excludeSymbols?: string[];
}

const DEFAULT_PROFILE: UserProfile = {
  capitalAmount: 1000000,
  riskTolerance: "MEDIUM",
  preferredSectors: [],
  esgPreference: false,
  maxPositions: 8,
  excludeSymbols: [],
};

interface UserProfileContextValue {
  profile: UserProfile;
  setProfile: (updater: UserProfile | ((prev: UserProfile) => UserProfile)) => void;
  resetProfile: () => void;
}

const UserProfileContext = createContext<UserProfileContextValue | null>(null);

const STORAGE_KEY = "user_profile";

export function UserProfileProvider({ children }: { children: React.ReactNode }) {
  const [profile, setProfileState] = useState<UserProfile>(DEFAULT_PROFILE);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as UserProfile;
        // 簡易バリデーション
        if (typeof parsed.capitalAmount === "number" && parsed.capitalAmount >= 0) {
          setProfileState({ ...DEFAULT_PROFILE, ...parsed });
        }
      }
    } catch {}
  }, []);

  const setProfile = (updater: UserProfile | ((prev: UserProfile) => UserProfile)) => {
    setProfileState(prev => {
      const next = typeof updater === "function" ? (updater as any)(prev) : updater;
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {}
      return next;
    });
  };

  const resetProfile = () => setProfile(DEFAULT_PROFILE);

  const value = useMemo(() => ({ profile, setProfile, resetProfile }), [profile]);

  return (
    <UserProfileContext.Provider value={value}>{children}</UserProfileContext.Provider>
  );
}

export function useUserProfile(): UserProfileContextValue {
  const ctx = useContext(UserProfileContext);
  if (!ctx) {
    throw new Error("useUserProfile must be used within UserProfileProvider");
  }
  return ctx;
}


