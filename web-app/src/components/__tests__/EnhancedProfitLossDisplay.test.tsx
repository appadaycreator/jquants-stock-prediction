import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EnhancedProfitLossDisplay } from '../EnhancedProfitLossDisplay';

// モックデータ
const mockPnLSummary = {
  total_investment: 1000000,
  current_value: 1200000,
  unrealized_pnl: 200000,
  realized_pnl: 0,
  total_pnl: 200000,
  pnl_percentage: 20.0,
  daily_pnl: 5000,
  weekly_pnl: 25000,
  monthly_pnl: 100000,
  yearly_pnl: 200000,
  best_performer: {
    symbol: "7203",
    symbolName: "トヨタ自動車",
    return: 15.5,
    value: 500000
  },
  worst_performer: {
    symbol: "6758",
    symbolName: "ソニーグループ",
    return: -5.2,
    value: 300000
  },
  risk_adjusted_return: 0.85,
  sharpe_ratio: 1.2,
  max_drawdown: -8.5,
  volatility: 12.3,
  win_rate: 75.0,
  profit_factor: 1.8
};

const mockPerformanceData = [
  {
    date: "2024-01-01",
    total_value: 1000000,
    daily_pnl: 0,
    cumulative_pnl: 0
  },
  {
    date: "2024-01-02",
    total_value: 1010000,
    daily_pnl: 10000,
    cumulative_pnl: 10000
  },
  {
    date: "2024-01-03",
    total_value: 1020000,
    daily_pnl: 10000,
    cumulative_pnl: 20000
  }
];

const mockPositions = [
  {
    symbol: "7203",
    symbolName: "トヨタ自動車",
    current_value: 500000,
    cost_basis: 450000,
    unrealized_pnl: 50000,
    pnl_percentage: 11.1,
    weight: 0.4,
    contribution: 0.25,
    risk_level: "MEDIUM",
    sector: "自動車",
    market_cap: 30000000000,
    volume: 1000000,
    volatility: 15.2,
    beta: 1.1,
    pe_ratio: 12.5,
    dividend_yield: 2.1
  },
  {
    symbol: "6758",
    symbolName: "ソニーグループ",
    current_value: 300000,
    cost_basis: 320000,
    unrealized_pnl: -20000,
    pnl_percentage: -6.25,
    weight: 0.25,
    contribution: -0.1,
    risk_level: "HIGH",
    sector: "エンターテインメント",
    market_cap: 15000000000,
    volume: 800000,
    volatility: 18.5,
    beta: 1.3,
    pe_ratio: 18.2,
    dividend_yield: 1.5
  }
];

