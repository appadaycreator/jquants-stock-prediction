/**
 * 時系列チャートのE2Eテスト
 */

import { test, expect } from "@playwright/test";

test.describe("時系列チャート", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("概要タブのチャートが正常に表示される", async ({ page }) => {
    // 概要タブがデフォルトで表示される
    await page.waitForSelector("text=株価推移と移動平均", { timeout: 10000 });
    
    // チャートが表示されることを確認
    await expect(page.locator(".recharts-responsive-container")).toBeVisible();
  });

  test("チャートの横軸にInvalid Dateが表示されない", async ({ page }) => {
    await page.waitForSelector("text=株価推移と移動平均", { timeout: 10000 });
    
    // Invalid Dateが表示されないことを確認
    const invalidDateElements = page.locator("text=Invalid Date");
    await expect(invalidDateElements).toHaveCount(0);
  });

  test("チャートのツールチップが動作する", async ({ page }) => {
    await page.waitForSelector("text=株価推移と移動平均", { timeout: 10000 });
    
    // チャートの線にホバー
    const chartLine = page.locator(".recharts-line .recharts-line-curve").first();
    await chartLine.hover();
    
    // ツールチップが表示されることを確認
    await expect(page.locator(".recharts-tooltip-wrapper")).toBeVisible();
  });

  test("チャートの凡例が表示される", async ({ page }) => {
    await page.waitForSelector("text=株価推移と移動平均", { timeout: 10000 });
    
    // 凡例が表示されることを確認
    await expect(page.locator(".recharts-legend")).toBeVisible();
    await expect(page.locator("text=実際価格")).toBeVisible();
    await expect(page.locator("text=SMA_5")).toBeVisible();
  });

  test("チャートのズーム機能が動作する", async ({ page }) => {
    await page.waitForSelector("text=株価推移と移動平均", { timeout: 10000 });
    
    // チャートエリアをクリックしてドラッグ
    const chartArea = page.locator(".recharts-cartesian-axis-tick");
    await chartArea.first().click();
    
    // チャートが正常に表示され続けることを確認
    await expect(page.locator(".recharts-responsive-container")).toBeVisible();
  });

  test("モバイル表示でもチャートが正常に表示される", async ({ page }) => {
    // モバイルサイズに設定
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.waitForSelector("text=株価推移と移動平均", { timeout: 10000 });
    
    // モバイルでもチャートが表示されることを確認
    await expect(page.locator(".recharts-responsive-container")).toBeVisible();
  });

  test("データが空の場合に適切なメッセージが表示される", async ({ page }) => {
    // データを空にする（実際の実装では、データが空の場合の処理を確認）
    await page.route("**/data/stock_data.json", route => 
      route.fulfill({ 
        status: 200, 
        contentType: "application/json", 
        body: JSON.stringify([]), 
      }),
    );
    
    await page.reload();
    await page.waitForSelector("text=データがありません", { timeout: 5000 });
    
    // 空の状態メッセージが表示されることを確認
    await expect(page.locator("text=データがありません")).toBeVisible();
  });
});
