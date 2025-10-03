/**
 * 共通の型定義
 * アプリケーション全体で使用される型を統一
 */

// 基本的なAPIレスポンス型
export interface ApiResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
  metadata?: {
    timestamp: string;
    version?: string;
    requestId?: string;
  };
}

// ページネーション型
export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    currentPage: number;
    totalPages: number;
    totalItems: number;
    itemsPerPage: number;
    hasNextPage: boolean;
    hasPrevPage: boolean;
  };
}

// エラー型
export interface AppError extends Error {
  code: string;
  statusCode?: number;
  context?: Record<string, any>;
  timestamp: string;
}

export interface ErrorInfo {
  category: "network" | "api" | "data" | "validation" | "permission" | "unknown";
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  userMessage: string;
  autoRetry: boolean;
  retryDelay: number;
  fallbackAction: "none" | "refresh" | "clear-cache" | "redirect" | "reload";
  timestamp: string;
}

// 株価データ型
export interface StockData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  lastUpdated: string;
  close: number;
  date?: string;
  open?: number;
  high?: number;
  low?: number;
}

// 予測データ型
export interface PredictionData {
  date: string;
  symbol: string;
  y_true: number;
  y_pred: number;
  error?: number;
  confidence?: number;
}

// 技術指標型
export interface TechnicalIndicators {
  sma5: number;
  sma10: number;
  sma25: number;
  sma50: number;
  rsi: number;
  macd: {
    macd: number;
    signal: number;
    histogram: number;
  };
  bollinger: {
    upper: number;
    middle: number;
    lower: number;
  };
}

// 分析結果型
export interface AnalysisResult {
  symbol: string;
  name: string;
  currentPrice: number;
  priceChange: number;
  priceChangePercent: number;
  indicators: TechnicalIndicators;
  recommendation: "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL";
  confidence: number;
  reasons: string[];
  riskLevel: "LOW" | "MEDIUM" | "HIGH";
  targetPrice?: number;
}

// 市場サマリー型
export interface MarketSummary {
  totalSymbols: number;
  analyzedSymbols: number;
  recommendations: {
    STRONG_BUY: number;
    BUY: number;
    HOLD: number;
    SELL: number;
    STRONG_SELL: number;
  };
  topGainers: AnalysisResult[];
  topLosers: AnalysisResult[];
  lastUpdated: string;
}

// 設定型
export interface UserSettings {
  theme: "light" | "dark" | "system";
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  analysis: {
    autoRefresh: boolean;
    refreshInterval: number;
    riskTolerance: "low" | "medium" | "high";
  };
  display: {
    currency: string;
    dateFormat: string;
    numberFormat: string;
  };
}

// パフォーマンス型
export interface PerformanceMetrics {
  renderTime: number;
  memoryUsage: number;
  networkLatency: number;
  errorRate: number;
  timestamp: string;
}

// ログ型
export interface LogEntry {
  level: "debug" | "info" | "warn" | "error";
  message: string;
  timestamp: string;
  context?: Record<string, any>;
  stack?: string;
}

// キャッシュ型
export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
  key: string;
}

// 検索型
export interface SearchResult<T> {
  items: T[];
  totalCount: number;
  query: string;
  filters?: Record<string, any>;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

// 通知型
export interface Notification {
  id: string;
  type: "info" | "success" | "warning" | "error";
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actions?: Array<{
    label: string;
    action: () => void;
  }>;
}

// フォーム型
export interface FormField<T = any> {
  name: keyof T;
  label: string;
  type: "text" | "number" | "email" | "password" | "select" | "checkbox" | "radio";
  required: boolean;
  placeholder?: string;
  options?: Array<{ label: string; value: any }>;
  validation?: {
    min?: number;
    max?: number;
    pattern?: RegExp;
    custom?: (value: any) => string | null;
  };
}

// モーダル型
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: "sm" | "md" | "lg" | "xl";
  closable?: boolean;
  children: React.ReactNode;
}

// テーブル型
export interface TableColumn<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string;
  align?: "left" | "center" | "right";
}

export interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  pagination?: {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
  };
  sorting?: {
    sortBy: keyof T;
    sortOrder: "asc" | "desc";
    onSort: (key: keyof T) => void;
  };
  selection?: {
    selectedRows: T[];
    onSelectionChange: (rows: T[]) => void;
  };
}

// チャート型
export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
    fill?: boolean;
  }>;
}

export interface ChartConfig {
  type: "line" | "bar" | "pie" | "doughnut" | "scatter";
  data: ChartData;
  options?: Record<string, any>;
  responsive?: boolean;
  maintainAspectRatio?: boolean;
}

// フィルター型
export interface FilterOption {
  label: string;
  value: any;
  count?: number;
}

export interface FilterConfig {
  key: string;
  label: string;
  type: "select" | "multiselect" | "range" | "date" | "text";
  options?: FilterOption[];
  placeholder?: string;
  multiple?: boolean;
}

// エクスポート型
export interface ExportConfig {
  format: "csv" | "xlsx" | "json" | "pdf";
  filename: string;
  data: any[];
  columns?: string[];
  includeHeaders?: boolean;
}

// インポート型
export interface ImportConfig {
  format: "csv" | "xlsx" | "json";
  file: File;
  mapping?: Record<string, string>;
  validation?: (data: any[]) => string[];
}

// バックアップ型
export interface BackupConfig {
  includeSettings: boolean;
  includeData: boolean;
  includeCache: boolean;
  compression: boolean;
}

export interface BackupData {
  settings: UserSettings;
  data: any;
  cache: Record<string, any>;
  timestamp: string;
  version: string;
}

// 同期型
export interface SyncConfig {
  autoSync: boolean;
  syncInterval: number;
  conflictResolution: "local" | "remote" | "manual";
  includeSettings: boolean;
  includeData: boolean;
}

export interface SyncStatus {
  isSyncing: boolean;
  lastSync: string | null;
  nextSync: string | null;
  conflicts: Array<{
    key: string;
    local: any;
    remote: any;
    resolution: "local" | "remote" | "manual";
  }>;
}

// セキュリティ型
export interface SecurityConfig {
  sessionTimeout: number;
  maxLoginAttempts: number;
  passwordPolicy: {
    minLength: number;
    requireUppercase: boolean;
    requireLowercase: boolean;
    requireNumbers: boolean;
    requireSymbols: boolean;
  };
  twoFactorAuth: boolean;
  encryption: boolean;
}

// 監査型
export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  resource: string;
  timestamp: string;
  ipAddress: string;
  userAgent: string;
  details: Record<string, any>;
  result: "success" | "failure";
}

// ヘルスチェック型
export interface HealthCheck {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  services: Array<{
    name: string;
    status: "up" | "down" | "degraded";
    responseTime: number;
    lastCheck: string;
  }>;
  metrics: {
    cpu: number;
    memory: number;
    disk: number;
    network: number;
  };
}
