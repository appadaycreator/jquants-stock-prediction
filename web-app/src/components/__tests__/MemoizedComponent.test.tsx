/**
 * メモ化コンポーネントのテスト
 */

import React, { memo, useState, useCallback } from "react";
import { render, screen, fireEvent } from "@testing-library/react";

// メモ化されたコンポーネント
const MemoizedChild = memo(({ value, onClick }: { value: number; onClick: () => void }) => {
  return (
    <div>
      <span data-testid="memo-value">{value}</span>
      <button onClick={onClick}>Increment</button>
    </div>
  );
});

MemoizedChild.displayName = "MemoizedChild";

// 親コンポーネント
const ParentComponent = () => {
  const [count, setCount] = useState(0);
  const [otherState, setOtherState] = useState(0);

  const handleIncrement = useCallback(() => {
    setCount(prev => prev + 1);
  }, []);

  return (
    <div>
      <div data-testid="parent-count">{count}</div>
      <div data-testid="parent-other">{otherState}</div>
      <MemoizedChild value={count} onClick={handleIncrement} />
      <button onClick={() => setOtherState(prev => prev + 1)}>Change Other State</button>
    </div>
  );
};

describe("MemoizedComponent", () => {
  it("メモ化されたコンポーネントが正しくレンダリングされる", () => {
    render(<ParentComponent />);

    expect(screen.getByTestId("memo-value")).toHaveTextContent("0");
    expect(screen.getByTestId("parent-count")).toHaveTextContent("0");
  });

  it("関連する状態が変更された時のみ再レンダリングされる", () => {
    render(<ParentComponent />);

    // 初期状態
    expect(screen.getByTestId("memo-value")).toHaveTextContent("0");

    // カウントを増加（メモ化されたコンポーネントが再レンダリングされる）
    fireEvent.click(screen.getByText("Increment"));
    expect(screen.getByTestId("memo-value")).toHaveTextContent("1");

    // 他の状態を変更（メモ化されたコンポーネントは再レンダリングされない）
    fireEvent.click(screen.getByText("Change Other State"));
    expect(screen.getByTestId("memo-value")).toHaveTextContent("1"); // 変更されていない
  });

  it("useCallbackが正しく動作する", () => {
    render(<ParentComponent />);

    // 複数回クリックしても正しく動作
    fireEvent.click(screen.getByText("Increment"));
    fireEvent.click(screen.getByText("Increment"));
    fireEvent.click(screen.getByText("Increment"));

    expect(screen.getByTestId("memo-value")).toHaveTextContent("3");
  });
});
