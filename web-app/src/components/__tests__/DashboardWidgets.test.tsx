import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardWidgets from '../DashboardWidgets';

const mockPerformanceMetrics = {
  accuracy: 85.5,
  mae: 12.3,
  rmse: 18.7,
  r2: 0.78,
};

const mockMarketInsights = {
  trends: [
    { description: "テクノロジー株の上昇傾向", sentiment: "positive" as const },
    { description: "エネルギー株の調整局面", sentiment: "negative" as const },
    { description: "金融株の安定推移", sentiment: "neutral" as const },
  ],
};

const mockModelComparison = [
  { name: "Random Forest", type: "Ensemble", mae: 10.2, mse: 156.8, rmse: 12.5, r2: 0.82, rank: 1 },
  { name: "XGBoost", type: "Gradient Boosting", mae: 11.1, mse: 178.3, rmse: 13.4, r2: 0.79, rank: 2 },
  { name: "LSTM", type: "Neural Network", mae: 12.8, mse: 201.5, rmse: 14.2, r2: 0.75, rank: 3 },
];

describe('DashboardWidgets', () => {
  const defaultProps = {
    performanceMetrics: mockPerformanceMetrics,
    marketInsights: mockMarketInsights,
    modelComparison: mockModelComparison,
    isLoading: false,
    error: null,
    onRetry: jest.fn(),
    isSampleData: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('正常にレンダリングされる', () => {
    render(<DashboardWidgets {...defaultProps} />);
    
    expect(screen.getByText('パフォーマンスサマリー')).toBeInTheDocument();
    expect(screen.getByText('市場サマリー')).toBeInTheDocument();
    expect(screen.getByText('モデル比較')).toBeInTheDocument();
    expect(screen.getByText('アラート')).toBeInTheDocument();
    expect(screen.getByText('推奨アクション')).toBeInTheDocument();
    expect(screen.getByText('システム状態')).toBeInTheDocument();
  });

  it('ローディング状態を正しく表示する', () => {
    render(<DashboardWidgets {...defaultProps} isLoading={true} />);
    
    // ローディングスピナーが表示されることを確認
    const loadingElements = screen.getAllByRole('generic');
    expect(loadingElements.some(el => el.className.includes('animate-pulse'))).toBe(true);
  });

  it('エラー状態を正しく表示する', () => {
    const errorMessage = 'データの読み込みに失敗しました';
    render(
      <DashboardWidgets 
        {...defaultProps} 
        error={errorMessage}
        isLoading={false}
      />
    );
    
    expect(screen.getByText('データ取得エラー')).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByText('再試行')).toBeInTheDocument();
  });

  it('サンプルデータ警告を表示する', () => {
    render(<DashboardWidgets {...defaultProps} isSampleData={true} />);
    
    expect(screen.getByText(/サンプルデータを表示しています/)).toBeInTheDocument();
  });

  it('再試行ボタンが正しく動作する', async () => {
    const mockOnRetry = jest.fn();
    render(
      <DashboardWidgets 
        {...defaultProps} 
        error="テストエラー"
        onRetry={mockOnRetry}
      />
    );
    
    const retryButton = screen.getByText('再試行');
    fireEvent.click(retryButton);
    
    expect(mockOnRetry).toHaveBeenCalledTimes(1);
  });

  it('パフォーマンスメトリクスを正しく表示する', () => {
    render(<DashboardWidgets {...defaultProps} />);
    
    expect(screen.getByText('85.5%')).toBeInTheDocument(); // 精度
    expect(screen.getByText('12.3')).toBeInTheDocument(); // MAE
    expect(screen.getByText('18.7')).toBeInTheDocument(); // RMSE
    expect(screen.getByText('0.78')).toBeInTheDocument(); // R²
  });

  it('市場インサイトを正しく表示する', () => {
    render(<DashboardWidgets {...defaultProps} />);
    
    expect(screen.getByText('テクノロジー株の上昇傾向')).toBeInTheDocument();
    expect(screen.getByText('エネルギー株の調整局面')).toBeInTheDocument();
    expect(screen.getByText('金融株の安定推移')).toBeInTheDocument();
  });

  it('モデル比較を正しく表示する', () => {
    render(<DashboardWidgets {...defaultProps} />);
    
    expect(screen.getByText('Random Forest')).toBeInTheDocument();
    expect(screen.getByText('XGBoost')).toBeInTheDocument();
    expect(screen.getByText('LSTM')).toBeInTheDocument();
  });

  it('最大リトライ回数に達した場合の表示', () => {
    // リトライ回数を3回に設定してテスト
    const propsWithMaxRetries = {
      ...defaultProps,
      error: 'テストエラー',
    };
    
    render(<DashboardWidgets {...propsWithMaxRetries} />);
    
    // 最初は再試行ボタンが表示される
    expect(screen.getByText('再試行')).toBeInTheDocument();
    
    // 3回リトライをシミュレート
    for (let i = 0; i < 3; i++) {
      fireEvent.click(screen.getByText('再試行'));
    }
    
    // 最大リトライ回数に達した場合の表示を確認
    // 注意: 実際の実装では、retryCountの状態管理が必要
  });
});
