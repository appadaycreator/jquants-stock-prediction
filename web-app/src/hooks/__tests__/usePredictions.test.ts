import { renderHook, act } from '@testing-library/react';
import { usePredictions } from '../usePredictions';

// Mock the unifiedApiClient
jest.mock('@/lib/unified-api-client', () => ({
  unifiedApiClient: {
    getPredictions: jest.fn(),
  },
}));

// Mock the useAnalysisWithSettings hook
jest.mock('../useAnalysisWithSettings', () => ({
  useAnalysisWithSettings: () => ({
    runAnalysisWithSettings: jest.fn(),
    isAnalyzing: false,
    analysisProgress: 0,
    analysisStatus: 'idle',
  }),
}));

describe('usePredictions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with correct default values', () => {
    const { result } = renderHook(() => usePredictions());
    
    expect(result.current.predictions).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
    expect(typeof result.current.refreshPredictions).toBe('function');
  });

  it('handles successful prediction fetch', async () => {
    const mockPredictions = [
      {
        symbol: '7203',
        companyName: 'トヨタ自動車',
        prediction: 'BUY',
        confidence: 0.85,
        price: 2500,
        change: 0.05,
      },
    ];

    const { unifiedApiClient } = require('@/lib/unified-api-client');
    unifiedApiClient.getPredictions.mockResolvedValue(mockPredictions);

    const { result } = renderHook(() => usePredictions());

    act(() => {
      result.current.refreshPredictions();
    });

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.predictions).toEqual(mockPredictions);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('handles API errors gracefully', async () => {
    const { unifiedApiClient } = require('@/lib/unified-api-client');
    unifiedApiClient.getPredictions.mockRejectedValue(new Error('API Error'));

    const { result } = renderHook(() => usePredictions());

    act(() => {
      result.current.refreshPredictions();
    });

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.predictions).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('API Error');
  });

  it('sets loading state during fetch', async () => {
    const { unifiedApiClient } = require('@/lib/unified-api-client');
    let resolvePromise;
    const promise = new Promise(resolve => {
      resolvePromise = resolve;
    });
    unifiedApiClient.getPredictions.mockReturnValue(promise);

    const { result } = renderHook(() => usePredictions());

    act(() => {
      result.current.refreshPredictions();
    });

    expect(result.current.isLoading).toBe(true);

    act(() => {
      resolvePromise([]);
    });

    await act(async () => {
      await promise;
    });

    expect(result.current.isLoading).toBe(false);
  });
});
