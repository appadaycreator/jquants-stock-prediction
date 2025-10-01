// モデル・指標情報の定義ファイル
export interface ModelDefinition {
  id: string;
  name: string;
  description: string;
  type: string;
  pros: string[];
  cons: string[];
  useCase: string;
  performance: {
    speed: "fast" | "medium" | "slow";
    accuracy: "high" | "medium" | "low";
    interpretability: "high" | "medium" | "low";
  };
  recommended: boolean;
}

export interface MetricDefinition {
  id: string;
  name: string;
  description: string;
  interpretation: string;
  goodRange: string;
  calculation: string;
  example: string;
}

// モデル定義
export const MODEL_DEFINITIONS: ModelDefinition[] = [
  {
    id: "xgboost",
    name: "XGBoost",
    description: "勾配ブースティングによる高精度な予測モデル",
    type: "アンサンブル学習",
    pros: [
      "高い予測精度",
      "過学習に強い",
      "特徴量の重要度を分析可能",
      "欠損値の処理が得意",
      "非線形関係を捉えやすい"
    ],
    cons: [
      "計算時間が長い",
      "パラメータ調整が複雑",
      "メモリ使用量が多い",
      "解釈が困難な場合がある"
    ],
    useCase: "高精度な予測が必要な場合、特徴量の重要度を知りたい場合",
    performance: {
      speed: "medium",
      accuracy: "high",
      interpretability: "medium"
    },
    recommended: true
  },
  {
    id: "random_forest",
    name: "Random Forest",
    description: "複数の決定木を組み合わせたアンサンブル学習",
    type: "アンサンブル学習",
    pros: [
      "高速処理",
      "過学習に強い",
      "解釈しやすい",
      "外れ値に頑健",
      "特徴量の重要度が分かる"
    ],
    cons: [
      "大量データではメモリ使用量が多い",
      "外挿が苦手",
      "線形関係の表現が限定的"
    ],
    useCase: "バランスの取れた性能を求める場合、解釈しやすいモデルが必要な場合",
    performance: {
      speed: "fast",
      accuracy: "high",
      interpretability: "high"
    },
    recommended: true
  },
  {
    id: "linear_regression",
    name: "線形回帰",
    description: "線形関係を仮定したシンプルな予測モデル",
    type: "線形モデル",
    pros: [
      "高速処理",
      "解釈しやすい",
      "計算リソースが少ない",
      "パラメータの意味が明確",
      "外挿に比較的強い"
    ],
    cons: [
      "非線形関係を捉えられない",
      "精度に限界",
      "外れ値の影響を受けやすい",
      "特徴量のスケールに敏感"
    ],
    useCase: "シンプルで高速な予測が必要な場合、解釈性を重視する場合",
    performance: {
      speed: "fast",
      accuracy: "medium",
      interpretability: "high"
    },
    recommended: false
  },
  {
    id: "ridge",
    name: "Ridge回帰",
    description: "正則化を加えた線形回帰の改良版",
    type: "正則化線形モデル",
    pros: [
      "過学習に強い",
      "高速処理",
      "パラメータ調整が簡単",
      "多重共線性に強い",
      "解釈しやすい"
    ],
    cons: [
      "線形関係の仮定が必要",
      "非線形関係を捉えられない",
      "特徴量選択が限定的",
      "外れ値の影響を受けやすい"
    ],
    useCase: "過学習を防ぎたい場合、特徴量が多い場合",
    performance: {
      speed: "fast",
      accuracy: "medium",
      interpretability: "high"
    },
    recommended: false
  },
  {
    id: "lasso",
    name: "Lasso回帰",
    description: "特徴量選択機能付きの正則化線形回帰",
    type: "正則化線形モデル",
    pros: [
      "自動特徴量選択",
      "過学習に強い",
      "解釈しやすい",
      "スパースな解を得やすい",
      "多重共線性に強い"
    ],
    cons: [
      "線形関係の仮定が必要",
      "非線形関係を捉えられない",
      "特徴量の相関に敏感",
      "外れ値の影響を受けやすい"
    ],
    useCase: "特徴量選択を自動化したい場合、解釈性を重視する場合",
    performance: {
      speed: "fast",
      accuracy: "medium",
      interpretability: "high"
    },
    recommended: false
  },
  {
    id: "svm",
    name: "サポートベクターマシン",
    description: "マージン最大化による分類・回帰モデル",
    type: "カーネル法",
    pros: [
      "高次元データに強い",
      "非線形関係を捉えられる",
      "外れ値に頑健",
      "メモリ効率が良い"
    ],
    cons: [
      "大規模データに不向き",
      "パラメータ調整が複雑",
      "解釈が困難",
      "計算時間が長い場合がある"
    ],
    useCase: "高次元データの分析、非線形関係のモデリング",
    performance: {
      speed: "medium",
      accuracy: "high",
      interpretability: "low"
    },
    recommended: false
  }
];

