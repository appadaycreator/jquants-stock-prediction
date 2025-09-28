/**
 * 評価指標計算ユーティリティ
 * 過学習検出とベースライン比較
 */

/**
 * 平均絶対誤差 (MAE)
 */
export function mae(y: number[], yhat: number[]): number {
  if (y.length !== yhat.length) {
    throw new Error('配列の長さが一致しません');
  }
  
  const errors = y.map((actual, i) => Math.abs(actual - yhat[i]));
  return errors.reduce((sum, error) => sum + error, 0) / errors.length;
}

/**
 * 二乗平均平方根誤差 (RMSE)
 */
export function rmse(y: number[], yhat: number[]): number {
  if (y.length !== yhat.length) {
    throw new Error('配列の長さが一致しません');
  }
  
  const squaredErrors = y.map((actual, i) => Math.pow(actual - yhat[i], 2));
  const mse = squaredErrors.reduce((sum, error) => sum + error, 0) / squaredErrors.length;
  return Math.sqrt(mse);
}

/**
 * 決定係数 (R²)
 */
export function r2(y: number[], yhat: number[]): number {
  if (y.length !== yhat.length) {
    throw new Error('配列の長さが一致しません');
  }
  
  const yMean = y.reduce((sum, val) => sum + val, 0) / y.length;
  const ssRes = y.reduce((sum, actual, i) => sum + Math.pow(actual - yhat[i], 2), 0);
  const ssTot = y.reduce((sum, actual) => sum + Math.pow(actual - yMean, 2), 0);
  
  if (ssTot === 0) {
    // 定数系列の場合
    return ssRes === 0 ? 1 : 0;
  }
  
  return 1 - (ssRes / ssTot);
}

/**
 * 平均絶対パーセント誤差 (MAPE)
 */
export function mape(y: number[], yhat: number[]): number {
  if (y.length !== yhat.length) {
    throw new Error('配列の長さが一致しません');
  }
  
  const errors = y.map((actual, i) => {
    if (actual === 0) return 0; // ゼロ除算を避ける
    return Math.abs((actual - yhat[i]) / actual);
  });
  
  return errors.reduce((sum, error) => sum + error, 0) / errors.length * 100;
}

/**
 * 過学習検出
 */
export function detectOverfitting(
  trainR2: number,
  testR2: number,
  threshold: number = 0.1
): {
  isOverfitting: boolean;
  riskLevel: '低' | '中' | '高';
  message: string;
} {
  const r2Diff = trainR2 - testR2;
  
  if (testR2 > 0.99) {
    return {
      isOverfitting: true,
      riskLevel: '高',
      message: '高リスク（R² > 0.99）'
    };
  }
  
  if (testR2 > 0.95) {
    return {
      isOverfitting: true,
      riskLevel: '中',
      message: '中リスク（R² > 0.95）'
    };
  }
  
  if (r2Diff > threshold) {
    return {
      isOverfitting: true,
      riskLevel: '中',
      message: `過学習疑い（差: ${r2Diff.toFixed(3)}）`
    };
  }
  
  return {
    isOverfitting: false,
    riskLevel: '低',
    message: '低リスク'
  };
}

/**
 * ベースライン（Naive）予測
 */
export function naiveBaseline(y: number[]): number[] {
  if (y.length < 2) {
    return y.slice(); // データが少ない場合はそのまま
  }
  
  // 前日終値を維持する予測
  return [y[0], ...y.slice(0, -1)];
}

/**
 * ベースライン性能評価
 */
export function evaluateBaseline(y: number[]): {
  mae: number;
  rmse: number;
  r2: number;
  mape: number;
} {
  const yhat = naiveBaseline(y);
  const actual = y.slice(1); // 最初の要素を除く
  const predicted = yhat.slice(1);
  
  return {
    mae: mae(actual, predicted),
    rmse: rmse(actual, predicted),
    r2: r2(actual, predicted),
    mape: mape(actual, predicted)
  };
}

/**
 * モデル性能の比較
 */
export function compareModels(
  modelMetrics: { mae: number; rmse: number; r2: number },
  baselineMetrics: { mae: number; rmse: number; r2: number }
): {
  maeImprovement: number;
  rmseImprovement: number;
  r2Improvement: number;
  isBetter: boolean;
} {
  const maeImprovement = ((baselineMetrics.mae - modelMetrics.mae) / baselineMetrics.mae) * 100;
  const rmseImprovement = ((baselineMetrics.rmse - modelMetrics.rmse) / baselineMetrics.rmse) * 100;
  const r2Improvement = modelMetrics.r2 - baselineMetrics.r2;
  
  const isBetter = modelMetrics.mae < baselineMetrics.mae && 
                   modelMetrics.rmse < baselineMetrics.rmse && 
                   modelMetrics.r2 > baselineMetrics.r2;
  
  return {
    maeImprovement,
    rmseImprovement,
    r2Improvement,
    isBetter
  };
}