describe('EnhancedProfitLossDisplay', () => {
  const defaultProps = {
    pnlSummary: mockPnLSummary,
    performanceData: mockPerformanceData,
    positions: mockPositions,
    onRefresh: jest.fn(),
    isLoading: false,
    autoRefresh: false,
    onAutoRefreshToggle: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('正常にレンダリングされる', () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} />);
    
    expect(screen.getByText('投資成果ダッシュボード')).toBeInTheDocument();
    expect(screen.getByText('投資成果を3秒で把握')).toBeInTheDocument();
  });

  it('主要指標が正しく表示される', () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} />);
    
    // 総投資額
    expect(screen.getByText('¥1,000,000')).toBeInTheDocument();
    
    // 現在価値
    expect(screen.getByText('¥1,200,000')).toBeInTheDocument();
    
    // 損益
    expect(screen.getByText('+¥200,000')).toBeInTheDocument();
    expect(screen.getByText('+20.00%')).toBeInTheDocument();
    
    // シャープレシオ
    expect(screen.getByText('1.20')).toBeInTheDocument();
  });

  it('期間別損益が正しく表示される', () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} />);
    
    expect(screen.getByText('日次')).toBeInTheDocument();
    expect(screen.getByText('週次')).toBeInTheDocument();
    expect(screen.getByText('月次')).toBeInTheDocument();
    expect(screen.getByText('年次')).toBeInTheDocument();
    expect(screen.getByText('総合')).toBeInTheDocument();
  });

  it('更新ボタンが正しく動作する', () => {
    const mockOnRefresh = jest.fn();
    render(<EnhancedProfitLossDisplay {...defaultProps} onRefresh={mockOnRefresh} />);
    
    const refreshButton = screen.getByText('更新');
    fireEvent.click(refreshButton);
    
    expect(mockOnRefresh).toHaveBeenCalledTimes(1);
  });

  it('自動更新ボタンが正しく動作する', () => {
    const mockOnAutoRefreshToggle = jest.fn();
    render(<EnhancedProfitLossDisplay {...defaultProps} onAutoRefreshToggle={mockOnAutoRefreshToggle} />);
    
    const autoRefreshButton = screen.getByText('自動更新');
    fireEvent.click(autoRefreshButton);
    
    expect(mockOnAutoRefreshToggle).toHaveBeenCalledWith(true);
  });

  it('詳細表示の切り替えが正しく動作する', () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} />);
    
    const toggleButton = screen.getByText('簡易表示');
    fireEvent.click(toggleButton);
    
    expect(screen.getByText('詳細表示')).toBeInTheDocument();
  });

  it('ローディング状態が正しく表示される', () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} isLoading={true} />);
    
    const refreshButton = screen.getByText('更新');
    expect(refreshButton).toBeDisabled();
  });

  it('自動更新が有効な場合の表示', () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} autoRefresh={true} />);
    
    const autoRefreshButton = screen.getByText('自動更新');
    expect(autoRefreshButton).toHaveClass('bg-blue-600');
  });

  it('パフォーマンス推移タブが正しく表示される', async () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} />);
    
    // 詳細表示を有効にする
    const toggleButton = screen.getByText('詳細表示');
    fireEvent.click(toggleButton);
    
    // パフォーマンス推移タブをクリック
    const performanceTab = screen.getByText('パフォーマンス推移');
    fireEvent.click(performanceTab);
    
    await waitFor(() => {
      expect(screen.getByText('損益推移グラフ')).toBeInTheDocument();
    });
  });

  it('銘柄ランキングタブが正しく表示される', async () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} />);
    
    // 詳細表示を有効にする
    const toggleButton = screen.getByText('詳細表示');
    fireEvent.click(toggleButton);
    
    // 銘柄ランキングタブをクリック
    const rankingTab = screen.getByText('銘柄ランキング');
    fireEvent.click(rankingTab);
    
    await waitFor(() => {
      expect(screen.getByText('銘柄パフォーマンスランキング')).toBeInTheDocument();
    });
  });

  it('セクター分析タブが正しく表示される', async () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} />);
    
    // 詳細表示を有効にする
    const toggleButton = screen.getByText('詳細表示');
    fireEvent.click(toggleButton);
    
    // セクター分析タブをクリック
    const sectorTab = screen.getByText('セクター分析');
    fireEvent.click(sectorTab);
    
    await waitFor(() => {
      expect(screen.getByText('セクター別パフォーマンス')).toBeInTheDocument();
    });
  });

  it('リスク指標タブが正しく表示される', async () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} />);
    
    // 詳細表示を有効にする
    const toggleButton = screen.getByText('詳細表示');
    fireEvent.click(toggleButton);
    
    // リスク指標タブをクリック
    const riskTab = screen.getByText('リスク指標');
    fireEvent.click(riskTab);
    
    await waitFor(() => {
      expect(screen.getByText('最大ドローダウン')).toBeInTheDocument();
      expect(screen.getByText('ボラティリティ')).toBeInTheDocument();
      expect(screen.getByText('勝率')).toBeInTheDocument();
      expect(screen.getByText('プロフィットファクター')).toBeInTheDocument();
    });
  });

  it('損益が負の場合の表示', () => {
    const negativePnLSummary = {
      ...mockPnLSummary,
      unrealized_pnl: -50000,
      pnl_percentage: -5.0
    };

    render(<EnhancedProfitLossDisplay {...defaultProps} pnlSummary={negativePnLSummary} />);
    
    expect(screen.getByText('-¥50,000')).toBeInTheDocument();
    expect(screen.getByText('-5.00%')).toBeInTheDocument();
  });

  it('空のパフォーマンスデータの場合の処理', () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} performanceData={[]} />);
    
    expect(screen.getByText('投資成果ダッシュボード')).toBeInTheDocument();
  });

  it('空のポジションデータの場合の処理', () => {
    render(<EnhancedProfitLossDisplay {...defaultProps} positions={[]} />);
    
    expect(screen.getByText('投資成果ダッシュボード')).toBeInTheDocument();
  });
});
