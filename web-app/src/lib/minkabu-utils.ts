import { toLegacyNumericCodeOrNull } from "@/lib/stock-code-utils";
/**
 * みんかぶリンクユーティリティ
 * 銘柄コードからみんかぶのURLを生成し、リンクを開く
 */

/**
 * 銘柄コードがみんかぶで利用可能かチェック
 * @param code 銘柄コード
 * @returns 利用可能かどうか
 */
export function isMinkabuLinkAvailable(code: string): boolean {
  return toLegacyNumericCodeOrNull(code) !== null;
}

/**
 * みんかぶのURLを生成
 * @param code 銘柄コード
 * @returns みんかぶのURL
 */
export function generateMinkabuUrl(code: string): string {
  const legacy = toLegacyNumericCodeOrNull(code);
  if (!legacy) throw new Error("無効な銘柄コードです");
  return `https://minkabu.jp/stock/${legacy}`;
}

/**
 * みんかぶのリンクを新しいタブで開く
 * @param code 銘柄コード
 */
export function openMinkabuLink(code: string): void {
  try {
    const url = generateMinkabuUrl(code);
    window.open(url, "_blank", "noopener,noreferrer");
  } catch (error) {
    console.error("みんかぶリンクの生成に失敗しました:", error);
    alert("みんかぶリンクを開けませんでした。銘柄コードを確認してください。");
  }
}

/**
 * 銘柄コードをみんかぶ用に正規化
 * @param code 銘柄コード
 * @returns 正規化された銘柄コード
 */
export function normalizeCodeForMinkabu(code: string): string {
  return toLegacyNumericCodeOrNull(code) || "";
}