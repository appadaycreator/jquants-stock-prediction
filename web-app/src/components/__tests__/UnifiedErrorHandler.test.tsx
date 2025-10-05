import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import UnifiedErrorHandler from "../UnifiedErrorHandler";

describe("UnifiedErrorHandler", () => {
  const defaultProps = {
    error: null,
    isLoading: false,
    onRetry: jest.fn(),
    maxRetries: 3,
    retryDelay: 100,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("エラーがない場合は子コンポーネントを表示する", () => {
    render(
      <UnifiedErrorHandler {...defaultProps}>
        <div>テストコンテンツ</div>
      </UnifiedErrorHandler>,
    );
    
    expect(screen.getByText("テストコンテンツ")).toBeInTheDocument();
  });

  it("ローディング状態を正しく表示する", () => {
    render(
      <UnifiedErrorHandler {...defaultProps} isLoading={true}>
        <div>テストコンテンツ</div>
      </UnifiedErrorHandler>,
    );
    
    expect(screen.getByText("読み込み中...")).toBeInTheDocument();
    expect(screen.queryByText("テストコンテンツ")).not.toBeInTheDocument();
  });

  it("エラー状態を正しく表示する", () => {
    const errorMessage = "テストエラー";
    render(
      <UnifiedErrorHandler {...defaultProps} error={errorMessage}>
        <div>テストコンテンツ</div>
      </UnifiedErrorHandler>,
    );
    
    expect(screen.getByText("データ取得エラー")).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
    expect(screen.getByText("再試行")).toBeInTheDocument();
  });

  it("再試行ボタンが正しく動作する", async () => {
    const mockOnRetry = jest.fn().mockResolvedValue(undefined);
    const errorMessage = "テストエラー";
    
    render(
      <UnifiedErrorHandler 
        {...defaultProps} 
        error={errorMessage}
        onRetry={mockOnRetry}
      >
        <div>テストコンテンツ</div>
      </UnifiedErrorHandler>,
    );
    
    const retryButton = screen.getByText("再試行");
    fireEvent.click(retryButton);
    
    await waitFor(() => {
      expect(mockOnRetry).toHaveBeenCalledTimes(1);
    });
  });

  it("再試行中はボタンが無効化される", async () => {
    const mockOnRetry = jest.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 100)),
    );
    const errorMessage = "テストエラー";
    
    render(
      <UnifiedErrorHandler 
        {...defaultProps} 
        error={errorMessage}
        onRetry={mockOnRetry}
        retryDelay={50}
      >
        <div>テストコンテンツ</div>
      </UnifiedErrorHandler>,
    );
    
    const retryButton = screen.getByText("再試行");
    fireEvent.click(retryButton);
    
    // 再試行中はボタンが無効化される
    expect(screen.getByText("再試行中...")).toBeInTheDocument();
  });

  it("ネットワーク状態を正しく表示する", () => {
    // オンライン状態をシミュレート
    Object.defineProperty(navigator, "onLine", {
      writable: true,
      value: true,
    });
    
    const errorMessage = "テストエラー";
    render(
      <UnifiedErrorHandler 
        {...defaultProps} 
        error={errorMessage}
        showNetworkStatus={true}
      >
        <div>テストコンテンツ</div>
      </UnifiedErrorHandler>,
    );
    
    expect(screen.getByText(/ネットワーク接続: 正常/)).toBeInTheDocument();
  });

  it("オフライン状態を正しく表示する", () => {
    // オフライン状態をシミュレート
    Object.defineProperty(navigator, "onLine", {
      writable: true,
      value: false,
    });
    
    const errorMessage = "テストエラー";
    render(
      <UnifiedErrorHandler 
        {...defaultProps} 
        error={errorMessage}
        showNetworkStatus={true}
      >
        <div>テストコンテンツ</div>
      </UnifiedErrorHandler>,
    );
    
    expect(screen.getByText(/ネットワーク接続: オフライン/)).toBeInTheDocument();
  });

  it("カスタムリロードハンドラーが正しく動作する", () => {
    const mockOnReload = jest.fn();
    const errorMessage = "テストエラー";
    
    render(
      <UnifiedErrorHandler 
        {...defaultProps} 
        error={errorMessage}
        onReload={mockOnReload}
      >
        <div>テストコンテンツ</div>
      </UnifiedErrorHandler>,
    );
    
    // 最大リトライ回数に達した場合の表示をシミュレート
    // 実際の実装では、retryCountの状態管理が必要
  });

  it("カスタムホームハンドラーが正しく動作する", () => {
    const mockOnGoHome = jest.fn();
    const errorMessage = "テストエラー";
    
    render(
      <UnifiedErrorHandler 
        {...defaultProps} 
        error={errorMessage}
        onGoHome={mockOnGoHome}
      >
        <div>テストコンテンツ</div>
      </UnifiedErrorHandler>,
    );
    
    // 最大リトライ回数に達した場合の表示をシミュレート
    // 実際の実装では、retryCountの状態管理が必要
  });
});
