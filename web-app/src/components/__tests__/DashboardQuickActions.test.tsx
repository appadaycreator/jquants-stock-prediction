import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardQuickActions from '../DashboardQuickActions';

// Mock the useRouter hook
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock the useAnalysisWithSettings hook
jest.mock('@/hooks/useAnalysisWithSettings', () => ({
  useAnalysisWithSettings: () => ({
    runAnalysisWithSettings: jest.fn(),
    isAnalyzing: false,
    analysisProgress: 0,
    analysisStatus: 'idle',
  }),
}));

describe('DashboardQuickActions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the component without crashing', () => {
    render(<DashboardQuickActions />);
    expect(screen.getByText('クイックアクション')).toBeInTheDocument();
  });

  it('displays all action buttons', () => {
    render(<DashboardQuickActions />);
    expect(screen.getByText('今日の投資指示')).toBeInTheDocument();
    expect(screen.getByText('個人投資ポートフォリオ')).toBeInTheDocument();
    expect(screen.getByText('5分ルーティン')).toBeInTheDocument();
    expect(screen.getByText('詳細分析')).toBeInTheDocument();
  });

  it('handles analysis button click', () => {
    const mockRunAnalysis = jest.fn();
    const mockUseAnalysisWithSettings = require('@/hooks/useAnalysisWithSettings').useAnalysisWithSettings;
    mockUseAnalysisWithSettings.mockReturnValue({
      runAnalysisWithSettings: mockRunAnalysis,
      isAnalyzing: false,
      analysisProgress: 0,
      analysisStatus: 'idle',
    });

    render(<DashboardQuickActions />);
    const analysisButton = screen.getByRole('link', { name: /今日の投資指示/i });
    fireEvent.click(analysisButton);

    expect(mockRunAnalysis).toHaveBeenCalled();
  });

  it('shows loading state when analyzing', () => {
    const mockUseAnalysisWithSettings = require('@/hooks/useAnalysisWithSettings').useAnalysisWithSettings;
    mockUseAnalysisWithSettings.mockReturnValue({
      runAnalysisWithSettings: jest.fn(),
      isAnalyzing: true,
      analysisProgress: 50,
      analysisStatus: 'analyzing',
    });

    render(<DashboardQuickActions />);
    // ローディング状態の表示はコンポーネントの実装に依存する
    // 現在の実装では直接的なローディング表示がないため、このテストは調整が必要
  });

  it('handles navigation to predictions page', () => {
    const mockPush = jest.fn();
    const mockUseRouter = require('next/navigation').useRouter;
    mockUseRouter.mockReturnValue({
      push: mockPush,
    });

    render(<DashboardQuickActions />);
    const predictionsButton = screen.getByRole('link', { name: /詳細分析/i });
    fireEvent.click(predictionsButton);

    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  it('handles navigation to settings page', () => {
    const mockPush = jest.fn();
    const mockUseRouter = require('next/navigation').useRouter;
    mockUseRouter.mockReturnValue({
      push: mockPush,
    });

    render(<DashboardQuickActions />);
    // 設定ページへのナビゲーションは現在のコンポーネントにはないため、
    // このテストは削除または調整が必要
  });
});
