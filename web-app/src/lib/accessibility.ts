/**
 * アクセシビリティユーティリティ
 * キーボード操作、ariaラベル、コントラスト対応
 */

interface AccessibilityConfig {
  enableKeyboardNavigation: boolean;
  enableScreenReader: boolean;
  enableHighContrast: boolean;
  enableFocusManagement: boolean;
  enableAriaLabels: boolean;
}

interface FocusTrapOptions {
  container: HTMLElement;
  firstFocusable?: HTMLElement;
  lastFocusable?: HTMLElement;
  onEscape?: () => void;
}

class AccessibilityManager {
  private config: AccessibilityConfig;
  private focusHistory: HTMLElement[] = [];
  private currentFocusIndex = -1;
  private focusTrap: FocusTrapOptions | null = null;

  constructor(config: AccessibilityConfig) {
    this.config = config;
    this.initAccessibility();
  }

  /**
   * アクセシビリティの初期化
   */
  private initAccessibility() {
    if (typeof window === 'undefined') return;

    // キーボードナビゲーション
    if (this.config.enableKeyboardNavigation) {
      this.setupKeyboardNavigation();
    }

    // フォーカス管理
    if (this.config.enableFocusManagement) {
      this.setupFocusManagement();
    }

    // 高コントラストモード
    if (this.config.enableHighContrast) {
      this.setupHighContrastMode();
    }

    // スクリーンリーダー対応
    if (this.config.enableScreenReader) {
      this.setupScreenReaderSupport();
    }
  }

