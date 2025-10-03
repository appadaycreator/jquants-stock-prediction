/**
 * datetime.ts のテスト
 */

import { formatDateTime, parseDateTime, getRelativeTime, isValidDate } from "../datetime";

describe("datetime", () => {
  describe("formatDateTime", () => {
    it("正常な日付をフォーマットする", () => {
      const date = new Date("2024-01-15T10:30:00Z");
      const result = formatDateTime(date);
      expect(result).toContain("2024");
      expect(result).toContain("01");
      expect(result).toContain("15");
    });

    it("nullを処理する", () => {
      const result = formatDateTime(null);
      expect(result).toBe("--");
    });
  });

  describe("parseDateTime", () => {
    it("有効な日付文字列をパースする", () => {
      const result = parseDateTime("2024-01-15T10:30:00Z");
      expect(result).toBeInstanceOf(Date);
    });

    it("無効な日付文字列を処理する", () => {
      const result = parseDateTime("invalid");
      expect(result).toBeNull();
    });
  });

  describe("getRelativeTime", () => {
    it("過去の時間を相対時間で表示する", () => {
      const pastDate = new Date(Date.now() - 1000 * 60 * 5); // 5分前
      const result = getRelativeTime(pastDate);
      expect(result).toContain("分前");
    });

    it("未来の時間を相対時間で表示する", () => {
      const futureDate = new Date(Date.now() + 1000 * 60 * 5); // 5分後
      const result = getRelativeTime(futureDate);
      expect(result).toContain("分後");
    });
  });

  describe("isValidDate", () => {
    it("有効な日付を検証する", () => {
      const validDate = new Date("2024-01-15");
      expect(isValidDate(validDate)).toBe(true);
    });

    it("無効な日付を検証する", () => {
      const invalidDate = new Date("invalid");
      expect(isValidDate(invalidDate)).toBe(false);
    });

    it("nullを検証する", () => {
      expect(isValidDate(null)).toBe(false);
    });
  });
});