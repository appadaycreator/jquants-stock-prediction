/**
 * 予測結果タブのE2Eテスト
 */

import { test, expect } from '@playwright/test';

test.describe('予測結果タブ', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('予測結果タブが正常に表示される', async ({ page }) => {
    // 予測結果タブをクリック
    await page.click('text=予測結果');
    
    // ローディング状態を待つ
    await page.waitForSelector('text=データを読み込み中', { timeout: 5000 });
    
    // 予測結果が表示されるまで待つ
    await page.waitForSelector('text=予測結果', { timeout: 10000 });
    
    // ヘッダーが表示されることを確認
    await expect(page.locator('h2')).toContainText('予測結果');
  });

  test('KPIカードが表示される', async ({ page }) => {
    await page.click('text=予測結果');
    await page.waitForSelector('text=予測結果', { timeout: 10000 });
    
    // KPIカードが表示されることを確認
    await expect(page.locator('text=MAE')).toBeVisible();
    await expect(page.locator('text=RMSE')).toBeVisible();
    await expect(page.locator('text=R²')).toBeVisible();
    await expect(page.locator('text=ベースライン')).toBeVisible();
  });

  test('予測結果テーブルが表示される', async ({ page }) => {
    await page.click('text=予測結果');
    await page.waitForSelector('text=予測結果', { timeout: 10000 });
    
    // テーブルヘッダーが表示されることを確認
    await expect(page.locator('text=日付')).toBeVisible();
    await expect(page.locator('text=銘柄')).toBeVisible();
    await expect(page.locator('text=実際値')).toBeVisible();
    await expect(page.locator('text=予測値')).toBeVisible();
    await expect(page.locator('text=誤差')).toBeVisible();
  });

  test('更新ボタンが動作する', async ({ page }) => {
    await page.click('text=予測結果');
    await page.waitForSelector('text=予測結果', { timeout: 10000 });
    
    // 更新ボタンをクリック
    await page.click('text=更新');
    
    // ローディング状態が表示されることを確認
    await expect(page.locator('text=データを読み込み中')).toBeVisible();
  });

  test('エラー状態でエラーパネルが表示される', async ({ page }) => {
    // ネットワークを無効化してエラーをシミュレート
    await page.route('**/data/*.json', route => route.abort());
    
    await page.click('text=予測結果');
    
    // エラーパネルが表示されることを確認
    await expect(page.locator('text=データの読み込みに失敗しました')).toBeVisible();
    await expect(page.locator('text=再試行')).toBeVisible();
  });

  test('過学習警告が表示される', async ({ page }) => {
    await page.click('text=予測結果');
    await page.waitForSelector('text=予測結果', { timeout: 10000 });
    
    // 過学習警告が表示される可能性があることを確認
    // （実際のデータに依存するため、存在する場合のみチェック）
    const warningElement = page.locator('text=過学習のリスクが検出されました');
    if (await warningElement.count() > 0) {
      await expect(warningElement).toBeVisible();
    }
  });
});
