import { fetchJson, handleApiError } from '../fetcher';

// Mock the fetch function
global.fetch = jest.fn();

describe('fetcher', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('fetchJson', () => {
    it('fetches data successfully', async () => {
      const mockData = { message: 'Success' };
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockData),
      });

      const result = await fetchJson('/api/test');

      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith('/api/test', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('handles API errors with status codes', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve({ error: 'Not Found' }),
      });

      await expect(fetchJson('/api/test')).rejects.toThrow('Not Found');
    });

    it('handles network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network Error'));

      await expect(fetchJson('/api/test')).rejects.toThrow('Network Error');
    });

    it('handles JSON parsing errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.reject(new Error('Invalid JSON')),
      });

      await expect(fetchJson('/api/test')).rejects.toThrow('Invalid JSON');
    });
  });

  describe('handleApiError', () => {
    it('handles 400 Bad Request', () => {
      const error = {
        status: 400,
        statusText: 'Bad Request',
        data: { error: 'Invalid request' },
      };

      expect(() => handleApiError(error)).toThrow('Bad Request');
    });

    it('handles 401 Unauthorized', () => {
      const error = {
        status: 401,
        statusText: 'Unauthorized',
        data: { error: 'Authentication required' },
      };

      expect(() => handleApiError(error)).toThrow('Unauthorized');
    });

    it('handles 403 Forbidden', () => {
      const error = {
        status: 403,
        statusText: 'Forbidden',
        data: { error: 'Access denied' },
      };

      expect(() => handleApiError(error)).toThrow('Forbidden');
    });

    it('handles 404 Not Found', () => {
      const error = {
        status: 404,
        statusText: 'Not Found',
        data: { error: 'Resource not found' },
      };

      expect(() => handleApiError(error)).toThrow('Not Found');
    });

    it('handles 500 Internal Server Error', () => {
      const error = {
        status: 500,
        statusText: 'Internal Server Error',
        data: { error: 'Server error' },
      };

      expect(() => handleApiError(error)).toThrow('Internal Server Error');
    });

    it('handles unknown status codes', () => {
      const error = {
        status: 999,
        statusText: 'Unknown Error',
        data: { error: 'Unknown error' },
      };

      expect(() => handleApiError(error)).toThrow('Unknown Error');
    });
  });
});