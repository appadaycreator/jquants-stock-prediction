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
    expect(screen.getByText('分析実行')).toBeInTheDocument();
    expect(screen.getByText('予測確認')).toBeInTheDocument();
    expect(screen.getByText('データ更新')).toBeInTheDocument();
    expect(screen.getByText('設定')).toBeInTheDocument();
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
    const analysisButton = screen.getByRole('button', { name: /分析実行/i });
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
    expect(screen.getByText('分析中...')).toBeInTheDocument();
  });

  it('handles navigation to predictions page', () => {
    const mockPush = jest.fn();
    const mockUseRouter = require('next/navigation').useRouter;
    mockUseRouter.mockReturnValue({
      push: mockPush,
    });

    render(<DashboardQuickActions />);
    const predictionsButton = screen.getByRole('button', { name: /予測確認/i });
    fireEvent.click(predictionsButton);

    expect(mockPush).toHaveBeenCalledWith('/predictions');
  });

  it('handles navigation to settings page', () => {
    const mockPush = jest.fn();
    const mockUseRouter = require('next/navigation').useRouter;
    mockUseRouter.mockReturnValue({
      push: mockPush,
    });

    render(<DashboardQuickActions />);
    const settingsButton = screen.getByRole('button', { name: /設定/i });
    fireEvent.click(settingsButton);

    expect(mockPush).toHaveBeenCalledWith('/settings');
  });
});
