import { renderHook, act } from '@testing-library/react';
import { usePredictions } from '../usePredictions';

// Mock the fetchJson function
jest.mock('@/lib/fetcher', () => ({
  fetchJson: jest.fn(),
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
    expect(typeof result.current.refetch).toBe('function');
  });

  it('handles successful prediction fetch', async () => {
    const mockPredictions = [
      {
        symbol: '7203',
        name: 'トヨタ自動車',
        currentPrice: 2500,
        predictedPrice: 2600,
        confidence: 0.85,
        recommendation: 'BUY',
        timeframe: '1週間',
        lastUpdated: '2024-01-01T00:00:00Z',
      },
    ];

    const { fetchJson } = require('@/lib/fetcher');
    fetchJson.mockResolvedValue({
      predictions: mockPredictions,
      lastUpdated: '2024-01-01T00:00:00Z',
      totalPredictions: 1,
    });

    const { result } = renderHook(() => usePredictions());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.predictions).toEqual(mockPredictions);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('handles API errors gracefully', async () => {
    const { fetchJson } = require('@/lib/fetcher');
    fetchJson.mockRejectedValue(new Error('API Error'));

    const { result } = renderHook(() => usePredictions());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.predictions).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('API Error');
  });

  it('sets loading state during fetch', async () => {
    const { fetchJson } = require('@/lib/fetcher');
    let resolvePromise;
    const promise = new Promise(resolve => {
      resolvePromise = resolve;
    });
    fetchJson.mockReturnValue(promise);

    const { result } = renderHook(() => usePredictions());

    expect(result.current.isLoading).toBe(true);

    act(() => {
      resolvePromise({
        predictions: [],
        lastUpdated: '2024-01-01T00:00:00Z',
        totalPredictions: 0,
      });
    });

    await act(async () => {
      await promise;
    });

    expect(result.current.isLoading).toBe(false);
  });
});
