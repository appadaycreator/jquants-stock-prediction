/**
 * ナビゲーション設定
 * ルーティングマップとメニュー構成を一元管理
 */

export interface NavigationItem {
  href: string;
  label: string;
  icon: string;
  description: string;
  status: 'active' | 'development' | 'coming_soon' | 'deprecated';
  category: 'main' | 'analysis' | 'investment' | 'settings' | 'help';
  requiresAuth?: boolean;
  mobile?: boolean;
  desktop?: boolean;
}

export const navigationConfig: NavigationItem[] = [
  // メイン機能
  {
    href: '/',
    label: 'ダッシュボード',
    icon: '🏠',
    description: 'メインダッシュボード',
    status: 'active',
    category: 'main',
    mobile: true,
    desktop: true,
  },
  {
    href: '/today',
    label: '今日の指示',
    icon: '🎯',
    description: '本日の売買候補と指示',
    status: 'active',
    category: 'main',
    mobile: true,
    desktop: true,
  },
  {
    href: '/personal-investment',
    label: '個人投資',
    icon: '💰',
    description: '個人投資ポートフォリオ管理',
    status: 'active',
    category: 'investment',
    mobile: true,
    desktop: true,
  },

  // 分析機能
  {
    href: '/dashboard',
    label: '詳細分析',
    icon: '📊',
    description: '詳細な分析結果',
    status: 'active',
    category: 'analysis',
    mobile: true,
    desktop: true,
  },
  {
    href: '/five-min-routine',
    label: '5分ルーティン',
    icon: '⚡',
    description: '効率的な投資分析ルーティン',
    status: 'active',
    category: 'analysis',
    mobile: true,
    desktop: true,
  },
  {
    href: '/reports',
    label: 'レポート',
    icon: '📈',
    description: '詳細レポート',
    status: 'active',
    category: 'analysis',
    mobile: true,
    desktop: true,
  },

  // リスク管理
  {
    href: '/risk',
    label: 'リスク管理',
    icon: '🛡️',
    description: 'リスク管理と設定',
    status: 'active',
    category: 'investment',
    mobile: true,
    desktop: true,
  },

  // 設定・ヘルプ
  {
    href: '/settings',
    label: '設定',
    icon: '⚙️',
    description: 'システム設定',
    status: 'active',
    category: 'settings',
    mobile: true,
    desktop: true,
  },
  {
    href: '/usage',
    label: '使い方',
    icon: '❓',
    description: '使用方法ガイド',
    status: 'active',
    category: 'help',
    mobile: true,
    desktop: true,
  },
  {
    href: '/troubleshooting',
    label: 'トラブルシューティング',
    icon: '🔧',
    description: '問題解決ガイド',
    status: 'active',
    category: 'help',
    mobile: true,
    desktop: true,
  },

  // 開発中・非表示機能
  {
    href: '/analysis-progress',
    label: '分析状況',
    icon: '🔄',
    description: '分析の進行状況',
    status: 'development',
    category: 'analysis',
    mobile: false,
    desktop: false,
  },
  {
    href: '/logs',
    label: 'ログ',
    icon: '📝',
    description: 'システムログ',
    status: 'development',
    category: 'settings',
    mobile: false,
    desktop: false,
  },
];

/**
 * カテゴリ別のナビゲーション取得
 */
export function getNavigationByCategory(category: NavigationItem['category']): NavigationItem[] {
  return navigationConfig.filter(item => item.category === category);
}

/**
 * アクティブなナビゲーション取得
 */
export function getActiveNavigation(): NavigationItem[] {
  return navigationConfig.filter(item => item.status === 'active');
}

/**
 * モバイル用ナビゲーション取得
 */
export function getMobileNavigation(): NavigationItem[] {
  return navigationConfig.filter(item => item.mobile && item.status === 'active');
}

/**
 * デスクトップ用ナビゲーション取得
 */
export function getDesktopNavigation(): NavigationItem[] {
  return navigationConfig.filter(item => item.desktop && item.status === 'active');
}

/**
 * メインカテゴリのナビゲーション取得
 */
export function getMainNavigation(): NavigationItem[] {
  return navigationConfig.filter(item => item.category === 'main' && item.status === 'active');
}

/**
 * 分析カテゴリのナビゲーション取得
 */
export function getAnalysisNavigation(): NavigationItem[] {
  return navigationConfig.filter(item => item.category === 'analysis' && item.status === 'active');
}

/**
 * 投資カテゴリのナビゲーション取得
 */
export function getInvestmentNavigation(): NavigationItem[] {
  return navigationConfig.filter(item => item.category === 'investment' && item.status === 'active');
}

/**
 * 設定カテゴリのナビゲーション取得
 */
export function getSettingsNavigation(): NavigationItem[] {
  return navigationConfig.filter(item => item.category === 'settings' && item.status === 'active');
}

/**
 * ヘルプカテゴリのナビゲーション取得
 */
export function getHelpNavigation(): NavigationItem[] {
  return navigationConfig.filter(item => item.category === 'help' && item.status === 'active');
}

/**
 * ルートの存在チェック
 */
export function isValidRoute(href: string): boolean {
  return navigationConfig.some(item => item.href === href && item.status === 'active');
}

/**
 * ルートの情報取得
 */
export function getRouteInfo(href: string): NavigationItem | null {
  return navigationConfig.find(item => item.href === href) || null;
}

/**
 * 開発中ページのリダイレクト設定
 */
export const developmentRedirects: Record<string, string> = {
  '/analysis-progress': '/dashboard',
  '/logs': '/settings',
};

/**
 * 非推奨ページのリダイレクト設定
 */
export const deprecatedRedirects: Record<string, string> = {
  // 必要に応じて追加
};
