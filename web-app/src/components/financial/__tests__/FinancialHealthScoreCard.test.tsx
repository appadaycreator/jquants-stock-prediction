/**
 * 財務健全性スコアカードコンポーネントのテスト
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { FinancialHealthScoreCard } from '../FinancialHealthScoreCard';
import { FinancialHealthScore } from '@/lib/financial/types';

describe('FinancialHealthScoreCard', () => {
  const mockHealthScore: FinancialHealthScore = {
    overallScore: 85.5,
    profitabilityScore: 88.2,
    marketScore: 82.1,
    safetyScore: 90.3,
    growthScore: 85.7,
    grade: 'A',
    recommendation: 'Buy',
    riskLevel: 'Low',
    strengths: ['高いROE', '安定した収益性', '健全な財務体質'],
    weaknesses: ['成長率の鈍化'],
    opportunities: ['新規事業展開', '海外市場進出'],
    threats: ['競合他社の参入', '原材料価格上昇'],
  };

  it('財務健全性スコアを正しく表示する', () => {
    render(<FinancialHealthScoreCard healthScore={mockHealthScore} />);
    
    expect(screen.getByText('財務健全性スコア')).toBeInTheDocument();
    expect(screen.getByText('85.5')).toBeInTheDocument();
    expect(screen.getByText('A')).toBeInTheDocument();
    expect(screen.getByText('Buy')).toBeInTheDocument();
    expect(screen.getByText('リスクレベル: Low')).toBeInTheDocument();
  });

  it('詳細スコアを正しく表示する', () => {
    render(<FinancialHealthScoreCard healthScore={mockHealthScore} />);
    
    expect(screen.getByText('収益性')).toBeInTheDocument();
    expect(screen.getByText('88.2')).toBeInTheDocument();
    
    expect(screen.getByText('市場評価')).toBeInTheDocument();
    expect(screen.getByText('82.1')).toBeInTheDocument();
    
    expect(screen.getByText('安全性')).toBeInTheDocument();
    expect(screen.getByText('90.3')).toBeInTheDocument();
    
    expect(screen.getByText('成長性')).toBeInTheDocument();
    expect(screen.getByText('85.7')).toBeInTheDocument();
  });

  it('SWOT分析を正しく表示する', () => {
    render(<FinancialHealthScoreCard healthScore={mockHealthScore} />);
    
    // 強みの表示確認
    expect(screen.getByText('強み')).toBeInTheDocument();
    expect(screen.getByText('高いROE')).toBeInTheDocument();
    expect(screen.getByText('安定した収益性')).toBeInTheDocument();
    expect(screen.getByText('健全な財務体質')).toBeInTheDocument();
    
    // 弱みの表示確認
    expect(screen.getByText('弱み')).toBeInTheDocument();
    expect(screen.getByText('成長率の鈍化')).toBeInTheDocument();
    
    // 機会の表示確認
    expect(screen.getByText('機会')).toBeInTheDocument();
    expect(screen.getByText('新規事業展開')).toBeInTheDocument();
    expect(screen.getByText('海外市場進出')).toBeInTheDocument();
    
    // 脅威の表示確認
    expect(screen.getByText('脅威')).toBeInTheDocument();
    expect(screen.getByText('競合他社の参入')).toBeInTheDocument();
    expect(screen.getByText('原材料価格上昇')).toBeInTheDocument();
  });

  it('スコアに基づく色を正しく適用する', () => {
    const { container } = render(<FinancialHealthScoreCard healthScore={mockHealthScore} />);
    
    // 高スコアの色確認
    const overallScore = screen.getByText('85.5');
    expect(overallScore).toHaveClass('text-gray-900');
    
    const grade = screen.getByText('A');
    expect(grade).toHaveClass('text-green-600');
    
    const recommendation = screen.getByText('Buy');
    expect(recommendation).toHaveClass('text-green-600');
    
    const riskLevel = screen.getByText('リスクレベル: Low');
    expect(riskLevel).toHaveClass('text-green-600');
  });

  it('低スコアの色を正しく適用する', () => {
    const lowScore: FinancialHealthScore = {
      ...mockHealthScore,
      overallScore: 45.2,
      grade: 'D',
      recommendation: 'Sell',
      riskLevel: 'High',
    };
    
    render(<FinancialHealthScoreCard healthScore={lowScore} />);
    
    const grade = screen.getByText('D');
    expect(grade).toHaveClass('text-orange-600');
    
    const recommendation = screen.getByText('Sell');
    expect(recommendation).toHaveClass('text-red-600');
    
    const riskLevel = screen.getByText('リスクレベル: High');
    expect(riskLevel).toHaveClass('text-red-600');
  });

  it('カスタムクラス名を正しく適用する', () => {
    const { container } = render(
      <FinancialHealthScoreCard healthScore={mockHealthScore} className="custom-class" />
    );
    
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('空のSWOT分析を正しく処理する', () => {
    const emptySWOT: FinancialHealthScore = {
      ...mockHealthScore,
      strengths: [],
      weaknesses: [],
      opportunities: [],
      threats: [],
    };
    
    render(<FinancialHealthScoreCard healthScore={emptySWOT} />);
    
    expect(screen.getByText('強み')).toBeInTheDocument();
    expect(screen.getByText('弱み')).toBeInTheDocument();
    expect(screen.getByText('機会')).toBeInTheDocument();
    expect(screen.getByText('脅威')).toBeInTheDocument();
  });

  it('レスポンシブレイアウトを正しく適用する', () => {
    render(<FinancialHealthScoreCard healthScore={mockHealthScore} />);
    
    const gridContainer = screen.getByText('収益性').closest('.grid');
    expect(gridContainer).toHaveClass('grid-cols-2', 'md:grid-cols-4');
    
    const swotGrid = screen.getByText('強み').closest('.grid');
    expect(swotGrid).toHaveClass('grid-cols-1', 'md:grid-cols-2');
  });
});
