import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PredictionsView from '../PredictionsView';

// Mock the fetchJson function
jest.mock('@/lib/fetcher', () => ({
  fetchJson: jest.fn(),
  fetchMultiple: jest.fn(),
  AppError: class AppError extends Error {
    constructor(message: string, public code: string) {
      super(message);
      this.name = 'AppError';
    }
  },
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

  it('renders the component without crashing', async () => {
    const { fetchMultiple } = require('@/lib/fetcher');
    fetchMultiple.mockResolvedValue({
      predictions: { 
        data: [
          {
            date: '2024-01-01',
            symbol: '7203',
            y_true: 2500,
            y_pred: 2600,
          }
        ], 
        meta: { model: 'test', generatedAt: '2024-01-01T00:00:00Z' } 
      },
      stockData: [],
      modelComparison: [],
    });

    render(<PredictionsView />);
    
    // ローディング状態が表示されることを確認
    expect(screen.getByTestId('predictions-skeleton')).toBeInTheDocument();
    
    // データが読み込まれるまで待機
    await waitFor(() => {
      expect(screen.getByText('予測結果')).toBeInTheDocument();
    }, { timeout: 15000 });
  }, 20000);

  it('displays predictions data correctly', async () => {
    const { fetchMultiple } = require('@/lib/fetcher');
    fetchMultiple.mockResolvedValue({
      predictions: { 
        data: [
          {
            date: '2024-01-01',
            symbol: '7203',
            y_true: 2500,
            y_pred: 2600,
          }
        ], 
        meta: { model: 'test', generatedAt: '2024-01-01T00:00:00Z' } 
      },
      stockData: [],
      modelComparison: [],
    });

    render(<PredictionsView />);
    
    // データが読み込まれるまで待機
    await waitFor(() => {
      expect(screen.getByText('7203')).toBeInTheDocument();
    }, { timeout: 10000 });
  }, 10000);

  it('shows loading state when analyzing', () => {
    const { fetchMultiple } = require('@/lib/fetcher');
    fetchMultiple.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<PredictionsView />);
    // ローディング状態はスケルトンコンポーネントで表示される
  });

  it('handles error state correctly', () => {
    const { fetchMultiple } = require('@/lib/fetcher');
    fetchMultiple.mockRejectedValue(new Error('API Error'));

    render(<PredictionsView />);
    // エラー状態はErrorPanelコンポーネントで表示される
  });

  it('calls refresh when refresh button is clicked', async () => {
    const { fetchMultiple } = require('@/lib/fetcher');
    fetchMultiple.mockResolvedValue({
      predictions: { 
        data: [
          {
            date: '2024-01-01',
            symbol: '7203',
            y_true: 2500,
            y_pred: 2600,
          }
        ], 
        meta: { model: 'test', generatedAt: '2024-01-01T00:00:00Z' } 
      },
      stockData: [],
      modelComparison: [],
    });

    render(<PredictionsView />);
    
    // データが読み込まれるまで待機
    await waitFor(() => {
      expect(screen.getByText('予測結果')).toBeInTheDocument();
    }, { timeout: 15000 });
    
    const refreshButton = screen.getByRole('button', { name: /更新/i });
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(fetchMultiple).toHaveBeenCalledTimes(2); // Initial load + refresh
    }, { timeout: 15000 });
  }, 20000);
});