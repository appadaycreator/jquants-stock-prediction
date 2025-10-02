// 設定スキーマの定義とバリデーション

export interface SettingsSchema {
  version: string;
  prediction: {
    days: number;
  };
  features: {
    selected: string[];
  };
  model: {
    type: string;
    primary_model: string;
    compare_models: boolean;
    retrain_frequency: string;
    auto_retrain: boolean;
  };
  data: {
    refresh_interval: string;
    max_data_points: number;
    include_technical_indicators: boolean;
  };
  ui: {
    theme: string;
    refresh_rate: number;
    show_tooltips: boolean;
  };
  hyperparameters?: {
    xgboost?: {
      n_estimators: number;
      learning_rate: number;
      max_depth: number;
      subsample: number;
      colsample_bytree: number;
      reg_alpha: number;
    };
    random_forest?: {
      n_estimators: number;
      max_depth: number;
      min_samples_split: number;
      min_samples_leaf: number;
      max_features: string;
      bootstrap: boolean;
    };
    ridge?: {
      alpha: number;
      fit_intercept: boolean;
      normalize: boolean;
    };
  };
}

// デフォルト設定
export const defaultSettings: SettingsSchema = {
  version: "1.0.0",
  prediction: {
    days: 30,
  },
  features: {
    selected: ["sma_5", "sma_10", "sma_25", "rsi", "macd", "bollinger_upper", "bollinger_lower"],
  },
  model: {
    type: "all",
    primary_model: "xgboost",
    compare_models: true,
    retrain_frequency: "weekly",
    auto_retrain: true,
  },
  data: {
    refresh_interval: "hourly",
    max_data_points: 1000,
    include_technical_indicators: true,
  },
  ui: {
    theme: "light",
    refresh_rate: 30,
    show_tooltips: true,
  },
  hyperparameters: {
    xgboost: {
      n_estimators: 100,
      learning_rate: 0.1,
      max_depth: 6,
      subsample: 1.0,
      colsample_bytree: 1.0,
      reg_alpha: 0,
    },
    random_forest: {
      n_estimators: 100,
      max_depth: 10,
      min_samples_split: 2,
      min_samples_leaf: 1,
      max_features: "sqrt",
      bootstrap: true,
    },
    ridge: {
      alpha: 1.0,
      fit_intercept: true,
      normalize: false,
    },
  },
};

// バリデーションルール
export const validationRules = {
  prediction: {
    days: {
      min: 1,
      max: 365,
      required: true,
    },
  },
  features: {
    selected: {
      minItems: 1,
      maxItems: 20,
      required: true,
    },
  },
  model: {
    type: {
      enum: ["all", "linear", "random_forest", "xgboost"],
      required: true,
    },
    primary_model: {
      enum: ["xgboost", "random_forest", "linear_regression", "ridge"],
      required: true,
    },
    compare_models: {
      type: "boolean",
      required: true,
    },
    retrain_frequency: {
      enum: ["daily", "weekly", "monthly", "manual"],
      required: true,
    },
    auto_retrain: {
      type: "boolean",
      required: true,
    },
  },
  data: {
    refresh_interval: {
      enum: ["realtime", "hourly", "daily", "weekly"],
      required: true,
    },
    max_data_points: {
      min: 100,
      max: 10000,
      required: true,
    },
    include_technical_indicators: {
      type: "boolean",
      required: true,
    },
  },
  ui: {
    theme: {
      enum: ["light", "dark", "auto"],
      required: true,
    },
    refresh_rate: {
      min: 1,
      max: 3600,
      required: true,
    },
    show_tooltips: {
      type: "boolean",
      required: true,
    },
  },
};

