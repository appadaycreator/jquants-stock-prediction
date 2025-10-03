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
  if (!code) return false;
  
  // 4桁の数字のみを対象とする
  const normalizedCode = code.replace(/^0+/, ''); // 先頭の0を除去
  return /^\d{4}$/.test(normalizedCode);
}

/**
 * みんかぶのURLを生成
 * @param code 銘柄コード
 * @returns みんかぶのURL
 */
export function generateMinkabuUrl(code: string): string {
  if (!isMinkabuLinkAvailable(code)) {
    throw new Error('無効な銘柄コードです');
  }
  
  const normalizedCode = code.replace(/^0+/, ''); // 先頭の0を除去
  return `https://minkabu.jp/stock/${normalizedCode}`;
}

/**
 * みんかぶのリンクを新しいタブで開く
 * @param code 銘柄コード
 */
export function openMinkabuLink(code: string): void {
  try {
    const url = generateMinkabuUrl(code);
    window.open(url, '_blank', 'noopener,noreferrer');
  } catch (error) {
    console.error('みんかぶリンクの生成に失敗しました:', error);
    alert('みんかぶリンクを開けませんでした。銘柄コードを確認してください。');
  }
}

/**
 * 銘柄コードをみんかぶ用に正規化
 * @param code 銘柄コード
 * @returns 正規化された銘柄コード
 */
export function normalizeCodeForMinkabu(code: string): string {
  if (!code) return '';
  
  // 先頭の0を除去して4桁に正規化
  return code.replace(/^0+/, '');
}