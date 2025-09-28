import { GuideStep } from '../../components/guide/TourProvider';

// ガイド設定
export interface GuideConfig {
  version: string;
  enabled: boolean;
  autoStart: boolean;
  showProgress: boolean;
  allowSkip: boolean;
  keyboardNavigation: boolean;
  steps: GuideStep[];
}

// デフォルトガイド設定
export const DEFAULT_GUIDE_CONFIG: GuideConfig = {
  version: '1.0.0',
  enabled: true,
  autoStart: true,
  showProgress: true,
  allowSkip: true,
  keyboardNavigation: true,
  steps: []
};

// ツアーステップ定義
export const TOUR_STEPS: GuideStep[] = [
  {
    id: 'welcome',
    target: '[data-guide-target="welcome"]',
    title: 'ようこそ！',
    body: 'J-Quants株価予測システムへようこそ。3分で主要機能を案内します。',
    placement: 'auto',
    page: '/',
    next: 'navigation'
  },
  {
    id: 'navigation',
    target: '[data-guide-target="navigation"]',
    title: 'ナビゲーション',
    body: '各ページへの移動はここから。予測・モデル・分析・設定を切り替えできます。',
    placement: 'bottom',
    page: '/',
    next: 'dashboard-overview'
  },
  {
    id: 'dashboard-overview',
    target: '[data-guide-target="dashboard-overview"]',
    title: 'ダッシュボード概要',
    body: '今日の投資指示と主要KPIが表示されます。まずはここを確認しましょう。',
    placement: 'auto',
    page: '/',
    next: 'kpi-metrics'
  },
  {
    id: 'kpi-metrics',
    target: '[data-guide-target="kpi-metrics"]',
    title: '主要指標の見方',
    body: 'MAE（平均絶対誤差）・R²（決定係数）・予測精度を確認。低いMAEと高いR²が理想的。',
    placement: 'auto',
    page: '/',
    next: 'candidate-cards'
  },
  {
    id: 'candidate-cards',
    target: '[data-guide-target="candidate-cards"]',
    title: '候補銘柄カード',
    body: '推奨銘柄とリスク情報を表示。カードをクリックして詳細分析に進めます。',
    placement: 'auto',
    page: '/',
    next: 'model-comparison'
  },
  {
    id: 'model-comparison',
    target: '[data-guide-target="model-comparison"]',
    title: 'モデル比較',
    body: '複数モデルの性能を比較。総合評価→詳細指標の順で確認しましょう。',
    placement: 'auto',
    page: '/',
    next: 'analysis-features'
  },
  {
    id: 'analysis-features',
    target: '[data-guide-target="analysis-features"]',
    title: '分析機能',
    body: '特徴量重要度・残差分析・相関分析でモデルの信頼性を確認できます。',
    placement: 'auto',
    page: '/',
    next: 'settings-config'
  },
  {
    id: 'settings-config',
    target: '[data-guide-target="settings-config"]',
    title: '設定',
    body: '実行時刻・通知先・しきい値を設定。定期的な分析実行に必要です。',
    placement: 'auto',
    page: '/',
    next: 'help-support'
  },
  {
    id: 'help-support',
    target: '[data-guide-target="help-support"]',
    title: 'ヘルプ・サポート',
    body: '困った時はF1キーまたは「？」ボタンでクイックヘルプを表示できます。',
    placement: 'auto',
    page: '/',
    next: 'completion'
  },
  {
    id: 'completion',
    target: '[data-guide-target="completion"]',
    title: '完了！',
    body: 'お疲れ様でした！これで主要機能を理解できました。明日からは自動案内しません。',
    placement: 'auto',
    page: '/'
  }
];

