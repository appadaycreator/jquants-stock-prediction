"use client";

import { useState, useEffect } from 'react';
import { GuideState } from '@/components/guide/TourProvider';

// ローカルストレージキー
const STORAGE_KEYS = {
  FIRST_VISIT: 'guide_first_visit',
  COMPLETED_STEPS: 'guide_completed_steps',
  TOUR_COMPLETED: 'guide_tour_completed',
  GUIDE_DISABLED: 'guide_disabled',
  CURRENT_STEP: 'guide_current_step',
  CHECKLIST_PROGRESS: 'guide_checklist_progress',
  USER_PREFERENCES: 'guide_user_preferences'
};

// ユーザー設定
export interface UserPreferences {
  autoStart: boolean;
  showTooltips: boolean;
  showProgress: boolean;
  keyboardNavigation: boolean;
  highContrast: boolean;
  language: string;
}

// チェックリスト進捗
export interface ChecklistProgress {
  completedItems: string[];
  totalItems: number;
  isCompleted: boolean;
  completedAt?: string;
}

// ガイドストアクラス
export class GuideStore {
  private static instance: GuideStore;
  private listeners: Set<() => void> = new Set();

  private constructor() {}

  static getInstance(): GuideStore {
    if (!GuideStore.instance) {
      GuideStore.instance = new GuideStore();
    }
    return GuideStore.instance;
  }

  // リスナー登録
  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  // リスナー通知
  private notify(): void {
    this.listeners.forEach(listener => listener());
  }

  // 初回訪問フラグ
  get isFirstVisit(): boolean {
    return localStorage.getItem(STORAGE_KEYS.FIRST_VISIT) !== 'false';
  }

  set isFirstVisit(value: boolean) {
    localStorage.setItem(STORAGE_KEYS.FIRST_VISIT, value.toString());
    this.notify();
  }

  // 完了ステップ
  get completedSteps(): string[] {
    const stored = localStorage.getItem(STORAGE_KEYS.COMPLETED_STEPS);
    return stored ? JSON.parse(stored) : [];
  }

  set completedSteps(steps: string[]) {
    localStorage.setItem(STORAGE_KEYS.COMPLETED_STEPS, JSON.stringify(steps));
    this.notify();
  }

  addCompletedStep(stepId: string): void {
    const current = this.completedSteps;
    if (!current.includes(stepId)) {
      this.completedSteps = [...current, stepId];
    }
  }

  // ツアー完了フラグ
  get isTourCompleted(): boolean {
    return localStorage.getItem(STORAGE_KEYS.TOUR_COMPLETED) === 'true';
  }

  set isTourCompleted(value: boolean) {
    localStorage.setItem(STORAGE_KEYS.TOUR_COMPLETED, value.toString());
    this.notify();
  }

  // ガイド無効化フラグ
  get isGuideDisabled(): boolean {
    return localStorage.getItem(STORAGE_KEYS.GUIDE_DISABLED) === 'true';
  }

  set isGuideDisabled(value: boolean) {
    localStorage.setItem(STORAGE_KEYS.GUIDE_DISABLED, value.toString());
    this.notify();
  }

  // 現在のステップ
  get currentStep(): string | null {
    return localStorage.getItem(STORAGE_KEYS.CURRENT_STEP);
  }

