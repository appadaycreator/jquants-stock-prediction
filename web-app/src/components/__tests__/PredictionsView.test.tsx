import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PredictionsView from '../PredictionsView';

// Mock the usePredictions hook
jest.mock('@/hooks/usePredictions', () => ({
  usePredictions: () => ({
    predictions: [
      {
        symbol: '7203',
        companyName: 'トヨタ自動車',
        prediction: 'BUY',
        confidence: 0.85,
        price: 2500,
        change: 0.05,
      },
    ],
    isLoading: false,
    error: null,
    refreshPredictions: jest.fn(),
  }),
}));

// Mock the useAnalysisWithSettings hook
jest.mock('@/hooks/useAnalysisWithSettings', () => ({
  useAnalysisWithSettings: () => ({
    runAnalysisWithSettings: jest.fn(),
    isAnalyzing: false,
    analysisProgress: 0,
    analysisStatus: 'idle',
    getAnalysisDescription: jest.fn(() => 'Test analysis'),
  }),
}));

describe('PredictionsView', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the component without crashing', () => {
    render(<PredictionsView />);
    expect(screen.getByText('予測結果')).toBeInTheDocument();
  });

  it('displays predictions data correctly', () => {
    render(<PredictionsView />);
    expect(screen.getByText('トヨタ自動車')).toBeInTheDocument();
    expect(screen.getByText('BUY')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('shows loading state when analyzing', () => {
    const mockUsePredictions = require('@/hooks/usePredictions').usePredictions;
    mockUsePredictions.mockReturnValue({
      predictions: [],
      isLoading: true,
      error: null,
      refreshPredictions: jest.fn(),
    });

    render(<PredictionsView />);
    expect(screen.getByText('分析中...')).toBeInTheDocument();
  });

  it('handles error state correctly', () => {
    const mockUsePredictions = require('@/hooks/usePredictions').usePredictions;
    mockUsePredictions.mockReturnValue({
      predictions: [],
      isLoading: false,
      error: 'API Error',
      refreshPredictions: jest.fn(),
    });

    render(<PredictionsView />);
    expect(screen.getByText('エラーが発生しました')).toBeInTheDocument();
  });

  it('calls refreshPredictions when refresh button is clicked', async () => {
    const mockRefreshPredictions = jest.fn();
    const mockUsePredictions = require('@/hooks/usePredictions').usePredictions;
    mockUsePredictions.mockReturnValue({
      predictions: [],
      isLoading: false,
      error: null,
      refreshPredictions: mockRefreshPredictions,
    });

    render(<PredictionsView />);
    const refreshButton = screen.getByRole('button', { name: /更新/i });
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(mockRefreshPredictions).toHaveBeenCalled();
    });
  });
});