/**
 * 新NISA枠管理機能の型定義テスト
 */

import { NISA_CONSTANTS } from "../types";

describe("NISA_CONSTANTS", () => {
  it("正しい定数値を定義している", () => {
    expect(NISA_CONSTANTS.GROWTH_ANNUAL_LIMIT).toBe(2_400_000);
    expect(NISA_CONSTANTS.GROWTH_TAX_FREE_LIMIT).toBe(12_000_000);
    expect(NISA_CONSTANTS.ACCUMULATION_ANNUAL_LIMIT).toBe(400_000);
    expect(NISA_CONSTANTS.ACCUMULATION_TAX_FREE_LIMIT).toBe(2_000_000);
  });
});
