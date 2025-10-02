/**
 * テキスト内の検索キーワードをハイライトするユーティリティ
 */

/**
 * テキスト内のキーワードをハイライトする
 * @param text ハイライトするテキスト
 * @param query 検索クエリ
 * @param className ハイライト用のCSSクラス名
 * @returns ハイライトされたHTML文字列
 */
export function highlightText(
  text: string, 
  query: string, 
  className: string = "bg-yellow-200 text-yellow-900 px-1 rounded",
): string {
  if (!query.trim() || !text) return text;
  
  // クエリを単語に分割し、特殊文字をエスケープ
  const keywords = query
    .split(/\s+/)
    .filter(keyword => keyword.length > 0)
    .map(keyword => keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  
  if (keywords.length === 0) return text;
  
  // 正規表現を作成（大文字小文字を区別しない）
  const regex = new RegExp(`(${keywords.join("|")})`, "gi");
  
  return text.replace(regex, `<span class="${className}">$1</span>`);
}

/**
 * 複数のフィールドからキーワードをハイライトする
 * @param fields ハイライトするフィールドの配列
 * @param query 検索クエリ
 * @param className ハイライト用のCSSクラス名
 * @returns ハイライトされたフィールドの配列
 */
export function highlightFields(
  fields: string[], 
  query: string, 
  className: string = "bg-yellow-200 text-yellow-900 px-1 rounded",
): string[] {
  return fields.map(field => highlightText(field, query, className));
}

/**
 * 検索結果のスニペットを生成（前後の文脈を含む）
 * @param text 元のテキスト
 * @param query 検索クエリ
 * @param maxLength 最大文字数
 * @param className ハイライト用のCSSクラス名
 * @returns ハイライトされたスニペット
 */
export function createSnippet(
  text: string, 
  query: string, 
  maxLength: number = 150,
  className: string = "bg-yellow-200 text-yellow-900 px-1 rounded",
): string {
  if (!query.trim() || !text) return text;
  
  const keywords = query.toLowerCase().split(/\s+/).filter(k => k.length > 0);
  const textLower = text.toLowerCase();
  
  // 最初にマッチするキーワードの位置を見つける
  let matchIndex = -1;
  for (const keyword of keywords) {
    const index = textLower.indexOf(keyword);
    if (index !== -1) {
      matchIndex = index;
      break;
    }
  }
  
  if (matchIndex === -1) {
    // マッチしない場合は先頭から切り取る
    return text.length > maxLength 
      ? text.substring(0, maxLength) + "..."
      : text;
  }
  
  // マッチ位置を中心に前後の文脈を含める
  const start = Math.max(0, matchIndex - Math.floor(maxLength / 2));
  const end = Math.min(text.length, start + maxLength);
  
  let snippet = text.substring(start, end);
  
  // 前後に省略記号を追加
  if (start > 0) snippet = "..." + snippet;
  if (end < text.length) snippet = snippet + "...";
  
  // ハイライトを適用
  return highlightText(snippet, query, className);
}

/**
 * 検索結果のタイトルとコンテンツをハイライトする
 * @param title タイトル
 * @param content コンテンツ
 * @param query 検索クエリ
 * @param showSnippet スニペット表示するかどうか
 * @returns ハイライトされたオブジェクト
 */
export function highlightSearchResult(
  title: string,
  content: string,
  query: string,
  showSnippet: boolean = true,
): {
  highlightedTitle: string;
  highlightedContent: string;
} {
  const highlightedTitle = highlightText(title, query);
  
  const highlightedContent = showSnippet 
    ? createSnippet(content, query)
    : highlightText(content, query);
  
  return {
    highlightedTitle,
    highlightedContent,
  };
}

/**
 * 検索クエリを正規化（重複除去、空白整理）
 * @param query 元のクエリ
 * @returns 正規化されたクエリ
 */
export function normalizeQuery(query: string): string {
  return query
    .trim()
    .split(/\s+/)
    .filter(word => word.length > 0)
    .join(" ");
}

/**
 * 検索クエリが有効かどうかチェック
 * @param query 検索クエリ
 * @returns 有効かどうか
 */
export function isValidQuery(query: string): boolean {
  const normalized = normalizeQuery(query);
  return normalized.length >= 2;
}
