export function getBasePath(): string {
  // Next.js の basePath はビルド時に反映される。クライアントでは PUBLIC 環境変数を使用。
  // 環境変数が無い場合は空文字を返し、ルート相対にフォールバック。
  // 末尾のスラッシュは除去する。
  const raw = process.env.NEXT_PUBLIC_BASE_PATH || "";
  if (!raw) return "";
  return raw.endsWith("/") ? raw.slice(0, -1) : raw;
}

export function resolveStaticPath(path: string): string {
  // 絶対URL(http/https)や data: はそのまま返す
  if (/^(?:https?:)?\/\//i.test(path) || path.startsWith("data:")) return path;
  
  const base = getBasePath();
  if (!base) return path;
  
  // 既に basePath が付いているかチェック
  if (path.startsWith(base)) {
    console.debug(`resolveStaticPath: Path already has basePath: ${path}`);
    return path;
  }
  
  // 先頭スラッシュを必須とし、重複しないよう結合
  const normalized = path.startsWith("/") ? path : `/${path}`;
  const resolved = `${base}${normalized}`;
  
  console.debug(`resolveStaticPath: ${path} -> ${resolved} (base: ${base})`);
  return resolved;
}

export function resolveApiPath(path: string): string {
  // API 風のパスも静的サイトでは静的 JSON を参照するため同様に解決
  return resolveStaticPath(path);
}

