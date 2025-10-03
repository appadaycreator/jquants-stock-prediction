/**
 * ErrorPanelコンポーネントのテスト
 */

import { render, screen, fireEvent } from "@testing-library/react";
import ErrorPanel from "../ErrorPanel";
import { AppError } from "@/lib/fetcher";

describe("ErrorPanel", () => {
  const mockError = new Error("テストエラー");
  const mockOnRetry = jest.fn();
  const mockOnDismiss = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("エラーメッセージを正しく表示する", () => {
    render(
      <ErrorPanel 
        error={mockError} 
        onRetry={mockOnRetry} 
        onDismiss={mockOnDismiss} 
      />,
    );
    
    expect(screen.getByText("エラー: テストエラー")).toBeInTheDocument();
  });

  it("リトライボタンをクリックした時にonRetryを呼び出す", () => {
    render(
      <ErrorPanel 
        error={mockError} 
        onRetry={mockOnRetry} 
        onDismiss={mockOnDismiss} 
      />,
    );
    
    const retryButton = screen.getByRole("button", { name: /再試行/i });
    fireEvent.click(retryButton);
    
    expect(mockOnRetry).toHaveBeenCalledTimes(1);
  });

  it("閉じるボタンをクリックした時にonDismissを呼び出す", () => {
    render(
      <ErrorPanel 
        error={mockError} 
        onRetry={mockOnRetry} 
        onDismiss={mockOnDismiss} 
      />,
    );
    
    const dismissButton = screen.getByRole("button", { name: /閉じる/i });
    fireEvent.click(dismissButton);
    
    expect(mockOnDismiss).toHaveBeenCalledTimes(1);
  });

  it("AppErrorのHTTP_404エラーを正しく表示する", () => {
    const appError = new AppError("HTTP_404", "Not Found");
    render(
      <ErrorPanel 
        error={appError} 
        onRetry={mockOnRetry} 
        onDismiss={mockOnDismiss} 
      />,
    );
    
    expect(screen.getByText("エラー: HTTP_404")).toBeInTheDocument();
  });

  it("AppErrorのTIMEOUTエラーを正しく表示する", () => {
    const appError = new AppError("TIMEOUT", "Request timeout");
    render(
      <ErrorPanel 
        error={appError} 
        onRetry={mockOnRetry} 
        onDismiss={mockOnDismiss} 
      />,
    );
    
    expect(screen.getByText("エラー: TIMEOUT")).toBeInTheDocument();
  });

  it("Failed to fetchエラーを正しく表示する", () => {
    const networkError = new Error("Failed to fetch");
    render(
      <ErrorPanel 
        error={networkError} 
        onRetry={mockOnRetry} 
        onDismiss={mockOnDismiss} 
      />,
    );
    
    expect(screen.getByText("ネットワーク接続に問題があります。インターネット接続を確認してください。")).toBeInTheDocument();
  });

  it("RSC payloadエラーを正しく表示する", () => {
    const rscError = new Error("RSC payload error");
    render(
      <ErrorPanel 
        error={rscError} 
        onRetry={mockOnRetry} 
        onDismiss={mockOnDismiss} 
      />,
    );
    
    expect(screen.getByText("サーバーとの通信に問題があります。しばらく待ってから再試行してください。")).toBeInTheDocument();
  });

  it("リトライボタンが無効化されていない", () => {
    render(
      <ErrorPanel 
        error={mockError} 
        onRetry={mockOnRetry} 
        onDismiss={mockOnDismiss} 
      />,
    );
    
    const retryButton = screen.getByRole("button", { name: /再試行/i });
    expect(retryButton).not.toBeDisabled();
  });

  it("閉じるボタンが無効化されていない", () => {
    render(
      <ErrorPanel 
        error={mockError} 
        onRetry={mockOnRetry} 
        onDismiss={mockOnDismiss} 
      />,
    );
    
    const dismissButton = screen.getByRole("button", { name: /閉じる/i });
    expect(dismissButton).not.toBeDisabled();
  });
});