// 指標定義
export const METRIC_DEFINITIONS: MetricDefinition[] = [
  {
    id: "mae",
    name: "MAE (平均絶対誤差)",
    description: "予測値と実際値の差の絶対値の平均",
    interpretation: "値が小さいほど予測精度が高い。単位は予測対象と同じ（円、%など）",
    goodRange: "MAE < 価格の5%程度が良好",
    calculation: "MAE = Σ|実際値 - 予測値| / n",
    example: "株価1000円の予測でMAE=50円なら、平均的に50円の誤差"
  },
  {
    id: "rmse",
    name: "RMSE (平均平方根誤差)",
    description: "予測値と実際値の差の二乗の平均の平方根",
    interpretation: "値が小さいほど予測精度が高い。大きな誤差を重視する指標",
    goodRange: "RMSE < 価格の10%程度が良好",
    calculation: "RMSE = √(Σ(実際値 - 予測値)² / n)",
    example: "株価1000円の予測でRMSE=100円なら、標準的な誤差が100円"
  },
  {
    id: "r2",
    name: "R² (決定係数)",
    description: "モデルがデータの変動をどの程度説明できるかを示す指標",
    interpretation: "0-1の値で、1に近いほど良い。0.7以上で実用的",
    goodRange: "R² > 0.7が良好、R² > 0.9が優秀",
    calculation: "R² = 1 - (残差平方和 / 総平方和)",
    example: "R²=0.8なら、モデルがデータの変動の80%を説明"
  },
  {
    id: "mse",
    name: "MSE (平均平方誤差)",
    description: "予測値と実際値の差の二乗の平均",
    interpretation: "値が小さいほど予測精度が高い。大きな誤差を強く重視",
    goodRange: "MSE < 価格の5%の二乗程度が良好",
    calculation: "MSE = Σ(実際値 - 予測値)² / n",
    example: "株価1000円の予測でMSE=2500なら、平均的な二乗誤差が2500"
  },
  {
    id: "mape",
    name: "MAPE (平均絶対パーセント誤差)",
    description: "予測値と実際値の差をパーセントで表した平均",
    interpretation: "値が小さいほど予測精度が高い。相対的な誤差を表す",
    goodRange: "MAPE < 10%が良好、MAPE < 5%が優秀",
    calculation: "MAPE = Σ|(実際値 - 予測値) / 実際値| × 100 / n",
    example: "MAPE=5%なら、平均的に5%の誤差"
  }
];

// 特徴量重要度の解釈
export const FEATURE_IMPORTANCE_GUIDE = {
  title: "特徴量重要度の読み方",
  description: "各特徴量が株価予測にどの程度影響するかを示します",
  interpretation: [
    {
      feature: "価格変動率",
      importance: "高",
      meaning: "過去の価格変動が将来の価格に大きく影響",
      investment_implication: "トレンドフォロー戦略が有効"
    },
    {
      feature: "ボリューム",
      importance: "高",
      meaning: "出来高が価格変動の予測に重要",
      investment_implication: "出来高の変化に注目して売買判断"
    },
    {
      feature: "RSI",
      importance: "中",
      meaning: "相対的強弱指標が価格予測に影響",
      investment_implication: "オーバーボート・オーバーソールドの判断材料"
    },
    {
      feature: "移動平均",
      importance: "中",
      meaning: "トレンドの方向性が価格予測に影響",
      investment_implication: "移動平均線の位置関係を確認"
    },
    {
      feature: "ボリンジャーバンド",
      importance: "中",
      meaning: "価格のボラティリティが予測に影響",
      investment_implication: "ボラティリティの変化に注目"
    },
    {
      feature: "MACD",
      importance: "低",
      meaning: "MACDシグナルが価格予測に影響",
      investment_implication: "トレンド転換のシグナルとして活用"
    }
  ],
  tips: [
    "重要度が高い特徴量ほど、その指標の変化に敏感に反応します",
    "複数の特徴量が組み合わさって予測精度が決まります",
    "市場環境によって特徴量の重要度は変化します",
    "重要度の低い特徴量でも、特定の条件下では重要になる場合があります"
  ]
};

// モデル比較のベストプラクティス
export const MODEL_COMPARISON_GUIDE = {
  title: "モデル比較のベストプラクティス",
  description: "複数の指標を総合的に評価して最適なモデルを選択しましょう",
  evaluation_criteria: [
    {
      metric: "R²",
      weight: "最重要",
      reason: "モデルの説明力の基本指標",
      threshold: "0.7以上を目標"
    },
    {
      metric: "RMSE",
      weight: "重要",
      reason: "実用的な誤差の大きさを表す",
      threshold: "価格の10%以下を目標"
    },
    {
      metric: "MAE",
      weight: "重要",
      reason: "平均的な誤差の大きさを表す",
      threshold: "価格の5%以下を目標"
    }
  ],
  selection_tips: [
    "単一の指標だけでなく、複数の指標を総合的に評価する",
    "データの性質（線形・非線形）に応じてモデルを選択する",
    "計算時間と精度のバランスを考慮する",
    "解釈性が必要な場合は線形モデルを優先する",
    "高精度が必要な場合はアンサンブル学習を選択する"
  ]
};
