"use client";

// アクセシビリティ設定
export const ACCESSIBILITY_CONFIG = {
  focusRing: true,
  screenReader: true,
  highContrast: true,
  keyboardNavigation: true,
  ariaLabels: {
    tour: 'ガイドツアー',
    tooltip: 'ツールチップ',
    checklist: 'チェックリスト',
    help: 'ヘルプ',
    glossary: '用語集'
  }
};

// ARIA属性の生成
export function generateAriaAttributes(type: string, options: Record<string, any> = {}) {
  const baseAttributes = {
    role: 'button',
    tabIndex: 0,
    'aria-label': ACCESSIBILITY_CONFIG.ariaLabels[type as keyof typeof ACCESSIBILITY_CONFIG.ariaLabels] || type
  };

  switch (type) {
    case 'tour':
      return {
        ...baseAttributes,
        role: 'dialog',
        'aria-modal': true,
        'aria-labelledby': 'tour-title',
        'aria-describedby': 'tour-description'
      };
    
    case 'tooltip':
      return {
        ...baseAttributes,
        role: 'tooltip',
        'aria-live': 'polite' as const
      };
    
    case 'checklist':
      return {
        ...baseAttributes,
        role: 'list',
        'aria-label': 'チェックリスト'
      };
    
    case 'help':
      return {
        ...baseAttributes,
        role: 'dialog',
        'aria-modal': true,
        'aria-labelledby': 'help-title'
      };
    
    case 'glossary':
      return {
        ...baseAttributes,
        role: 'dialog',
        'aria-modal': true,
        'aria-labelledby': 'glossary-title'
      };
    
    default:
      return baseAttributes;
  }
}

// フォーカス管理
export class FocusManager {
  private static instance: FocusManager;
  private focusStack: HTMLElement[] = [];
  private currentFocus: HTMLElement | null = null;

  private constructor() {}

  static getInstance(): FocusManager {
    if (!FocusManager.instance) {
      FocusManager.instance = new FocusManager();
    }
    return FocusManager.instance;
  }

  // フォーカスを保存
  saveFocus(): void {
    this.currentFocus = document.activeElement as HTMLElement;
    if (this.currentFocus) {
      this.focusStack.push(this.currentFocus);
    }
  }

  // フォーカスを復元
  restoreFocus(): void {
    if (this.focusStack.length > 0) {
      const previousFocus = this.focusStack.pop();
      if (previousFocus && previousFocus.focus) {
        previousFocus.focus();
      }
    }
  }

  // フォーカスを特定の要素に移動
  focusElement(element: HTMLElement): void {
    if (element && element.focus) {
      element.focus();
    }
  }

  // フォーカストラップ（モーダル内でのフォーカス制限）
  trapFocus(container: HTMLElement): () => void {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
          }
        }
      }
    };

    container.addEventListener('keydown', handleTabKey);
    
    // クリーンアップ関数を返す
    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  }

  // フォーカススタックをクリア
  clearFocusStack(): void {
    this.focusStack = [];
    this.currentFocus = null;
  }
}

// スクリーンリーダー対応
export class ScreenReaderManager {
  private static instance: ScreenReaderManager;
  private announcementElement: HTMLElement | null = null;

  private constructor() {
    this.createAnnouncementElement();
  }

  static getInstance(): ScreenReaderManager {
    if (!ScreenReaderManager.instance) {
      ScreenReaderManager.instance = new ScreenReaderManager();
    }
    return ScreenReaderManager.instance;
  }

  private createAnnouncementElement(): void {
    if (typeof window === 'undefined') return;

    this.announcementElement = document.createElement('div');
    this.announcementElement.setAttribute('aria-live', 'polite');
    this.announcementElement.setAttribute('aria-atomic', 'true');
    this.announcementElement.className = 'sr-only';
    this.announcementElement.style.cssText = `
      position: absolute;
      left: -10000px;
      width: 1px;
      height: 1px;
      overflow: hidden;
    `;
    document.body.appendChild(this.announcementElement);
  }

  // アナウンスを読み上げ
  announce(message: string, priority: 'polite' | 'assertive' = 'polite'): void {
    if (!this.announcementElement) return;

    this.announcementElement.setAttribute('aria-live', priority);
    this.announcementElement.textContent = message;
    
    // 短時間後にクリア
    setTimeout(() => {
      if (this.announcementElement) {
        this.announcementElement.textContent = '';
      }
    }, 1000);
  }

