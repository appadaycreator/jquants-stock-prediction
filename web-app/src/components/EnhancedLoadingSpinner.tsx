/**
 * 強化されたローディングスピナー
 * プログレス表示、エラーハンドリング、自動リトライ機能を統合
 */

import React, { useState, useEffect } from 'react';
import { Loader2, AlertTriangle, RefreshCw, CheckCircle } from 'lucide-react';

interface LoadingState {
  isLoading: boolean;
  progress: number;
  message: string;
  error?: string;
  canRetry: boolean;
  retryCount: number;
  maxRetries: number;
}

interface EnhancedLoadingSpinnerProps {
  state: LoadingState;
  onRetry?: () => void;
  onCancel?: () => void;
  showProgress?: boolean;
  showRetryButton?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'minimal' | 'overlay';
}

export default function EnhancedLoadingSpinner({
  state,
  onRetry,
  onCancel,
  showProgress = true,
  showRetryButton = true,
  size = 'md',
  variant = 'default',
}: EnhancedLoadingSpinnerProps) {
  const [animationPhase, setAnimationPhase] = useState(0);

  useEffect(() => {
    if (state.isLoading) {
      const interval = setInterval(() => {
        setAnimationPhase(prev => (prev + 1) % 4);
      }, 500);
      return () => clearInterval(interval);
    }
  }, [state.isLoading]);

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const getLoadingMessage = () => {
    if (state.error) {
      return state.error;
    }
    if (state.retryCount > 0) {
      return `${state.message} (再試行 ${state.retryCount}/${state.maxRetries})`;
    }
    return state.message;
  };

  const getAnimationDots = () => {
    const dots = ['.', '..', '...', '....'];
    return dots[animationPhase];
  };

  const renderSpinner = () => {
    if (state.error && !state.isLoading) {
      return (
        <div className="flex items-center justify-center text-red-500">
          <AlertTriangle className={`${sizeClasses[size]} mr-2`} />
        </div>
      );
    }

    if (!state.isLoading && state.progress === 100) {
      return (
        <div className="flex items-center justify-center text-green-500">
          <CheckCircle className={`${sizeClasses[size]} mr-2`} />
        </div>
      );
    }

    return (
      <div className="flex items-center justify-center">
        <Loader2 className={`${sizeClasses[size]} animate-spin`} />
      </div>
    );
  };

  const renderContent = () => {
    if (variant === 'minimal') {
      return (
        <div className="flex items-center space-x-2">
          {renderSpinner()}
          <span className="text-sm text-gray-600">
            {getLoadingMessage()}
            {state.isLoading && getAnimationDots()}
          </span>
        </div>
      );
    }

    if (variant === 'overlay') {
      return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
            <div className="text-center">
              {renderSpinner()}
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                {state.isLoading ? '処理中...' : state.error ? 'エラー' : '完了'}
              </h3>
              <p className="mt-2 text-sm text-gray-600">
                {getLoadingMessage()}
                {state.isLoading && getAnimationDots()}
              </p>
              
              {showProgress && state.isLoading && (
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${state.progress}%` }}
                    />
                  </div>
                  <p className="mt-2 text-xs text-gray-500">
                    {state.progress}% 完了
                  </p>
                </div>
              )}

              <div className="mt-6 flex space-x-3">
                {state.error && showRetryButton && state.canRetry && onRetry && (
                  <button
                    onClick={onRetry}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4 inline mr-2" />
                    再試行
                  </button>
                )}
                {onCancel && (
                  <button
                    onClick={onCancel}
                    className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    キャンセル
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }

    // default variant
    return (
      <div className="flex flex-col items-center justify-center p-6">
        {renderSpinner()}
        
        <div className="mt-4 text-center">
          <h3 className="text-lg font-medium text-gray-900">
            {state.isLoading ? '処理中...' : state.error ? 'エラーが発生しました' : '完了'}
          </h3>
          <p className="mt-2 text-sm text-gray-600">
            {getLoadingMessage()}
            {state.isLoading && getAnimationDots()}
          </p>
        </div>

        {showProgress && state.isLoading && (
          <div className="mt-4 w-full max-w-xs">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${state.progress}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-gray-500 text-center">
              {state.progress}% 完了
            </p>
          </div>
        )}

        {state.error && showRetryButton && state.canRetry && onRetry && (
          <button
            onClick={onRetry}
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            再試行 ({state.retryCount}/{state.maxRetries})
          </button>
        )}
      </div>
    );
  };

  return renderContent();
}

/**
 * ローディング状態管理フック
 */
export function useLoadingState(initialMessage: string = '読み込み中...') {
  const [state, setState] = useState<LoadingState>({
    isLoading: false,
    progress: 0,
    message: initialMessage,
    canRetry: false,
    retryCount: 0,
    maxRetries: 3,
  });

  const startLoading = (message: string = initialMessage) => {
    setState(prev => ({
      ...prev,
      isLoading: true,
      progress: 0,
      message,
      error: undefined,
      canRetry: false,
    }));
  };

  const updateProgress = (progress: number, message?: string) => {
    setState(prev => ({
      ...prev,
      progress: Math.min(100, Math.max(0, progress)),
      message: message || prev.message,
    }));
  };

  const setError = (error: string, canRetry: boolean = true) => {
    setState(prev => ({
      ...prev,
      isLoading: false,
      error,
      canRetry,
    }));
  };

  const setSuccess = (message: string = '完了') => {
    setState(prev => ({
      ...prev,
      isLoading: false,
      progress: 100,
      message,
      error: undefined,
      canRetry: false,
    }));
  };

  const retry = () => {
    setState(prev => ({
      ...prev,
      isLoading: true,
      progress: 0,
      error: undefined,
      retryCount: prev.retryCount + 1,
      canRetry: prev.retryCount < prev.maxRetries,
    }));
  };

  const reset = () => {
    setState({
      isLoading: false,
      progress: 0,
      message: initialMessage,
      canRetry: false,
      retryCount: 0,
      maxRetries: 3,
    });
  };

  return {
    state,
    startLoading,
    updateProgress,
    setError,
    setSuccess,
    retry,
    reset,
  };
}
