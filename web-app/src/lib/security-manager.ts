/**
 * セキュリティ管理システム
 * 個人投資データの保護とセキュリティ強化
 */

interface SecurityConfig {
  enableEncryption: boolean;
  enableCSP: boolean;
  enableHSTS: boolean;
  enableXSSProtection: boolean;
  enableCSRFProtection: boolean;
  sessionTimeout: number; // ミリ秒
  maxLoginAttempts: number;
  passwordMinLength: number;
  enableAuditLog: boolean;
}

interface SecurityHeaders {
  'Content-Security-Policy': string;
  'X-Frame-Options': string;
  'X-Content-Type-Options': string;
  'X-XSS-Protection': string;
  'Strict-Transport-Security': string;
  'Referrer-Policy': string;
}

interface AuditLog {
  timestamp: string;
  event: string;
  user?: string;
  ip?: string;
  details: Record<string, any>;
}

class SecurityManager {
  private config: SecurityConfig;
  private auditLogs: AuditLog[] = [];
  private loginAttempts: Map<string, { count: number; lastAttempt: number }> = new Map();
  private sessionTokens: Map<string, { userId: string; expires: number }> = new Map();

  constructor(config: Partial<SecurityConfig> = {}) {
    this.config = {
      enableEncryption: true,
      enableCSP: true,
      enableHSTS: true,
      enableXSSProtection: true,
      enableCSRFProtection: true,
      sessionTimeout: 30 * 60 * 1000, // 30分
      maxLoginAttempts: 5,
      passwordMinLength: 8,
      enableAuditLog: true,
      ...config
    };

    this.initializeSecurity();
  }

  /**
   * セキュリティの初期化
   */
  private initializeSecurity(): void {
    if (typeof window === 'undefined') return;

    this.setSecurityHeaders();
    this.initializeCSP();
    this.initializeSessionManagement();
    this.initializeAuditLogging();
  }

  /**
   * セキュリティヘッダーの設定
   */
  private setSecurityHeaders(): void {
    if (typeof window === 'undefined') return;

    const headers: SecurityHeaders = {
      'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https:; font-src 'self' data:;",
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff',
      'X-XSS-Protection': '1; mode=block',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
      'Referrer-Policy': 'strict-origin-when-cross-origin'
    };

    // メタタグとして設定
    Object.entries(headers).forEach(([name, value]) => {
      const meta = document.createElement('meta');
      meta.setAttribute('http-equiv', name);
      meta.setAttribute('content', value);
      document.head.appendChild(meta);
    });
  }

  /**
   * CSPの初期化
   */
  private initializeCSP(): void {
    if (!this.config.enableCSP || typeof window === 'undefined') return;

    // インラインスクリプトの制限
    const script = document.createElement('script');
    script.textContent = `
      // CSP違反の監視
      document.addEventListener('securitypolicyviolation', (e) => {
        console.warn('CSP違反:', e.violatedDirective, e.blockedURI);
        this.logSecurityEvent('csp_violation', {
          directive: e.violatedDirective,
          blockedURI: e.blockedURI,
          sourceFile: e.sourceFile
        });
      });
    `;
    document.head.appendChild(script);
  }