// ページ別ツアーステップ
export const PAGE_TOUR_STEPS: Record<string, GuideStep[]> = {
  '/': TOUR_STEPS,
  '/predictions': [
    {
      id: 'predictions-overview',
      target: '[data-guide-target="predictions-overview"]',
      title: '予測結果画面',
      body: '実際値と予測値の比較グラフを確認できます。',
      placement: 'auto',
      page: '/predictions',
      next: 'predictions-chart'
    },
    {
      id: 'predictions-chart',
      target: '[data-guide-target="predictions-chart"]',
      title: '予測チャート',
      body: '時系列での予測精度を視覚的に確認。青線が実際値、赤線が予測値です。',
      placement: 'auto',
      page: '/predictions',
      next: 'predictions-scatter'
    },
    {
      id: 'predictions-scatter',
      target: '[data-guide-target="predictions-scatter"]',
      title: '散布図分析',
      body: '予測値と実際値の相関を確認。対角線に近いほど精度が高いです。',
      placement: 'auto',
      page: '/predictions'
    }
  ],
  '/models': [
    {
      id: 'models-overview',
      target: '[data-guide-target="models-overview"]',
      title: 'モデル比較画面',
      body: '複数の機械学習モデルの性能を比較できます。',
      placement: 'auto',
      page: '/models',
      next: 'models-ranking'
    },
    {
      id: 'models-ranking',
      target: '[data-guide-target="models-ranking"]',
      title: '性能ランキング',
      body: 'MAE、RMSE、R²で自動ランキング。最優秀モデルがハイライト表示されます。',
      placement: 'auto',
      page: '/models',
      next: 'models-details'
    },
    {
      id: 'models-details',
      target: '[data-guide-target="models-details"]',
      title: '詳細メトリクス',
      body: '各モデルの包括的評価指標を確認。過学習のリスクも表示されます。',
      placement: 'auto',
      page: '/models'
    }
  ],
  '/analysis': [
    {
      id: 'analysis-overview',
      target: '[data-guide-target="analysis-overview"]',
      title: '分析画面',
      body: 'モデルの信頼性と特徴量の重要度を分析できます。',
      placement: 'auto',
      page: '/analysis',
      next: 'analysis-features'
    },
    {
      id: 'analysis-features',
      target: '[data-guide-target="analysis-features"]',
      title: '特徴量重要度',
      body: 'どの要因が予測に最も影響するかを確認。バーチャートと円グラフで表示。',
      placement: 'auto',
      page: '/analysis',
      next: 'analysis-residuals'
    },
    {
      id: 'analysis-residuals',
      target: '[data-guide-target="analysis-residuals"]',
      title: '残差分析',
      body: '予測誤差のパターンを分析。ランダムな分布が理想的です。',
      placement: 'auto',
      page: '/analysis',
      next: 'analysis-correlation'
    },
    {
      id: 'analysis-correlation',
      target: '[data-guide-target="analysis-correlation"]',
      title: '相関分析',
      body: '特徴量間の相関マトリックス。多重共線性の検出に役立ちます。',
      placement: 'auto',
      page: '/analysis'
    }
  ],
  '/settings': [
    {
      id: 'settings-overview',
      target: '[data-guide-target="settings-overview"]',
      title: '設定画面',
      body: 'システムの動作をカスタマイズできます。',
      placement: 'auto',
      page: '/settings',
      next: 'settings-model'
    },
    {
      id: 'settings-model',
      target: '[data-guide-target="settings-model"]',
      title: 'モデル設定',
      body: 'プライマリモデルの選択と再訓練設定。定期的なモデル更新が重要です。',
      placement: 'auto',
      page: '/settings',
      next: 'settings-data'
    },
    {
      id: 'settings-data',
      target: '[data-guide-target="settings-data"]',
      title: 'データ設定',
      body: '更新間隔とデータポイント数制限。API制限を考慮した設定を推奨。',
      placement: 'auto',
      page: '/settings',
      next: 'settings-notification'
    },
    {
      id: 'settings-notification',
      target: '[data-guide-target="settings-notification"]',
      title: '通知設定',
      body: '分析完了時の通知先を設定。メールアドレスと通知条件を指定。',
      placement: 'auto',
      page: '/settings'
    }
  ]
};

// ツールチップ設定
export const TOOLTIP_CONFIG = {
  metrics: {
    mae: {
      content: 'MAE: 平均絶対誤差',
      detail: '予測値と実際値の差の絶対値の平均。値が小さいほど予測精度が高い。'
    },
    rmse: {
      content: 'RMSE: 二乗平均平方根誤差',
      detail: '予測値と実際値の差の二乗平均の平方根。MAEより大きな誤差に敏感。'
    },
    r2: {
      content: 'R²: 決定係数',
      detail: 'モデルがデータの変動を説明できる割合。1に近いほど良い。'
    },
    accuracy: {
      content: '予測精度',
      detail: '直近テスト期間での予測と実際の一致度。過去データへの過適合に注意。'
    }
  },
  risk: {
    warning: {
      content: 'リスク警告',
      detail: '損切り接近・ボラティリティ上昇・イベント接近を検知。'
    },
    recommendation: {
      content: '推奨ラベル',
      detail: 'AI分析に基づく投資判断。BUY/SELL/HOLDの推奨。'
    }
  },
  charts: {
    legend: {
      content: '凡例',
      detail: 'グラフの各要素の説明。クリックで表示/非表示を切り替え。'
    },
    axis: {
      content: '軸',
      detail: 'X軸（時間）とY軸（価格）の情報。ズーム・パン操作が可能。'
    }
  }
};

// チェックリスト設定
export const CHECKLIST_CONFIG = {
  items: [
    {
      id: 'dashboard-overview',
      title: 'ダッシュボードを1分で把握する',
      description: '今日の投資指示と主要KPIを確認',
      required: true
    },
    {
      id: 'kpi-understanding',
      title: 'KPIの意味を理解する',
      description: 'MAE、R²、予測精度の解釈を習得',
      required: true
    },
    {
      id: 'candidate-exploration',
      title: '銘柄カードから詳細に入る',
      description: '推奨銘柄の詳細分析を実行',
      required: false
    },
    {
      id: 'settings-configuration',
      title: '通知先を設定する',
      description: '分析結果の通知設定を完了',
      required: true
    }
  ],
  completion: {
    message: 'お疲れ様でした！主要機能を理解できました。',
    autoHide: true,
    hideDelay: 2000
  }
};

// キーボードショートカット設定
export const SHORTCUT_CONFIG = {
  help: 'F1',
  glossary: 'G',
  tour: 'T',
  escape: 'Escape',
  next: 'ArrowRight',
  prev: 'ArrowLeft',
  skip: 'Escape'
};

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
