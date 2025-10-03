/**
 * Buttonコンポーネントのテスト
 */

import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "../ui/button";

describe("Button", () => {
  it("デフォルトのボタンをレンダリングする", () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole("button", { name: "Click me" });
    expect(button).toBeInTheDocument();
  });

  it("クリックイベントを処理する", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    const button = screen.getByRole("button", { name: "Click me" });
    fireEvent.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("disabled状態でレンダリングする", () => {
    render(<Button disabled>Disabled button</Button>);
    const button = screen.getByRole("button", { name: "Disabled button" });
    expect(button).toBeDisabled();
  });

  it("異なるバリアントでレンダリングする", () => {
    render(<Button variant="destructive">Destructive button</Button>);
    const button = screen.getByRole("button", { name: "Destructive button" });
    expect(button).toBeInTheDocument();
  });

  it("異なるサイズでレンダリングする", () => {
    render(<Button size="lg">Large button</Button>);
    const button = screen.getByRole("button", { name: "Large button" });
    expect(button).toBeInTheDocument();
  });

  it("disabled状態でクリックできない", () => {
    const handleClick = jest.fn();
    render(<Button disabled onClick={handleClick}>Disabled button</Button>);
    
    const button = screen.getByRole("button", { name: "Disabled button" });
    fireEvent.click(button);
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  it("アイコンとテキストを表示する", () => {
    render(
      <Button>
        <span>Icon</span>
        Button text
      </Button>
    );
    const button = screen.getByRole("button");
    expect(button).toHaveTextContent("Icon");
    expect(button).toHaveTextContent("Button text");
  });

  it("カスタムクラス名を適用する", () => {
    render(<Button className="custom-class">Custom button</Button>);
    const button = screen.getByRole("button", { name: "Custom button" });
    expect(button).toHaveClass("custom-class");
  });

  it("aria属性を適用する", () => {
    render(
      <Button aria-label="Custom label" aria-describedby="description">
        Button
      </Button>
    );
    const button = screen.getByRole("button");
    expect(button).toHaveAttribute("aria-label", "Custom label");
    expect(button).toHaveAttribute("aria-describedby", "description");
  });
});
