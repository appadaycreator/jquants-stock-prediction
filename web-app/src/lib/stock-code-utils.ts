/**
 * 銘柄コード変換ユーティリティ
 * 4桁と5桁の銘柄コードを相互変換
 */

export interface StockCodeMapping {
  [key: string]: string;
}

/**
 * 銘柄コードを正規化（2024年1月以降の新形式対応）
 */
export function normalizeStockCode(code: string): string {
  if (!code) return "";
  
  const trimmed = code.trim();
  
  // 新形式（アルファベット含む）の場合は大文字に統一
  if (/^[A-Za-z]\d{4}$/.test(trimmed)) {
    return trimmed.toUpperCase();
  }
  
  // 従来形式の処理
  // 5桁で先頭が0の場合は4桁に変換
  if (trimmed.length === 5 && trimmed.startsWith("0")) {
    return trimmed.substring(1);
  }
  
  // 4桁の場合はそのまま
  if (trimmed.length === 4) {
    return trimmed;
  }
  
  // その他の場合はそのまま
  return trimmed;
}

/**
 * 銘柄コードを5桁形式に変換
 */
export function toFiveDigitCode(code: string): string {
  if (!code) return "";
  
  // 4桁の場合は先頭に0を追加
  if (code.length === 4) {
    return "0" + code;
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
  console.log("🔍 formatStockCode called with:", code, "type:", typeof code, "length:", code?.length);
  
  if (!code) {
    console.log("❌ formatStockCode: empty code, returning empty string");
    return "";
  }
  
  // 5桁で下1桁が0の場合は除去して4桁で表示
  if (code.length === 5 && code.endsWith("0")) {
    const result = code.substring(0, 4);
    console.log("✅ formatStockCode: 5-digit code ending with 0, converting", code, "→", result);
    return result;
  }
  
  // その他の場合はそのまま表示
  console.log("ℹ️ formatStockCode: no conversion needed, returning:", code);
  return code;
}

/**
 * 銘柄コードが有効かチェック（2024年1月以降の新形式対応）
 */
export function isValidStockCode(code: string): boolean {
  if (!code) return false;
  
  const normalized = normalizeStockCode(code);
  
  // 新形式（アルファベット含む）のチェック
  if (/^[A-Za-z]\d{4}$/.test(normalized)) {
    return true;
  }
  
  // 従来形式（4桁数字）のチェック
  if (/^\d{4}$/.test(normalized)) {
    return true;
  }
  
  return false;
}

/**
 * 銘柄コードの形式を判定
 */
export function getStockCodeFormat(code: string): "legacy" | "new" | "invalid" {
  if (!code) return "invalid";
  
  const normalized = normalizeStockCode(code);
  
  if (/^[A-Za-z]\d{4}$/.test(normalized)) {
    return "new";
  }
  
  if (/^\d{4}$/.test(normalized)) {
    return "legacy";
  }
  
  return "invalid";
}

/**
 * 銘柄コードの表示用ラベルを取得
 */
export function getStockCodeLabel(code: string): string {
  const format = getStockCodeFormat(code);
  
  switch (format) {
    case "legacy":
      return `従来形式: ${code}`;
    case "new":
      return `新形式: ${code}`;
    default:
      return `無効: ${code}`;
  }
}
