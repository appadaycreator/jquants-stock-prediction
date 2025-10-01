/**
 * ErrorBoundaryコンポーネントのテスト
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ErrorBoundary } from "../ErrorBoundary";

// エラーを投げるコンポーネント
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error("Test error");
  }
  return <div>正常なコンテンツ</div>;
};

describe("ErrorBoundary", () => {
  it("正常なコンテンツを表示する", () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("正常なコンテンツ")).toBeInTheDocument();
  });

  it("エラーが発生した場合にフォールバックを表示する", () => {
    // コンソールエラーを抑制
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("予期しないエラーが発生しました")).toBeInTheDocument();
    expect(screen.getByText("再試行")).toBeInTheDocument();
    expect(screen.getByText("ページを再読み込み")).toBeInTheDocument();

    consoleSpy.mockRestore();
  });

  it("カスタムフォールバックを表示する", () => {
    const customFallback = <div>カスタムエラーメッセージ</div>;

    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("カスタムエラーメッセージ")).toBeInTheDocument();
  });

  it("開発モードでエラー詳細を表示する", () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "development";

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(screen.getByText("エラー詳細（開発モード）")).toBeInTheDocument();

    consoleSpy.mockRestore();
    process.env.NODE_ENV = originalEnv;
  });

  it("再試行ボタンが動作する", () => {
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    const retryButton = screen.getByText("再試行");
    expect(retryButton).toBeInTheDocument();

    // 再試行ボタンをクリック
    retryButton.click();

    // エラー状態がリセットされることを確認
    expect(screen.getByText("正常なコンテンツ")).toBeInTheDocument();

    consoleSpy.mockRestore();
  });

  it("onErrorコールバックを呼び出す", () => {
    const onError = vi.fn();
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.any(Object),
    );

    consoleSpy.mockRestore();
  });
});
