/**
 * 銘柄コードユーティリティのテスト
 * 2024年1月以降の新形式（アルファベット含む）に対応
 */

import {
  normalizeStockCode,
  isValidStockCode,
  getStockCodeFormat,
  getStockCodeLabel,
  formatStockCode,
  toFiveDigitCode
} from '../../lib/stock-code-utils';

describe('StockCodeUtils', () => {
  describe('normalizeStockCode', () => {
    it('従来形式（4桁数字）を正規化する', () => {
      expect(normalizeStockCode('7203')).toBe('7203');
      expect(normalizeStockCode('8035')).toBe('8035');
      expect(normalizeStockCode('6758')).toBe('6758');
    });

    it('5桁数字を4桁に正規化する', () => {
      expect(normalizeStockCode('07203')).toBe('7203');
      expect(normalizeStockCode('72030')).toBe('72030'); // 末尾0は除去しない
    });

    it('新形式（アルファベット含む）を大文字に正規化する', () => {
      expect(normalizeStockCode('A1234')).toBe('A1234');
      expect(normalizeStockCode('a1234')).toBe('A1234');
      expect(normalizeStockCode('B0001')).toBe('B0001');
      expect(normalizeStockCode('b0001')).toBe('B0001');
    });

    it('空文字やnullを適切に処理する', () => {
      expect(normalizeStockCode('')).toBe('');
      expect(normalizeStockCode('   ')).toBe('');
    });
  });

  describe('isValidStockCode', () => {
    it('有効な従来形式コードを認識する', () => {
      expect(isValidStockCode('7203')).toBe(true);
      expect(isValidStockCode('8035')).toBe(true);
      expect(isValidStockCode('6758')).toBe(true);
    });

    it('有効な新形式コードを認識する', () => {
      expect(isValidStockCode('A1234')).toBe(true);
      expect(isValidStockCode('B0001')).toBe(true);
      expect(isValidStockCode('C9999')).toBe(true);
    });

    it('無効なコードを拒否する', () => {
      expect(isValidStockCode('123')).toBe(false);      // 3桁
      expect(isValidStockCode('12345')).toBe(false);     // 5桁数字
      expect(isValidStockCode('AB1234')).toBe(false);   // 2文字アルファベット
      expect(isValidStockCode('A123')).toBe(false);     // 3桁数字
      expect(isValidStockCode('1234A')).toBe(false);    // 末尾アルファベット
      expect(isValidStockCode('')).toBe(false);        // 空文字
    });
  });

  describe('getStockCodeFormat', () => {
    it('従来形式を正しく判定する', () => {
      expect(getStockCodeFormat('7203')).toBe('legacy');
      expect(getStockCodeFormat('8035')).toBe('legacy');
      expect(getStockCodeFormat('6758')).toBe('legacy');
    });

    it('新形式を正しく判定する', () => {
      expect(getStockCodeFormat('A1234')).toBe('new');
      expect(getStockCodeFormat('B0001')).toBe('new');
      expect(getStockCodeFormat('C9999')).toBe('new');
    });

    it('無効な形式を正しく判定する', () => {
      expect(getStockCodeFormat('123')).toBe('invalid');
      expect(getStockCodeFormat('12345')).toBe('invalid');
      expect(getStockCodeFormat('AB1234')).toBe('invalid');
      expect(getStockCodeFormat('')).toBe('invalid');
    });
  });

  describe('getStockCodeLabel', () => {
    it('従来形式のラベルを生成する', () => {
      expect(getStockCodeLabel('7203')).toBe('従来形式: 7203');
      expect(getStockCodeLabel('8035')).toBe('従来形式: 8035');
    });

    it('新形式のラベルを生成する', () => {
      expect(getStockCodeLabel('A1234')).toBe('新形式: A1234');
      expect(getStockCodeLabel('B0001')).toBe('新形式: B0001');
    });

    it('無効な形式のラベルを生成する', () => {
      expect(getStockCodeLabel('123')).toBe('無効: 123');
      expect(getStockCodeLabel('')).toBe('無効: ');
    });
  });

  describe('formatStockCode', () => {
    it('5桁で末尾が0の場合は4桁に変換する', () => {
      expect(formatStockCode('72030')).toBe('7203');
      expect(formatStockCode('80350')).toBe('8035');
    });

    it('4桁の場合はそのまま返す', () => {
      expect(formatStockCode('7203')).toBe('7203');
      expect(formatStockCode('8035')).toBe('8035');
    });

    it('新形式の場合はそのまま返す', () => {
      expect(formatStockCode('A1234')).toBe('A1234');
      expect(formatStockCode('B0001')).toBe('B0001');
    });

    it('空文字の場合は空文字を返す', () => {
      expect(formatStockCode('')).toBe('');
    });
  });

  describe('toFiveDigitCode', () => {
    it('4桁の場合は先頭に0を追加する', () => {
      expect(toFiveDigitCode('7203')).toBe('07203');
      expect(toFiveDigitCode('8035')).toBe('08035');
    });

    it('5桁の場合はそのまま返す', () => {
      expect(toFiveDigitCode('07203')).toBe('07203');
      expect(toFiveDigitCode('72030')).toBe('72030');
    });

    it('新形式の場合はそのまま返す', () => {
      expect(toFiveDigitCode('A1234')).toBe('A1234');
      expect(toFiveDigitCode('B0001')).toBe('B0001');
    });

    it('空文字の場合は空文字を返す', () => {
      expect(toFiveDigitCode('')).toBe('');
    });
  });

  describe('統合テスト', () => {
    it('従来形式の完全なワークフロー', () => {
      const code = '7203';
      
      expect(normalizeStockCode(code)).toBe('7203');
      expect(isValidStockCode(code)).toBe(true);
      expect(getStockCodeFormat(code)).toBe('legacy');
      expect(getStockCodeLabel(code)).toBe('従来形式: 7203');
      expect(formatStockCode(code)).toBe('7203');
      expect(toFiveDigitCode(code)).toBe('07203');
    });

    it('新形式の完全なワークフロー', () => {
      const code = 'A1234';
      
      expect(normalizeStockCode(code)).toBe('A1234');
      expect(isValidStockCode(code)).toBe(true);
      expect(getStockCodeFormat(code)).toBe('new');
      expect(getStockCodeLabel(code)).toBe('新形式: A1234');
      expect(formatStockCode(code)).toBe('A1234');
      expect(toFiveDigitCode(code)).toBe('A1234');
    });

    it('5桁数字の完全なワークフロー', () => {
      const code = '07203';
      
      expect(normalizeStockCode(code)).toBe('7203');
      expect(isValidStockCode(code)).toBe(true);
      expect(getStockCodeFormat(code)).toBe('legacy');
      expect(getStockCodeLabel(code)).toBe('従来形式: 7203');
      expect(formatStockCode(code)).toBe('7203');
      expect(toFiveDigitCode(code)).toBe('07203');
    });
  });
});