  // ガイドステップのアナウンス
  announceStep(stepTitle: string, stepDescription: string): void {
    const message = `ガイドステップ: ${stepTitle}. ${stepDescription}`;
    this.announce(message, 'assertive');
  }

  // チェックリスト項目のアナウンス
  announceChecklistItem(itemTitle: string, completed: boolean): void {
    const status = completed ? '完了' : '未完了';
    const message = `チェックリスト項目: ${itemTitle} - ${status}`;
    this.announce(message);
  }

  // ツールチップのアナウンス
  announceTooltip(content: string): void {
    this.announce(`ツールチップ: ${content}`);
  }
}

// キーボードナビゲーション
export class KeyboardNavigation {
  private static instance: KeyboardNavigation;
  private shortcuts: Map<string, () => void> = new Map();

  private constructor() {}

  static getInstance(): KeyboardNavigation {
    if (!KeyboardNavigation.instance) {
      KeyboardNavigation.instance = new KeyboardNavigation();
    }
    return KeyboardNavigation.instance;
  }

  // ショートカットを登録
  registerShortcut(key: string, handler: () => void): () => void {
    this.shortcuts.set(key, handler);
    
    return () => {
      this.shortcuts.delete(key);
    };
  }

  // キーボードイベントを処理
  handleKeyDown = (event: KeyboardEvent): void => {
    const key = event.key;
    const handler = this.shortcuts.get(key);
    
    if (handler) {
      event.preventDefault();
      event.stopPropagation();
      handler();
    }
  };

  // イベントリスナーを開始
  start(): void {
    document.addEventListener('keydown', this.handleKeyDown);
  }

  // イベントリスナーを停止
  stop(): void {
    document.removeEventListener('keydown', this.handleKeyDown);
  }

  // 全ショートカットをクリア
  clear(): void {
    this.shortcuts.clear();
  }
}

// 高コントラストモードの検出
export function detectHighContrastMode(): boolean {
  if (typeof window === 'undefined') return false;
  
  // Windows High Contrast Mode の検出
  const mediaQuery = window.matchMedia('(-ms-high-contrast: active)');
  if (mediaQuery.matches) return true;
  
  // その他の高コントラストモードの検出
  const computedStyle = window.getComputedStyle(document.body);
  const backgroundColor = computedStyle.backgroundColor;
  const color = computedStyle.color;
  
  // 背景色と文字色が同じ場合は高コントラストモードの可能性
  return backgroundColor === color;
}

// 色覚異常対応
export function detectColorBlindness(): 'normal' | 'protanopia' | 'deuteranopia' | 'tritanopia' {
  if (typeof window === 'undefined') return 'normal';
  
  // 色覚異常の検出（簡易版）
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) return 'normal';
  
  // テスト用の色を描画
  ctx.fillStyle = '#ff0000';
  ctx.fillRect(0, 0, 1, 1);
  
  const imageData = ctx.getImageData(0, 0, 1, 1);
  const data = imageData.data;
  
  // 色の値を分析（簡易版）
  if (data[0] === 255 && data[1] === 0 && data[2] === 0) {
    return 'normal';
  }
  
  return 'normal'; // 実際の実装ではより詳細な検出が必要
}

// アクセシビリティユーティリティ
export const accessibilityUtils = {
  // フォーカス管理
  focusManager: FocusManager.getInstance(),
  
  // スクリーンリーダー管理
  screenReader: ScreenReaderManager.getInstance(),
  
  // キーボードナビゲーション
  keyboard: KeyboardNavigation.getInstance(),
  
  // 高コントラストモード検出
  isHighContrast: detectHighContrastMode(),
  
  // 色覚異常検出
  colorBlindness: detectColorBlindness(),
  
  // ARIA属性生成
  generateAriaAttributes,
  
  // アクセシビリティ設定
  config: ACCESSIBILITY_CONFIG
};

// シングルトンインスタンス
export const focusManager = accessibilityUtils.focusManager;
export const screenReader = accessibilityUtils.screenReader;
export const keyboardNavigation = accessibilityUtils.keyboard;
