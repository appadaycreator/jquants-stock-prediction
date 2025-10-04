/**
 * 新NISA取引記録管理APIのテスト
 */

import { POST, PUT, DELETE } from '../transaction/route';
import { NextRequest } from 'next/server';

// モック
jest.mock('@/lib/nisa', () => ({
  NisaManager: jest.fn().mockImplementation(() => ({
    initialize: jest.fn().mockResolvedValue(true),
    addTransaction: jest.fn().mockResolvedValue({
      isValid: true,
      errors: [],
      warnings: [],
    }),
    storage: {
      updateTransaction: jest.fn().mockResolvedValue({
        isValid: true,
        errors: [],
        warnings: [],
      }),
      deleteTransaction: jest.fn().mockResolvedValue({
        isValid: true,
        errors: [],
        warnings: [],
      }),
    },
  })),
}));

describe('/api/nisa/transaction', () => {
  describe('POST', () => {
    it('正常な取引追加を処理する', async () => {
      const transaction = {
        type: 'BUY',
        symbol: '7203',
        symbolName: 'トヨタ自動車',
        quantity: 100,
        price: 2500,
        amount: 250_000,
        quotaType: 'GROWTH',
        transactionDate: '2024-01-15',
      };

      const request = new NextRequest('http://localhost:3000/api/nisa/transaction', {
        method: 'POST',
        body: JSON.stringify(transaction),
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.data.message).toBe('取引記録が正常に追加されました');
    });

    it('バリデーションエラーを処理する', async () => {
      // モックを変更
      const { NisaManager } = require('@/lib/nisa');
      NisaManager.mockImplementation(() => ({
        initialize: jest.fn().mockResolvedValue(true),
        addTransaction: jest.fn().mockResolvedValue({
          isValid: false,
          errors: ['取引データが無効です'],
          warnings: [],
        }),
      }));

      const transaction = {
        type: 'INVALID',
        symbol: '',
        symbolName: '',
        quantity: 0,
        price: -100,
        amount: 0,
        quotaType: 'INVALID',
        transactionDate: '2024-01-15',
      };

      const request = new NextRequest('http://localhost:3000/api/nisa/transaction', {
        method: 'POST',
        body: JSON.stringify(transaction),
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const response = await POST(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('VALIDATION_ERROR');
    });
  });

  describe('PUT', () => {
    it('正常な取引更新を処理する', async () => {
      const updates = {
        id: 'test-id',
        quantity: 200,
        amount: 500_000,
      };

      const request = new NextRequest('http://localhost:3000/api/nisa/transaction', {
        method: 'PUT',
        body: JSON.stringify(updates),
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const response = await PUT(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.data.message).toBe('取引記録が正常に更新されました');
    });

    it('IDが不足している場合は400を返す', async () => {
      const updates = {
        quantity: 200,
        amount: 500_000,
      };

      const request = new NextRequest('http://localhost:3000/api/nisa/transaction', {
        method: 'PUT',
        body: JSON.stringify(updates),
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const response = await PUT(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('VALIDATION_ERROR');
    });
  });

  describe('DELETE', () => {
    it('正常な取引削除を処理する', async () => {
      const request = new NextRequest('http://localhost:3000/api/nisa/transaction?id=test-id', {
        method: 'DELETE',
      });

      const response = await DELETE(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.data.message).toBe('取引記録が正常に削除されました');
    });

    it('IDが不足している場合は400を返す', async () => {
      const request = new NextRequest('http://localhost:3000/api/nisa/transaction', {
        method: 'DELETE',
      });

      const response = await DELETE(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('VALIDATION_ERROR');
    });
  });
});
