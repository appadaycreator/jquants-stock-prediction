/**
 * セキュリティフック
 * セキュリティ機能の提供と監視
 */

import { useState, useEffect, useCallback } from 'react';
import { securityManager } from '../lib/security-manager';

interface UseSecurityOptions {
  enableMonitoring?: boolean;
  onSecurityEvent?: (event: string, details: any) => void;
  onSessionTimeout?: () => void;
  onLoginBlocked?: (identifier: string) => void;
}

export function useSecurity(options: UseSecurityOptions = {}) {
  const [isSecure, setIsSecure] = useState(true);
  const [sessionValid, setSessionValid] = useState(false);
  const [securityEvents, setSecurityEvents] = useState<any[]>([]);
  const [loginAttempts, setLoginAttempts] = useState<Map<string, number>>(new Map());

  const {
    enableMonitoring = true,
    onSecurityEvent,
    onSessionTimeout,
    onLoginBlocked
  } = options;

  // セキュリティ監視
  useEffect(() => {
    if (!enableMonitoring) return;

    const interval = setInterval(() => {
      // セッションの検証
      const token = localStorage.getItem('session_token');
      if (token) {
        const validation = securityManager.validateSession(token);
        setSessionValid(validation.valid);
        
        if (!validation.valid) {
          onSessionTimeout?.();
        }
      }

      // セキュリティイベントの監視
      const events = securityManager.getAuditLogs();
      setSecurityEvents(events);
    }, 5000); // 5秒ごとにチェック

    return () => clearInterval(interval);
  }, [enableMonitoring, onSessionTimeout]);

  // パスワードの検証
  const validatePassword = useCallback((password: string) => {
    return securityManager.validatePassword(password);
  }, []);

  // ログイン試行のチェック
  const checkLoginAttempts = useCallback((identifier: string) => {
    const result = securityManager.checkLoginAttempts(identifier);
    
    if (!result.allowed) {
      onLoginBlocked?.(identifier);
    }

    setLoginAttempts(prev => {
      const newMap = new Map(prev);
      newMap.set(identifier, result.remaining);
      return newMap;
    });

    return result;
  }, [onLoginBlocked]);

  // セッションの作成
  const createSession = useCallback((userId: string) => {
    const token = securityManager.createSession(userId);
    localStorage.setItem('session_token', token);
    setSessionValid(true);
    
    onSecurityEvent?.('session_created', { userId });
    return token;
  }, [onSecurityEvent]);

  // セッションの検証
  const validateSession = useCallback((token: string) => {
    const result = securityManager.validateSession(token);
    setSessionValid(result.valid);
    return result;
  }, []);

  // ログアウト
  const logout = useCallback(() => {
    securityManager.logout();
    setSessionValid(false);
    localStorage.removeItem('session_token');
    
    onSecurityEvent?.('logout', {});
  }, [onSecurityEvent]);

  // データの暗号化
  const encryptData = useCallback(async (data: string, key: string) => {
    try {
      return await securityManager.encryptData(data, key);
    } catch (error) {
      console.error('暗号化エラー:', error);
      throw error;
    }
  }, []);

  // データの復号化
  const decryptData = useCallback(async (encryptedData: string, key: string) => {
    try {
      return await securityManager.decryptData(encryptedData, key);
    } catch (error) {
      console.error('復号化エラー:', error);
      throw error;
    }
  }, []);

  // セキュリティイベントのログ記録
  const logSecurityEvent = useCallback((event: string, details: any) => {
    securityManager.logSecurityEvent(event, details);
    onSecurityEvent?.(event, details);
  }, [onSecurityEvent]);

  // セキュリティ設定の更新
  const updateSecurityConfig = useCallback((config: any) => {
    securityManager.updateConfig(config);
  }, []);

  // 現在のセキュリティ設定の取得
  const getSecurityConfig = useCallback(() => {
    return securityManager.getConfig();
  }, []);

  // 監査ログの取得
  const getAuditLogs = useCallback(() => {
    return securityManager.getAuditLogs();
  }, []);

  return {
    isSecure,
    sessionValid,
    securityEvents,
    loginAttempts,
    validatePassword,
    checkLoginAttempts,
    createSession,
    validateSession,
    logout,
    encryptData,
    decryptData,
    logSecurityEvent,
    updateSecurityConfig,
    getSecurityConfig,
    getAuditLogs
  };
}