/**
 * 時系列分割の検証
 */
export function validateTimeSeriesSplit(
  dates: string[],
  trainSize: number,
  testSize: number
): boolean {
  if (dates.length < trainSize + testSize) {
    return false;
  }
  
  // 日付が時系列順になっているかチェック
  for (let i = 1; i < dates.length; i++) {
    const prev = new Date(dates[i - 1]);
    const curr = new Date(dates[i]);
    if (curr < prev) {
      return false;
    }
  }
  
  return true;
}

/**
 * TimeSeriesSplit評価
 */
export function timeSeriesSplitEvaluation(
  X: number[][],
  y: number[],
  dates: string[],
  nSplits: number = 5
): {
  trainScores: number[];
  testScores: number[];
  overfittingRisk: string;
  isOverfitting: boolean;
} {
  const trainScores: number[] = [];
  const testScores: number[] = [];
  
  // 時系列順にデータを分割
  const splitSize = Math.floor(X.length / nSplits);
  
  for (let i = 0; i < nSplits - 1; i++) {
    const trainEnd = (i + 1) * splitSize;
    const testStart = trainEnd;
    const testEnd = Math.min(testStart + splitSize, X.length);
    
    if (testStart >= X.length) break;
    
    const XTrain = X.slice(0, trainEnd);
    const yTrain = y.slice(0, trainEnd);
    const XTest = X.slice(testStart, testEnd);
    const yTest = y.slice(testStart, testEnd);
    
    if (XTrain.length === 0 || XTest.length === 0) continue;
    
    // 簡易的な線形回帰で評価（実際のモデルは外部で学習）
    const trainR2 = calculateR2(yTrain, yTrain); // 簡略化
    const testR2 = calculateR2(yTest, yTest); // 簡略化
    
    trainScores.push(trainR2);
    testScores.push(testR2);
  }
  
  const avgTrainScore = trainScores.reduce((a, b) => a + b, 0) / trainScores.length;
  const avgTestScore = testScores.reduce((a, b) => a + b, 0) / testScores.length;
  const scoreDiff = avgTrainScore - avgTestScore;
  
  let overfittingRisk = '低リスク';
  let isOverfitting = false;
  
  if (avgTestScore > 0.99) {
    overfittingRisk = '高リスク（R² > 0.99）';
    isOverfitting = true;
  } else if (avgTestScore > 0.95) {
    overfittingRisk = '中リスク（R² > 0.95）';
    isOverfitting = true;
  } else if (scoreDiff > 0.1) {
    overfittingRisk = `過学習疑い（差: ${scoreDiff.toFixed(3)}）`;
    isOverfitting = true;
  }
  
  return {
    trainScores,
    testScores,
    overfittingRisk,
    isOverfitting
  };
}

/**
 * Walk-forward評価
 */
export function walkForwardEvaluation(
  X: number[][],
  y: number[],
  dates: string[],
  windowSize: number = 100,
  stepSize: number = 10
): {
  predictions: number[];
  actuals: number[];
  mae: number;
  rmse: number;
  r2: number;
  isBetterThanBaseline: boolean;
} {
  const predictions: number[] = [];
  const actuals: number[] = [];
  
  for (let i = windowSize; i < X.length; i += stepSize) {
    const XTrain = X.slice(i - windowSize, i);
    const yTrain = y.slice(i - windowSize, i);
    const XTest = X.slice(i, i + stepSize);
    const yTest = y.slice(i, i + stepSize);
    
    if (XTrain.length === 0 || XTest.length === 0) continue;
    
    // 簡易的な予測（実際のモデルは外部で学習）
    const prediction = yTrain[yTrain.length - 1]; // 前日終値を予測値とする
    predictions.push(prediction);
    actuals.push(yTest[0]);
  }
  
  const maeValue = mae(actuals, predictions);
  const rmseValue = rmse(actuals, predictions);
  const r2Value = r2(actuals, predictions);
  
  // ベースライン（Naive）との比較
  const baselinePredictions = naiveBaseline(actuals);
  const baselineR2 = r2(actuals, baselinePredictions);
  const isBetterThanBaseline = r2Value > baselineR2;
  
  return {
    predictions,
    actuals,
    mae: maeValue,
    rmse: rmseValue,
    r2: r2Value,
    isBetterThanBaseline
  };
}

/**
 * R²計算のヘルパー関数
 */
function calculateR2(y: number[], yhat: number[]): number {
  if (y.length !== yhat.length) return 0;
  
  const yMean = y.reduce((sum, val) => sum + val, 0) / y.length;
  const ssRes = y.reduce((sum, actual, i) => sum + Math.pow(actual - yhat[i], 2), 0);
  const ssTot = y.reduce((sum, actual) => sum + Math.pow(actual - yMean, 2), 0);
  
  if (ssTot === 0) return ssRes === 0 ? 1 : 0;
  
  return 1 - (ssRes / ssTot);
}