  /**
   * キーボードナビゲーションの設定
   */
  private setupKeyboardNavigation() {
    document.addEventListener('keydown', (event) => {
      // Tabキーでフォーカス移動
      if (event.key === 'Tab') {
        this.handleTabNavigation(event);
      }

      // Enter/Spaceキーでアクティベート
      if (event.key === 'Enter' || event.key === ' ') {
        this.handleActivation(event);
      }

      // Escapeキーでフォーカストラップ解除
      if (event.key === 'Escape') {
        this.handleEscapeKey(event);
      }

      // 矢印キーでカスタムナビゲーション
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
        this.handleArrowNavigation(event);
      }
    });
  }

  /**
   * Tabナビゲーションの処理
   */
  private handleTabNavigation(event: KeyboardEvent) {
    const focusableElements = this.getFocusableElements();
    const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);

    if (event.shiftKey) {
      // Shift+Tab: 前の要素へ
      if (currentIndex > 0) {
        event.preventDefault();
        focusableElements[currentIndex - 1].focus();
      }
    } else {
      // Tab: 次の要素へ
      if (currentIndex < focusableElements.length - 1) {
        event.preventDefault();
        focusableElements[currentIndex + 1].focus();
      }
    }
  }

  /**
   * アクティベーションの処理
   */
  private handleActivation(event: KeyboardEvent) {
    const target = event.target as HTMLElement;
    
    if (target.getAttribute('role') === 'button' || 
        target.tagName === 'BUTTON' ||
        target.getAttribute('tabindex') === '0') {
      event.preventDefault();
      target.click();
    }
  }

  /**
   * Escapeキーの処理
   */
  private handleEscapeKey(event: KeyboardEvent) {
    if (this.focusTrap?.onEscape) {
      event.preventDefault();
      this.focusTrap.onEscape();
    }
  }

  /**
   * 矢印キーナビゲーションの処理
   */
  private handleArrowNavigation(event: KeyboardEvent) {
    const target = event.target as HTMLElement;
    const role = target.getAttribute('role');
    
    if (role === 'tablist' || role === 'menu' || role === 'grid') {
      event.preventDefault();
      this.navigateWithArrows(target, event.key);
    }
  }

  /**
   * 矢印キーでのナビゲーション
   */
  private navigateWithArrows(container: HTMLElement, direction: string) {
    const focusableElements = this.getFocusableElements(container);
    const currentIndex = focusableElements.indexOf(document.activeElement as HTMLElement);

    let nextIndex = currentIndex;

    switch (direction) {
      case 'ArrowUp':
        nextIndex = Math.max(0, currentIndex - 1);
        break;
      case 'ArrowDown':
        nextIndex = Math.min(focusableElements.length - 1, currentIndex + 1);
        break;
      case 'ArrowLeft':
        nextIndex = Math.max(0, currentIndex - 1);
        break;
      case 'ArrowRight':
        nextIndex = Math.min(focusableElements.length - 1, currentIndex + 1);
        break;
    }

    if (nextIndex !== currentIndex) {
      focusableElements[nextIndex].focus();
    }
  }

  /**
   * フォーカス管理の設定
   */
  private setupFocusManagement() {
    document.addEventListener('focusin', (event) => {
      const target = event.target as HTMLElement;
      this.focusHistory.push(target);
      this.currentFocusIndex = this.focusHistory.length - 1;
    });

    document.addEventListener('focusout', (event) => {
      // フォーカスが外れた時の処理
      this.handleFocusOut(event);
    });
  }

  /**
   * フォーカスアウトの処理
   */
  private handleFocusOut(event: FocusEvent) {
    const target = event.target as HTMLElement;
    const relatedTarget = event.relatedTarget as HTMLElement;

    // フォーカスが完全に外れた場合
    if (!relatedTarget || !document.contains(relatedTarget)) {
      this.announceToScreenReader('フォーカスが外れました');
    }
  }

  /**
   * 高コントラストモードの設定
   */
  private setupHighContrastMode() {
    // システムの高コントラスト設定を検出
    if (window.matchMedia('(prefers-contrast: high)').matches) {
      document.body.classList.add('high-contrast');
      this.announceToScreenReader('高コントラストモードが有効です');
    }

    // 高コントラスト設定の変更を監視
    window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
      if (e.matches) {
        document.body.classList.add('high-contrast');
        this.announceToScreenReader('高コントラストモードが有効になりました');
      } else {
        document.body.classList.remove('high-contrast');
        this.announceToScreenReader('高コントラストモードが無効になりました');
      }
    });
  }

  /**
   * スクリーンリーダー対応の設定
   */
  private setupScreenReaderSupport() {
    // ライブリージョンの作成
    this.createLiveRegion();
    
    // スキップリンクの追加
    this.addSkipLinks();
  }

  /**
   * ライブリージョンの作成
   */
  private createLiveRegion() {
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    liveRegion.id = 'live-region';
    document.body.appendChild(liveRegion);
  }

  /**
   * スキップリンクの追加
   */
  private addSkipLinks() {
    const skipLinks = document.createElement('div');
    skipLinks.className = 'skip-links';
    skipLinks.innerHTML = `
      <a href="#main-content" class="skip-link">メインコンテンツにスキップ</a>
      <a href="#navigation" class="skip-link">ナビゲーションにスキップ</a>
      <a href="#search" class="skip-link">検索にスキップ</a>
    `;
    document.body.insertBefore(skipLinks, document.body.firstChild);
  }

  /**
   * フォーカストラップの設定
   */
  setFocusTrap(options: FocusTrapOptions) {
    this.focusTrap = options;
    const focusableElements = this.getFocusableElements(options.container);
    
    if (focusableElements.length > 0) {
      const firstElement = options.firstFocusable || focusableElements[0];
      const lastElement = options.lastFocusable || focusableElements[focusableElements.length - 1];
      
      firstElement.focus();
      
      // フォーカストラップのイベントリスナー
      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === 'Tab') {
          if (event.shiftKey && document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          } else if (!event.shiftKey && document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      };
      
      options.container.addEventListener('keydown', handleKeyDown);
    }
  }

  /**
   * フォーカストラップの解除
   */
  removeFocusTrap() {
    this.focusTrap = null;
  }

  /**
   * フォーカス可能な要素の取得
   */
  private getFocusableElements(container: HTMLElement = document.body): HTMLElement[] {
    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[role="button"]',
      '[role="link"]',
      '[role="menuitem"]',
      '[role="tab"]'
    ];

    const elements = container.querySelectorAll(focusableSelectors.join(', '));
    return Array.from(elements) as HTMLElement[];
  }

  /**
   * スクリーンリーダーへの通知
   */
  announceToScreenReader(message: string) {
    const liveRegion = document.getElementById('live-region');
    if (liveRegion) {
      liveRegion.textContent = message;
      // メッセージをクリア（同じメッセージを再度読み上げるため）
      setTimeout(() => {
        liveRegion.textContent = '';
      }, 1000);
    }
  }

  /**
   * ARIAラベルの設定
   */
  setAriaLabel(element: HTMLElement, label: string, description?: string) {
    if (this.config.enableAriaLabels) {
      element.setAttribute('aria-label', label);
      if (description) {
        element.setAttribute('aria-describedby', description);
      }
    }
  }

  /**
   * コントラスト比の計算
   */
  calculateContrastRatio(color1: string, color2: string): number {
    const rgb1 = this.hexToRgb(color1);
    const rgb2 = this.hexToRgb(color2);
    
    if (!rgb1 || !rgb2) return 0;

    const luminance1 = this.getLuminance(rgb1);
    const luminance2 = this.getLuminance(rgb2);
    
    const lighter = Math.max(luminance1, luminance2);
    const darker = Math.min(luminance1, luminance2);
    
    return (lighter + 0.05) / (darker + 0.05);
  }

  /**
   * 16進数カラーをRGBに変換
   */
  private hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }

  /**
   * 相対輝度の計算
   */
  private getLuminance(rgb: { r: number; g: number; b: number }): number {
    const { r, g, b } = rgb;
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  }

  /**
   * アクセシビリティレポートの生成
   */
  generateAccessibilityReport(): any {
    const focusableElements = this.getFocusableElements();
    const elementsWithAriaLabels = focusableElements.filter(el => 
      el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby')
    );
    const elementsWithRoles = focusableElements.filter(el => 
      el.hasAttribute('role')
    );

    return {
      totalFocusableElements: focusableElements.length,
      elementsWithAriaLabels: elementsWithAriaLabels.length,
      elementsWithRoles: elementsWithRoles.length,
      accessibilityScore: Math.round(
        ((elementsWithAriaLabels.length + elementsWithRoles.length) / 
         (focusableElements.length * 2)) * 100
      ),
      recommendations: this.generateAccessibilityRecommendations()
    };
  }

  /**
   * アクセシビリティ改善の推奨事項を生成
   */
  private generateAccessibilityRecommendations(): string[] {
    const recommendations: string[] = [];
    const report = this.generateAccessibilityReport();

    if (report.accessibilityScore < 70) {
      recommendations.push('ARIAラベルとロールの追加を推奨します。');
    }

    if (report.elementsWithAriaLabels < report.totalFocusableElements * 0.5) {
      recommendations.push('フォーカス可能な要素の50%以上にARIAラベルを追加してください。');
    }

    return recommendations;
  }

  /**
   * クリーンアップ
   */
  cleanup() {
    this.focusHistory = [];
    this.currentFocusIndex = -1;
    this.focusTrap = null;
  }
}

// デフォルト設定
const defaultConfig: AccessibilityConfig = {
  enableKeyboardNavigation: true,
  enableScreenReader: true,
  enableHighContrast: true,
  enableFocusManagement: true,
  enableAriaLabels: true
};

export const accessibilityManager = new AccessibilityManager(defaultConfig);
export default AccessibilityManager;
export type { AccessibilityConfig, FocusTrapOptions };
