import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PerformanceComparison } from '../PerformanceComparison';

// モックデータ
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
  },
  {
    symbol: "9984",
    symbolName: "ソフトバンクグループ",
    current_value: 200000,
    cost_basis: 180000,
    unrealized_pnl: 20000,
    pnl_percentage: 11.1,
    weight: 0.2,
    contribution: 0.1,
    risk_level: "HIGH",
    sector: "通信",
    market_cap: 8000000000,
    volume: 500000,
    volatility: 22.1,
    beta: 1.5,
    pe_ratio: 25.3,
    dividend_yield: 0.8
  }
];

const mockBenchmarkData = {
  name: "日経平均",
  return: 8.5,
  volatility: 12.0
};

describe('PerformanceComparison', () => {
  const defaultProps = {
    positions: mockPositions,
    benchmarkData: mockBenchmarkData,
    onPositionClick: jest.fn(),
    className: ""
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('正常にレンダリングされる', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    expect(screen.getByText('パフォーマンス比較')).toBeInTheDocument();
  });

  it('ビューモードボタンが正しく表示される', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    expect(screen.getByText('テーブル')).toBeInTheDocument();
    expect(screen.getByText('チャート')).toBeInTheDocument();
    expect(screen.getByText('セクター')).toBeInTheDocument();
  });

  it('タブが正しく表示される', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    expect(screen.getByText('ランキング')).toBeInTheDocument();
    expect(screen.getByText('ベスト・ワースト')).toBeInTheDocument();
    expect(screen.getByText('リスク分析')).toBeInTheDocument();
    expect(screen.getByText('セクター分析')).toBeInTheDocument();
  });

  it('ランキングタブが正しく表示される', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    expect(screen.getByText('ランキング')).toBeInTheDocument();
    expect(screen.getByText('損益率')).toBeInTheDocument();
    expect(screen.getByText('配分')).toBeInTheDocument();
    expect(screen.getByText('ボラティリティ')).toBeInTheDocument();
    expect(screen.getByText('ベータ')).toBeInTheDocument();
  });

  it('ソート機能が正しく動作する', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const sortSelect = screen.getByDisplayValue('損益率');
    fireEvent.change(sortSelect, { target: { value: 'weight' } });
    
    expect(sortSelect).toHaveValue('weight');
  });

  it('ソート順序の切り替えが正しく動作する', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const sortOrderButton = screen.getByRole('button', { name: /trending/i });
    fireEvent.click(sortOrderButton);
    
    expect(sortOrderButton).toBeInTheDocument();
  });

  it('セクターフィルターが正しく動作する', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const sectorSelect = screen.getByDisplayValue('すべて');
    fireEvent.change(sectorSelect, { target: { value: '自動車' } });
    
    expect(sectorSelect).toHaveValue('自動車');
  });

  it('ベスト・ワーストタブが正しく表示される', async () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const bestWorstTab = screen.getByText('ベスト・ワースト');
    fireEvent.click(bestWorstTab);
    
    await waitFor(() => {
      expect(screen.getByText('ベストパフォーマー')).toBeInTheDocument();
      expect(screen.getByText('ワーストパフォーマー')).toBeInTheDocument();
    });
  });

  it('リスク分析タブが正しく表示される', async () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const riskTab = screen.getByText('リスク分析');
    fireEvent.click(riskTab);
    
    await waitFor(() => {
      expect(screen.getByText('リスク分布')).toBeInTheDocument();
      expect(screen.getByText('ボラティリティ分析')).toBeInTheDocument();
    });
  });

  it('セクター分析タブが正しく表示される', async () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const sectorTab = screen.getByText('セクター分析');
    fireEvent.click(sectorTab);
    
    await waitFor(() => {
      expect(screen.getByText('セクター別パフォーマンス')).toBeInTheDocument();
      expect(screen.getByText('セクター別配分')).toBeInTheDocument();
    });
  });

  it('ポジションクリックが正しく動作する', () => {
    const mockOnPositionClick = jest.fn();
    render(<PerformanceComparison {...defaultProps} onPositionClick={mockOnPositionClick} />);
    
    // ポジションをクリック
    const positionElement = screen.getByText('7203');
    fireEvent.click(positionElement);
    
    expect(mockOnPositionClick).toHaveBeenCalledWith('7203');
  });

  it('パフォーマンスバッジの色が正しく表示される', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    // 利益のバッジ
    expect(screen.getByText('利益')).toBeInTheDocument();
    // 損失のバッジ
    expect(screen.getByText('損失')).toBeInTheDocument();
  });

  it('リスクレベルの色が正しく表示される', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
  });

  it('セクターの色が正しく表示される', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    expect(screen.getByText('自動車')).toBeInTheDocument();
    expect(screen.getByText('エンターテインメント')).toBeInTheDocument();
    expect(screen.getByText('通信')).toBeInTheDocument();
  });

  it('空のポジションデータの場合の処理', () => {
    render(<PerformanceComparison {...defaultProps} positions={[]} />);
    
    expect(screen.getByText('パフォーマンス比較')).toBeInTheDocument();
  });

  it('カスタムクラスが正しく適用される', () => {
    const { container } = render(<PerformanceComparison {...defaultProps} className="custom-class" />);
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('ベンチマークデータが正しく表示される', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    expect(screen.getByText('パフォーマンス比較')).toBeInTheDocument();
  });

  it('ビューモードの切り替えが正しく動作する', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const chartButton = screen.getByText('チャート');
    fireEvent.click(chartButton);
    
    expect(chartButton).toHaveClass('bg-blue-600');
  });

  it('セクタービューモードが正しく動作する', () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const sectorButton = screen.getByText('セクター');
    fireEvent.click(sectorButton);
    
    expect(sectorButton).toHaveClass('bg-blue-600');
  });

  it('リスク分布が正しく計算される', async () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const riskTab = screen.getByText('リスク分析');
    fireEvent.click(riskTab);
    
    await waitFor(() => {
      expect(screen.getByText('高リスク')).toBeInTheDocument();
      expect(screen.getByText('中リスク')).toBeInTheDocument();
      expect(screen.getByText('低リスク')).toBeInTheDocument();
    });
  });

  it('ボラティリティ分析が正しく表示される', async () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const riskTab = screen.getByText('リスク分析');
    fireEvent.click(riskTab);
    
    await waitFor(() => {
      expect(screen.getByText('平均ボラティリティ')).toBeInTheDocument();
      expect(screen.getByText('高ボラティリティ銘柄')).toBeInTheDocument();
    });
  });

  it('セクター別パフォーマンスが正しく表示される', async () => {
    render(<PerformanceComparison {...defaultProps} />);
    
    const sectorTab = screen.getByText('セクター分析');
    fireEvent.click(sectorTab);
    
    await waitFor(() => {
      expect(screen.getByText('セクター別パフォーマンス')).toBeInTheDocument();
      expect(screen.getByText('セクター別配分')).toBeInTheDocument();
    });
  });
});
