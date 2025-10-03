/**
 * Buttonコンポーネントのテスト
 */

import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "../ui/button";

describe("Button", () => {
  it("デフォルトのボタンをレンダリングする", () => {
    render(<Button>テストボタン</Button>);
    const button = screen.getByRole("button", { name: "テストボタン" });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("bg-primary", "text-primary-foreground");
  });

  it("異なるバリアントを正しくレンダリングする", () => {
    render(<Button variant="destructive">削除ボタン</Button>);
    const button = screen.getByRole("button", { name: "削除ボタン" });
    expect(button).toHaveClass("bg-destructive", "text-destructive-foreground");
  });

  it("異なるサイズを正しくレンダリングする", () => {
    render(<Button size="lg">大きなボタン</Button>);
    const button = screen.getByRole("button", { name: "大きなボタン" });
    expect(button).toHaveClass("h-11", "px-8");
  });

  it("クリックイベントを正しく処理する", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>クリックボタン</Button>);
    const button = screen.getByRole("button", { name: "クリックボタン" });
    
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("無効化されたボタンを正しくレンダリングする", () => {
    render(<Button disabled>無効ボタン</Button>);
    const button = screen.getByRole("button", { name: "無効ボタン" });
    expect(button).toBeDisabled();
    expect(button).toHaveClass("disabled:pointer-events-none", "disabled:opacity-50");
  });

  it("カスタムクラス名を適用する", () => {
    render(<Button className="custom-class">カスタムボタン</Button>);
    const button = screen.getByRole("button", { name: "カスタムボタン" });
    expect(button).toHaveClass("custom-class");
  });

  it("すべてのバリアントを正しくレンダリングする", () => {
    const variants = ["default", "destructive", "outline", "secondary", "ghost", "link"] as const;
    
    variants.forEach((variant) => {
      const { unmount } = render(<Button variant={variant}>{variant}ボタン</Button>);
      const button = screen.getByRole("button", { name: `${variant}ボタン` });
      expect(button).toBeInTheDocument();
      unmount();
    });
  });

  it("すべてのサイズを正しくレンダリングする", () => {
    const sizes = ["default", "sm", "lg", "icon"] as const;
    
    sizes.forEach((size) => {
      const { unmount } = render(<Button size={size}>{size}ボタン</Button>);
      const button = screen.getByRole("button", { name: `${size}ボタン` });
      expect(button).toBeInTheDocument();
      unmount();
    });
  });

  it("refを正しく転送する", () => {
    const ref = jest.fn();
    render(<Button ref={ref}>refボタン</Button>);
    expect(ref).toHaveBeenCalled();
  });

  it("追加のpropsを正しく転送する", () => {
    render(<Button data-testid="test-button" aria-label="テストボタン">テスト</Button>);
    const button = screen.getByTestId("test-button");
    expect(button).toHaveAttribute("aria-label", "テストボタン");
  });
});