  /**
   * セッション管理の初期化
   */
  private initializeSessionManagement(): void {
    if (typeof window === 'undefined') return;

    // セッションタイムアウトの監視
    let lastActivity = Date.now();
    
    const resetActivity = () => {
      lastActivity = Date.now();
    };

    // ユーザーアクティビティの監視
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
      document.addEventListener(event, resetActivity, true);
    });

    // セッションタイムアウトのチェック
    setInterval(() => {
      if (Date.now() - lastActivity > this.config.sessionTimeout) {
        this.handleSessionTimeout();
      }
    }, 60000); // 1分ごとにチェック
  }

  /**
   * セッションタイムアウトの処理
   */
  private handleSessionTimeout(): void {
    this.logSecurityEvent('session_timeout', {});
    
    // セッションのクリア
    this.clearSession();
    
    // ログアウト処理
    this.logout();
  }

  /**
   * 監査ログの初期化
   */
  private initializeAuditLogging(): void {
    if (!this.config.enableAuditLog) return;

    // セキュリティイベントの監視
    this.logSecurityEvent('security_initialized', {
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    });
  }

  /**
   * パスワードの検証
   */
  validatePassword(password: string): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (password.length < this.config.passwordMinLength) {
      errors.push(`パスワードは${this.config.passwordMinLength}文字以上である必要があります`);
    }

    if (!/[A-Z]/.test(password)) {
      errors.push('大文字を含む必要があります');
    }

    if (!/[a-z]/.test(password)) {
      errors.push('小文字を含む必要があります');
    }

    if (!/[0-9]/.test(password)) {
      errors.push('数字を含む必要があります');
    }

    if (!/[^A-Za-z0-9]/.test(password)) {
      errors.push('特殊文字を含む必要があります');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * ログイン試行の監視
   */
  checkLoginAttempts(identifier: string): { allowed: boolean; remaining: number } {
    const attempts = this.loginAttempts.get(identifier);
    const now = Date.now();

    if (!attempts) {
      this.loginAttempts.set(identifier, { count: 1, lastAttempt: now });
      return { allowed: true, remaining: this.config.maxLoginAttempts - 1 };
    }

    // 時間経過によるリセット
    if (now - attempts.lastAttempt > 15 * 60 * 1000) { // 15分
      this.loginAttempts.set(identifier, { count: 1, lastAttempt: now });
      return { allowed: true, remaining: this.config.maxLoginAttempts - 1 };
    }

    if (attempts.count >= this.config.maxLoginAttempts) {
      this.logSecurityEvent('login_blocked', { identifier, attempts: attempts.count });
      return { allowed: false, remaining: 0 };
    }

    attempts.count++;
    attempts.lastAttempt = now;
    this.loginAttempts.set(identifier, attempts);

    return { 
      allowed: true, 
      remaining: this.config.maxLoginAttempts - attempts.count 
    };
  }

  /**
   * セッションの作成
   */
  createSession(userId: string): string {
    const token = this.generateSecureToken();
    const expires = Date.now() + this.config.sessionTimeout;
    
    this.sessionTokens.set(token, { userId, expires });
    
    this.logSecurityEvent('session_created', { userId, token });
    
    return token;
  }

  /**
   * セッションの検証
   */
  validateSession(token: string): { valid: boolean; userId?: string } {
    const session = this.sessionTokens.get(token);
    
    if (!session) {
      this.logSecurityEvent('invalid_session', { token });
      return { valid: false };
    }

    if (Date.now() > session.expires) {
      this.sessionTokens.delete(token);
      this.logSecurityEvent('session_expired', { token, userId: session.userId });
      return { valid: false };
    }

    return { valid: true, userId: session.userId };
  }

  /**
   * セッションのクリア
   */
  clearSession(): void {
    this.sessionTokens.clear();
    this.logSecurityEvent('session_cleared', {});
  }

  /**
   * ログアウト
   */
  logout(): void {
    this.clearSession();
    
    // ローカルストレージのクリア
    if (typeof window !== 'undefined') {
      localStorage.clear();
      sessionStorage.clear();
    }

    this.logSecurityEvent('logout', {});
  }

  /**
   * セキュアトークンの生成
   */
  private generateSecureToken(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  /**
   * データの暗号化
   */
  async encryptData(data: string, key: string): Promise<string> {
    if (!this.config.enableEncryption) return data;

    try {
      const encoder = new TextEncoder();
      const dataBuffer = encoder.encode(data);
      const keyBuffer = encoder.encode(key);

      const cryptoKey = await crypto.subtle.importKey(
        'raw',
        keyBuffer,
        { name: 'AES-GCM' },
        false,
        ['encrypt']
      );

      const iv = crypto.getRandomValues(new Uint8Array(12));
      const encrypted = await crypto.subtle.encrypt(
        { name: 'AES-GCM', iv },
        cryptoKey,
        dataBuffer
      );

      const result = new Uint8Array(iv.length + encrypted.byteLength);
      result.set(iv);
      result.set(new Uint8Array(encrypted), iv.length);

      return btoa(String.fromCharCode(...result));
    } catch (error) {
      console.error('暗号化エラー:', error);
      throw error;
    }
  }

  /**
   * データの復号化
   */
  async decryptData(encryptedData: string, key: string): Promise<string> {
    if (!this.config.enableEncryption) return encryptedData;

    try {
      const decoder = new TextDecoder();
      const keyBuffer = new TextEncoder().encode(key);

      const cryptoKey = await crypto.subtle.importKey(
        'raw',
        keyBuffer,
        { name: 'AES-GCM' },
        false,
        ['decrypt']
      );

      const data = Uint8Array.from(atob(encryptedData), c => c.charCodeAt(0));
      const iv = data.slice(0, 12);
      const encrypted = data.slice(12);

      const decrypted = await crypto.subtle.decrypt(
        { name: 'AES-GCM', iv },
        cryptoKey,
        encrypted
      );

      return decoder.decode(decrypted);
    } catch (error) {
      console.error('復号化エラー:', error);
      throw error;
    }
  }

  /**
   * セキュリティイベントのログ記録
   */
  logSecurityEvent(event: string, details: Record<string, any>): void {
    if (!this.config.enableAuditLog) return;

    const log: AuditLog = {
      timestamp: new Date().toISOString(),
      event,
      details,
      ip: this.getClientIP(),
      user: this.getCurrentUser()
    };

    this.auditLogs.push(log);

    // ログの保存（実際の実装ではサーバーに送信）
    console.log('セキュリティイベント:', log);
  }

  /**
   * クライアントIPの取得
   */
  private getClientIP(): string {
    // 実際の実装ではサーバーから取得
    return 'unknown';
  }

  /**
   * 現在のユーザーの取得
   */
  private getCurrentUser(): string {
    // 実際の実装では認証システムから取得
    return 'anonymous';
  }

  /**
   * 監査ログの取得
   */
  getAuditLogs(): AuditLog[] {
    return [...this.auditLogs];
  }

  /**
   * セキュリティ設定の更新
   */
  updateConfig(newConfig: Partial<SecurityConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * 現在の設定の取得
   */
  getConfig(): SecurityConfig {
    return { ...this.config };
  }
}

// シングルトンインスタンス
export const securityManager = new SecurityManager();

export default SecurityManager;
