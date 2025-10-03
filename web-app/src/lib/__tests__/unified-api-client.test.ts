import { unifiedApiClient } from '../unified-api-client';

// Mock the fetch function
global.fetch = jest.fn();

describe('unified-api-client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getStockData', () => {
    it('fetches stock data successfully', async () => {
      const mockData = {
        symbol: '7203',
        companyName: 'トヨタ自動車',
        price: 2500,
        change: 0.05,
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      });

      const result = await unifiedApiClient.getStockData('7203');

      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/stocks/7203')
      );
    });

    it('handles API errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      });

      await expect(unifiedApiClient.getStockData('INVALID')).rejects.toThrow();
    });

    it('handles network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network Error'));

      await expect(unifiedApiClient.getStockData('7203')).rejects.toThrow('Network Error');
    });
  });

  describe('getMarketData', () => {
    it('fetches market data successfully', async () => {
      const mockData = {
        marketStatus: 'open',
        indices: [
          { name: '日経平均', value: 30000, change: 0.02 },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      });

      const result = await unifiedApiClient.getMarketData();

      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/market')
      );
    });
  });

  describe('getPredictions', () => {
    it('fetches predictions successfully', async () => {
      const mockPredictions = [
        {
          symbol: '7203',
          prediction: 'BUY',
          confidence: 0.85,
        },
      ];

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockPredictions),
      });

      const result = await unifiedApiClient.getPredictions();

      expect(result).toEqual(mockPredictions);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/predictions')
      );
    });
  });

  describe('getPersonalInvestmentData', () => {
    it('fetches personal investment data successfully', async () => {
      const mockData = {
        totalValue: 1000000,
        dailyChange: 5000,
        portfolio: [
          { symbol: '7203', value: 500000, weight: 0.5 },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      });

      const result = await unifiedApiClient.getPersonalInvestmentData();

      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/personal-investment')
      );
    });
  });
});