  set currentStep(stepId: string | null) {
    if (stepId) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_STEP, stepId);
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_STEP);
    }
    this.notify();
  }

  // チェックリスト進捗
  get checklistProgress(): ChecklistProgress {
    const stored = localStorage.getItem(STORAGE_KEYS.CHECKLIST_PROGRESS);
    return stored ? JSON.parse(stored) : {
      completedItems: [],
      totalItems: 4,
      isCompleted: false
    };
  }

  set checklistProgress(progress: ChecklistProgress) {
    localStorage.setItem(STORAGE_KEYS.CHECKLIST_PROGRESS, JSON.stringify(progress));
    this.notify();
  }

  addChecklistItem(itemId: string): void {
    const current = this.checklistProgress;
    if (!current.completedItems.includes(itemId)) {
      const updated = {
        ...current,
        completedItems: [...current.completedItems, itemId],
        isCompleted: current.completedItems.length + 1 >= current.totalItems
      };
      if (updated.isCompleted) {
        updated.completedAt = new Date().toISOString();
      }
      this.checklistProgress = updated;
    }
  }

  removeChecklistItem(itemId: string): void {
    const current = this.checklistProgress;
    const updated = {
      ...current,
      completedItems: current.completedItems.filter(id => id !== itemId),
      isCompleted: false,
      completedAt: undefined
    };
    this.checklistProgress = updated;
  }

  // ユーザー設定
  get userPreferences(): UserPreferences {
    const stored = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES);
    return stored ? JSON.parse(stored) : {
      autoStart: true,
      showTooltips: true,
      showProgress: true,
      keyboardNavigation: true,
      highContrast: false,
      language: 'ja'
    };
  }

  set userPreferences(preferences: UserPreferences) {
    localStorage.setItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(preferences));
    this.notify();
  }

  updateUserPreferences(updates: Partial<UserPreferences>): void {
    const current = this.userPreferences;
    this.userPreferences = { ...current, ...updates };
  }

  // ガイド状態の取得
  getGuideState(): GuideState {
    return {
      isActive: false,
      currentStep: this.currentStep,
      completedSteps: this.completedSteps,
      isFirstVisit: this.isFirstVisit,
      isTourCompleted: this.isTourCompleted,
      isGuideDisabled: this.isGuideDisabled
    };
  }

  // ガイド状態の更新
  updateGuideState(updates: Partial<GuideState>): void {
    if (updates.isFirstVisit !== undefined) {
      this.isFirstVisit = updates.isFirstVisit;
    }
    if (updates.completedSteps !== undefined) {
      this.completedSteps = updates.completedSteps;
    }
    if (updates.isTourCompleted !== undefined) {
      this.isTourCompleted = updates.isTourCompleted;
    }
    if (updates.isGuideDisabled !== undefined) {
      this.isGuideDisabled = updates.isGuideDisabled;
    }
    if (updates.currentStep !== undefined) {
      this.currentStep = updates.currentStep;
    }
  }

  // ガイドのリセット
  resetGuide(): void {
    localStorage.removeItem(STORAGE_KEYS.FIRST_VISIT);
    localStorage.removeItem(STORAGE_KEYS.COMPLETED_STEPS);
    localStorage.removeItem(STORAGE_KEYS.TOUR_COMPLETED);
    localStorage.removeItem(STORAGE_KEYS.GUIDE_DISABLED);
    localStorage.removeItem(STORAGE_KEYS.CURRENT_STEP);
    localStorage.removeItem(STORAGE_KEYS.CHECKLIST_PROGRESS);
    this.notify();
  }

  // 特定のステップが完了しているかチェック
  isStepCompleted(stepId: string): boolean {
    return this.completedSteps.includes(stepId);
  }

  // チェックリスト項目が完了しているかチェック
  isChecklistItemCompleted(itemId: string): boolean {
    return this.checklistProgress.completedItems.includes(itemId);
  }

  // ガイドの進行状況を取得
  getProgress(): { completed: number; total: number; percentage: number } {
    const completed = this.completedSteps.length;
    const total = 10; // デフォルトのステップ数
    return {
      completed,
      total,
      percentage: Math.round((completed / total) * 100)
    };
  }

  // チェックリストの進行状況を取得
  getChecklistProgress(): { completed: number; total: number; percentage: number } {
    const progress = this.checklistProgress;
    return {
      completed: progress.completedItems.length,
      total: progress.totalItems,
      percentage: Math.round((progress.completedItems.length / progress.totalItems) * 100)
    };
  }

  // ガイドの統計情報
  getStats(): {
    totalSteps: number;
    completedSteps: number;
    completionRate: number;
    checklistItems: number;
    completedChecklistItems: number;
    checklistCompletionRate: number;
    isFirstTimeUser: boolean;
    lastActivity?: string;
  } {
    const guideProgress = this.getProgress();
    const checklistProgress = this.getChecklistProgress();
    
    return {
      totalSteps: guideProgress.total,
      completedSteps: guideProgress.completed,
      completionRate: guideProgress.percentage,
      checklistItems: checklistProgress.total,
      completedChecklistItems: checklistProgress.completed,
      checklistCompletionRate: checklistProgress.percentage,
      isFirstTimeUser: this.isFirstVisit,
      lastActivity: this.checklistProgress.completedAt
    };
  }
}

// シングルトンインスタンス
export const guideStore = GuideStore.getInstance();

// フック用のヘルパー関数
export function useGuideStore() {
  const [state, setState] = useState(guideStore.getGuideState());
  
  useEffect(() => {
    const unsubscribe = guideStore.subscribe(() => {
      setState(guideStore.getGuideState());
    });
    
    return unsubscribe;
  }, []);

  return {
    ...state,
    store: guideStore
  };
}

