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

  it('renders the component without crashing', () => {
    const { fetchMultiple } = require('@/lib/fetcher');
    fetchMultiple.mockResolvedValue({
      predictions: { data: [], meta: { model: 'test', generatedAt: '2024-01-01T00:00:00Z' } },
      stockData: [],
      modelComparison: [],
    });

    render(<PredictionsView />);
    expect(screen.getByText('予測結果')).toBeInTheDocument();
  });

  it('displays predictions data correctly', () => {
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
    expect(screen.getByText('7203')).toBeInTheDocument();
  });

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
      predictions: { data: [], meta: { model: 'test', generatedAt: '2024-01-01T00:00:00Z' } },
      stockData: [],
      modelComparison: [],
    });

    render(<PredictionsView />);
    const refreshButton = screen.getByRole('button', { name: /更新/i });
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(fetchMultiple).toHaveBeenCalledTimes(2); // Initial load + refresh
    });
  });
});