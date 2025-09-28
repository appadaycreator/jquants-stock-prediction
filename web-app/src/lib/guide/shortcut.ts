"use client";

import { useEffect, useCallback } from 'react';

// キーボードショートカット設定
export const SHORTCUT_KEYS = {
  HELP: 'F1',
  GLOSSARY: 'KeyG',
  TOUR: 'KeyT',
  ESCAPE: 'Escape',
  NEXT: 'ArrowRight',
  PREV: 'ArrowLeft',
  ENTER: 'Enter',
  SPACE: 'Space'
} as const;

// ショートカットハンドラー型
export type ShortcutHandler = (event: KeyboardEvent) => void;

// ショートカットマネージャークラス
export class ShortcutManager {
  private static instance: ShortcutManager;
  private handlers: Map<string, ShortcutHandler[]> = new Map();
  private isEnabled: boolean = true;

  private constructor() {}

  static getInstance(): ShortcutManager {
    if (!ShortcutManager.instance) {
      ShortcutManager.instance = new ShortcutManager();
    }
    return ShortcutManager.instance;
  }

  // ショートカット登録
  register(key: string, handler: ShortcutHandler): () => void {
    if (!this.handlers.has(key)) {
      this.handlers.set(key, []);
    }
    
    const handlers = this.handlers.get(key)!;
    handlers.push(handler);

    // 登録解除関数を返す
    return () => {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    };
  }

  // ショートカット削除
  unregister(key: string, handler: ShortcutHandler): void {
    const handlers = this.handlers.get(key);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  // 有効/無効切り替え
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  // キーボードイベント処理
  private handleKeyDown = (event: KeyboardEvent): void => {
    if (!this.isEnabled) return;

    // 入力フィールドでのショートカット無効化
    const target = event.target as HTMLElement;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.contentEditable === 'true') {
      return;
    }

    const key = event.code;
    const handlers = this.handlers.get(key);
    
    if (handlers && handlers.length > 0) {
      event.preventDefault();
      event.stopPropagation();
      
      handlers.forEach(handler => {
        try {
          handler(event);
        } catch (error) {
          console.error('Shortcut handler error:', error);
        }
      });
    }
  };

  // イベントリスナー登録
  start(): void {
    document.addEventListener('keydown', this.handleKeyDown);
  }

  // イベントリスナー削除
  stop(): void {
    document.removeEventListener('keydown', this.handleKeyDown);
  }

  // 全ショートカットクリア
  clear(): void {
    this.handlers.clear();
  }
}

// シングルトンインスタンス
export const shortcutManager = ShortcutManager.getInstance();

// React フック
export function useShortcut(
  key: string,
  handler: ShortcutHandler,
  deps: React.DependencyList = []
): void {
  const memoizedHandler = useCallback(handler, deps);

  useEffect(() => {
    const unsubscribe = shortcutManager.register(key, memoizedHandler);
    return unsubscribe;
  }, [key, memoizedHandler]);
}

// 特定のショートカット用フック
export function useHelpShortcut(handler: () => void): void {
  useShortcut(SHORTCUT_KEYS.HELP, handler);
}

export function useGlossaryShortcut(handler: () => void): void {
  useShortcut(SHORTCUT_KEYS.GLOSSARY, handler);
}

export function useTourShortcut(handler: () => void): void {
  useShortcut(SHORTCUT_KEYS.TOUR, handler);
  
  // Ctrl/Cmd + T でもツアー開始
  useShortcut('KeyT', (event) => {
    if (event.ctrlKey || event.metaKey) {
      handler();
    }
  });
}

export function useEscapeShortcut(handler: () => void): void {
  useShortcut(SHORTCUT_KEYS.ESCAPE, handler);
}

export function useNavigationShortcuts(
  onNext: () => void,
  onPrev: () => void,
  onEnter: () => void
): void {
  useShortcut(SHORTCUT_KEYS.NEXT, onNext);
  useShortcut(SHORTCUT_KEYS.PREV, onPrev);
  useShortcut(SHORTCUT_KEYS.ENTER, onEnter);
  useShortcut(SHORTCUT_KEYS.SPACE, onEnter);
}

// ガイド専用ショートカット
export function useGuideShortcuts(
  onHelp: () => void,
  onGlossary: () => void,
  onTour: () => void,
  onNext: () => void,
  onPrev: () => void,
  onSkip: () => void
): void {
  useHelpShortcut(onHelp);
  useGlossaryShortcut(onGlossary);
  useTourShortcut(onTour);
  useNavigationShortcuts(onNext, onPrev, onNext);
  useEscapeShortcut(onSkip);
}

// ショートカットの初期化
export function initializeShortcuts(): void {
  shortcutManager.start();
}

// ショートカットのクリーンアップ
export function cleanupShortcuts(): void {
  shortcutManager.stop();
  shortcutManager.clear();
}

// ショートカットの有効/無効切り替え
export function setShortcutsEnabled(enabled: boolean): void {
  shortcutManager.setEnabled(enabled);
}

// ショートカットヘルプ表示用のデータ
export const SHORTCUT_HELP = [
  {
    key: 'F1',
    description: 'クイックヘルプを開く',
    category: 'ナビゲーション'
  },
  {
    key: 'G',
    description: '用語集を開く',
    category: 'ナビゲーション'
  },
  {
    key: 'T',
    description: 'ガイドツアーを開始',
    category: 'ナビゲーション'
  },
  {
    key: '← →',
    description: 'ツアーの前/次へ移動',
    category: 'ツアー'
  },
  {
    key: 'Enter / Space',
    description: 'ツアーの次へ進む',
    category: 'ツアー'
  },
  {
    key: 'Esc',
    description: 'ツアーをスキップ',
    category: 'ツアー'
  }
];
