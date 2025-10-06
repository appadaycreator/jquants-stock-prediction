/**
 * 銘柄コード変換ユーティリティ
 * 4桁と5桁の銘柄コードを相互変換
 */

export interface StockCodeMapping {
  [key: string]: string;
}

/**
 * 銘柄コードを正規化（2024年1月以降の新形式対応）
 * - 新形式: 先頭アルファベット+4桁 → 大文字に統一
 * - 従来形式: 数字のみ → 先頭0の除去（5桁の0埋めは4桁へ）
 */
export function normalizeStockCode(code: string): string {
  if (!code) return "";
  const trimmed = code.trim();

  // 新形式（アルファベット+4桁）は大文字に統一
  if (/^[A-Za-z]\d{4}$/.test(trimmed)) {
    return trimmed.toUpperCase();
  }

  // 数字のみ（従来形式想定）
  if (/^\d+$/.test(trimmed)) {
    // 5桁かつ先頭0 → 4桁に正規化
    if (trimmed.length === 5 && trimmed.startsWith("0")) {
      return trimmed.substring(1);
    }
    // それ以外はそのまま（4桁が想定の中心）
    return trimmed;
  }

  // その他はトリムのみ反映
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
  if (!code) return "";
  const trimmed = code.trim();

  // 新形式はそのまま大文字表記
  if (/^[A-Za-z]\d{4}$/.test(trimmed)) {
    return trimmed.toUpperCase();
  }

  // 5桁0埋めは4桁で表示
  if (/^\d{5}$/.test(trimmed) && trimmed.startsWith("0")) {
    return trimmed.substring(1);
  }

  // 4桁はそのまま
  if (/^\d{4}$/.test(trimmed)) {
    return trimmed;
  }

  // その他はそのまま返却（未知形式）
  return trimmed;
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

/**
 * みんかぶ等、従来4桁数値のみを受け付ける外部リンク向けの4桁数値を返す。
 * 条件を満たさない場合は null。
 */
export function toLegacyNumericCodeOrNull(code: string): string | null {
  if (!code) return null;
  const normalized = normalizeStockCode(code);
  if (/^\d{4}$/.test(normalized)) return normalized;
  return null;
}
