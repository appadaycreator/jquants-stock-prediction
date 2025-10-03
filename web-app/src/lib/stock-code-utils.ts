/**
 * 銘柄コード変換ユーティリティ
 * 4桁と5桁の銘柄コードを相互変換
 */

export interface StockCodeMapping {
  [key: string]: string;
}

/**
 * 銘柄コードを正規化（4桁に統一）
 */
export function normalizeStockCode(code: string): string {
  if (!code) return '';
  
  // 5桁で先頭が0の場合は4桁に変換
  if (code.length === 5 && code.startsWith('0')) {
    return code.substring(1);
  }
  
  // 4桁の場合はそのまま
  if (code.length === 4) {
    return code;
  }
  
  // その他の場合はそのまま
  return code;
}

/**
 * 銘柄コードを5桁形式に変換
 */
export function toFiveDigitCode(code: string): string {
  if (!code) return '';
  
  // 4桁の場合は先頭に0を追加
  if (code.length === 4) {
    return '0' + code;
  }
  
  // 5桁の場合はそのまま
  if (code.length === 5) {
    return code;
  }
  
  // その他の場合はそのまま
  return code;
}

/**
 * 銘柄コードの表示用フォーマット
 */
export function formatStockCode(code: string): string {
  console.log('🔍 formatStockCode called with:', code, 'type:', typeof code, 'length:', code?.length);
  
  if (!code) {
    console.log('❌ formatStockCode: empty code, returning empty string');
    return '';
  }
  
  // 5桁で下1桁が0の場合は除去して4桁で表示
  if (code.length === 5 && code.endsWith('0')) {
    const result = code.substring(0, 4);
    console.log('✅ formatStockCode: 5-digit code ending with 0, converting', code, '→', result);
    return result;
  }
  
  // その他の場合はそのまま表示
  console.log('ℹ️ formatStockCode: no conversion needed, returning:', code);
  return code;
}

/**
 * 銘柄コードが有効かチェック
 */
export function isValidStockCode(code: string): boolean {
  if (!code) return false;
  
  const normalized = normalizeStockCode(code);
  return /^\d{4}$/.test(normalized);
}
