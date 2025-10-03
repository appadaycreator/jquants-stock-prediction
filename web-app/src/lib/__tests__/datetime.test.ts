/**
 * 日付処理ユーティリティのテスト
 */

// import { describe, it, expect } from "vitest";
import { parseToJst, jstLabel, normalizeDateString, formatDate, createChartDateArray } from "../datetime";

describe("datetime utilities", () => {
  describe("parseToJst", () => {
    it("ISO文字列をJSTに正規化する", () => {
      const result = parseToJst("2024-01-15T10:30:00Z");
      expect(result.isValid).toBe(true);
      expect(jstLabel(result)).toBe("2024-01-15");
    });

    it("YYYY-MM-DD形式をJSTに正規化する", () => {
      const result = parseToJst("2024-01-15");
      expect(result.isValid).toBe(true);
      expect(jstLabel(result)).toBe("2024-01-15");
    });

    it("YYYYMMDD形式をJSTに正規化する", () => {
      const result = parseToJst("20240115");
      expect(result.isValid).toBe(true);
      expect(jstLabel(result)).toBe("2024-01-15");
    });

    it("ミリ秒のタイムスタンプをJSTに正規化する", () => {
      const timestamp = 1705305000000; // 2024-01-15 10:30:00 UTC
      const result = parseToJst(timestamp);
      expect(result.isValid).toBe(true);
      expect(jstLabel(result)).toBe("2024-01-15");
    });

    it("秒のタイムスタンプをJSTに正規化する", () => {
      const timestamp = 1705305000; // 2024-01-15 10:30:00 UTC
      const result = parseToJst(timestamp);
      expect(result.isValid).toBe(true);
      expect(jstLabel(result)).toBe("2024-01-15");
    });

    it("無効な日付文字列に対してデフォルト日付を返す", () => {
      const result = parseToJst("invalid-date");
      expect(result.isValid).toBe(true);
      expect(jstLabel(result)).toBe("2024-01-01");
    });
  });

  describe("normalizeDateString", () => {
    it("既にYYYY-MM-DD形式の場合はそのまま返す", () => {
      expect(normalizeDateString("2024-01-15")).toBe("2024-01-15");
    });

    it("YYYYMMDD形式をYYYY-MM-DD形式に変換する", () => {
      expect(normalizeDateString("20240115")).toBe("2024-01-15");
    });

    it("無効な日付文字列に対してデフォルト日付を返す", () => {
      expect(normalizeDateString("invalid")).toBe("2024-01-01");
    });
  });

  describe("formatDate", () => {
    it("有効な日付文字列をフォーマットする", () => {
      expect(formatDate("2024-01-15")).toBe("2024/01/15");
    });

    it("無効な日付文字列に対してInvalid Dateを返す", () => {
      expect(formatDate("invalid")).toBe("2024/01/01");
    });
  });

  describe("createChartDateArray", () => {
    it("日付配列からチャート用データを生成する", () => {
      const dates = ["2024-01-15", "2024-01-16", "2024-01-17"];
      const result = createChartDateArray(dates);
      
      expect(result).toHaveLength(3);
      expect(result[0]).toHaveProperty("date");
      expect(result[0]).toHaveProperty("timestamp");
      expect(result[0].date).toBe("2024-01-15");
      expect(typeof result[0].timestamp).toBe("number");
    });

    it("無効な日付を除外する", () => {
      const dates = ["2024-01-15", "invalid", "2024-01-17"];
      const result = createChartDateArray(dates);
      
      expect(result).toHaveLength(3);
      expect(result[0].date).toBe("2024-01-15");
      expect(result[1].date).toBe("2024-01-01");
      expect(result[2].date).toBe("2024-01-17");
    });
  });
});