// 設定のバリデーション
export function validateSettings(settings: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  // バージョンチェック
  if (!settings.version) {
    errors.push("設定バージョンが指定されていません");
  }

  // 予測設定のバリデーション
  if (!settings.prediction || typeof settings.prediction.days !== "number") {
    errors.push("予測期間が正しく設定されていません");
  } else if (settings.prediction.days < 1 || settings.prediction.days > 365) {
    errors.push("予測期間は1-365日の範囲で設定してください");
  }

  // 特徴量設定のバリデーション
  if (!settings.features || !Array.isArray(settings.features.selected)) {
    errors.push("特徴量設定が正しく設定されていません");
  } else if (settings.features.selected.length === 0) {
    errors.push("最低1つの特徴量を選択してください");
  } else if (settings.features.selected.length > 20) {
    errors.push("特徴量は20個以下にしてください");
  }

  // モデル設定のバリデーション
  if (!settings.model) {
    errors.push("モデル設定が正しく設定されていません");
  } else {
    if (!validationRules.model.type.enum.includes(settings.model.type)) {
      errors.push("無効なモデルタイプが指定されています");
    }
    if (!validationRules.model.primary_model.enum.includes(settings.model.primary_model)) {
      errors.push("無効なプライマリモデルが指定されています");
    }
    if (!validationRules.model.retrain_frequency.enum.includes(settings.model.retrain_frequency)) {
      errors.push("無効な再訓練頻度が指定されています");
    }
  }

  // データ設定のバリデーション
  if (!settings.data) {
    errors.push("データ設定が正しく設定されていません");
  } else {
    if (!validationRules.data.refresh_interval.enum.includes(settings.data.refresh_interval)) {
      errors.push("無効なデータ更新間隔が指定されています");
    }
    if (typeof settings.data.max_data_points !== "number" || 
        settings.data.max_data_points < 100 || 
        settings.data.max_data_points > 10000) {
      errors.push("最大データポイント数は100-10000の範囲で設定してください");
    }
  }

  // UI設定のバリデーション
  if (!settings.ui) {
    errors.push("UI設定が正しく設定されていません");
  } else {
    if (!validationRules.ui.theme.enum.includes(settings.ui.theme)) {
      errors.push("無効なテーマが指定されています");
    }
    if (typeof settings.ui.refresh_rate !== "number" || 
        settings.ui.refresh_rate < 1 || 
        settings.ui.refresh_rate > 3600) {
      errors.push("更新間隔は1-3600秒の範囲で設定してください");
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

// 設定のマイグレーション
export function migrateSettings(settings: any): SettingsSchema {
  const migrated = { ...defaultSettings };

  // バージョン1.0.0へのマイグレーション
  if (!settings.version || settings.version === "0.9.0") {
    // 古い設定を新しい形式に変換
    if (settings.prediction) {
      migrated.prediction = {
        days: settings.prediction.days || 30,
      };
    }

    if (settings.features) {
      migrated.features = {
        selected: settings.features.selected || defaultSettings.features.selected,
      };
    }

    if (settings.model) {
      migrated.model = {
        type: settings.model.type || "all",
        primary_model: settings.model.primary_model || "xgboost",
        compare_models: settings.model.compare_models !== undefined ? settings.model.compare_models : true,
        retrain_frequency: settings.model.retrain_frequency || "weekly",
        auto_retrain: settings.model.auto_retrain !== undefined ? settings.model.auto_retrain : true,
      };
    }

    if (settings.data) {
      migrated.data = {
        refresh_interval: settings.data.refresh_interval || "hourly",
        max_data_points: settings.data.max_data_points || 1000,
        include_technical_indicators: settings.data.include_technical_indicators !== undefined ? settings.data.include_technical_indicators : true,
      };
    }

    if (settings.ui) {
      migrated.ui = {
        theme: settings.ui.theme || "light",
        refresh_rate: settings.ui.refresh_rate || 30,
        show_tooltips: settings.ui.show_tooltips !== undefined ? settings.ui.show_tooltips : true,
      };
    }

    if (settings.hyperparameters) {
      migrated.hyperparameters = {
        ...defaultSettings.hyperparameters,
        ...settings.hyperparameters,
      };
    }
  }

  // バージョンを更新
  migrated.version = "1.0.0";

  return migrated;
}

// 設定の正規化（不足している項目をデフォルト値で補完）
export function normalizeSettings(settings: any): SettingsSchema {
  const normalized = { ...defaultSettings };

  // 各セクションを正規化
  if (settings.prediction) {
    normalized.prediction = {
      ...defaultSettings.prediction,
      ...settings.prediction,
    };
  }

  if (settings.features) {
    normalized.features = {
      ...defaultSettings.features,
      ...settings.features,
    };
  }

  if (settings.model) {
    normalized.model = {
      ...defaultSettings.model,
      ...settings.model,
    };
  }

  if (settings.data) {
    normalized.data = {
      ...defaultSettings.data,
      ...settings.data,
    };
  }

  if (settings.ui) {
    normalized.ui = {
      ...defaultSettings.ui,
      ...settings.ui,
    };
  }

  if (settings.hyperparameters) {
    normalized.hyperparameters = {
      ...defaultSettings.hyperparameters,
      ...settings.hyperparameters,
    };
  }

  // バージョンを設定
  normalized.version = settings.version || "1.0.0";

  return normalized;
}

// 設定の比較（変更検出）
export function compareSettings(oldSettings: SettingsSchema, newSettings: SettingsSchema): string[] {
  const changes: string[] = [];

  // 予測設定の変更
  if (oldSettings.prediction.days !== newSettings.prediction.days) {
    changes.push(`予測期間: ${oldSettings.prediction.days}日 → ${newSettings.prediction.days}日`);
  }

  // 特徴量設定の変更
  const oldFeatures = oldSettings.features.selected.sort();
  const newFeatures = newSettings.features.selected.sort();
  if (JSON.stringify(oldFeatures) !== JSON.stringify(newFeatures)) {
    changes.push(`特徴量: ${oldFeatures.length}個 → ${newFeatures.length}個`);
  }

  // モデル設定の変更
  if (oldSettings.model.type !== newSettings.model.type) {
    changes.push(`モデルタイプ: ${oldSettings.model.type} → ${newSettings.model.type}`);
  }
  if (oldSettings.model.compare_models !== newSettings.model.compare_models) {
    changes.push(`モデル比較: ${oldSettings.model.compare_models ? "有効" : "無効"} → ${newSettings.model.compare_models ? "有効" : "無効"}`);
  }
  if (oldSettings.model.retrain_frequency !== newSettings.model.retrain_frequency) {
    changes.push(`再訓練頻度: ${oldSettings.model.retrain_frequency} → ${newSettings.model.retrain_frequency}`);
  }

  // データ設定の変更
  if (oldSettings.data.refresh_interval !== newSettings.data.refresh_interval) {
    changes.push(`データ更新間隔: ${oldSettings.data.refresh_interval} → ${newSettings.data.refresh_interval}`);
  }
  if (oldSettings.data.max_data_points !== newSettings.data.max_data_points) {
    changes.push(`最大データポイント数: ${oldSettings.data.max_data_points} → ${newSettings.data.max_data_points}`);
  }

  // UI設定の変更
  if (oldSettings.ui.theme !== newSettings.ui.theme) {
    changes.push(`テーマ: ${oldSettings.ui.theme} → ${newSettings.ui.theme}`);
  }
  if (oldSettings.ui.refresh_rate !== newSettings.ui.refresh_rate) {
    changes.push(`更新間隔: ${oldSettings.ui.refresh_rate}秒 → ${newSettings.ui.refresh_rate}秒`);
  }

  return changes;
}
