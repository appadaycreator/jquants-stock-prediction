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

  // パターン: 3桁 + アルファベット + 0（例: 131A0 → 131A）
  if (/^\d{3}[A-Za-z]0$/.test(trimmed)) {
    return (trimmed.substring(0, 3) + trimmed.charAt(3).toUpperCase());
  }

  // 数字のみ（従来形式想定）
  if (/^\d+$/.test(trimmed)) {
    // 5桁かつ先頭0 → 4桁に正規化
    if (trimmed.length === 5 && trimmed.startsWith("0")) {
      return trimmed.substring(1);
    }
    // 5桁かつ末尾0 → 末尾0を除去して4桁に正規化（例: 30760 → 3076）
    if (trimmed.length === 5 && trimmed.endsWith("0")) {
      const candidate = trimmed.substring(0, 4);
      if (/^\d{4}$/.test(candidate)) return candidate;
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
  const normalized = normalizeStockCode(trimmed);

  // 新形式はそのまま大文字表記
  if (/^[A-Za-z]\d{4}$/.test(normalized)) {
    return normalized.toUpperCase();
  }

  // 4桁数字ならそのまま
  if (/^\d{4}$/.test(normalized)) {
    return normalized;
  }

  // 5桁（先頭0/末尾0）などは normalize 済みのため normalized を返却
  if (/^\d{5}$/.test(trimmed)) {
    return normalized;
  }


  // その他はそのまま返却（未知形式）
  return normalized;
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
