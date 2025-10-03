/**
 * ThemeToggleコンポーネントのテスト
 */

import { render, screen, fireEvent } from "@testing-library/react";
import ThemeToggle from "../ThemeToggle";

// ThemeContextのモック
const mockSetTheme = jest.fn();
jest.mock("../../contexts/ThemeContext", () => ({
  useTheme: () => ({
    theme: "light",
    setTheme: mockSetTheme,
  }),
}));

describe("ThemeToggle", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("テーマトグルボタンを正しくレンダリングする", () => {
    render(<ThemeToggle />);
    
    const toggleButtons = screen.getAllByRole("button");
    expect(toggleButtons).toHaveLength(3); // ライト、ダーク、自動の3つのボタン
  });

  it("ライトテーマボタンをクリックした時にsetThemeが呼ばれる", () => {
    render(<ThemeToggle />);
    
    const lightButton = screen.getByTitle("ライトテーマに切り替え");
    fireEvent.click(lightButton);
    
    expect(mockSetTheme).toHaveBeenCalledWith("light");
  });

  it("ダークテーマボタンをクリックした時にsetThemeが呼ばれる", () => {
    render(<ThemeToggle />);
    
    const darkButton = screen.getByTitle("ダークテーマに切り替え");
    fireEvent.click(darkButton);
    
    expect(mockSetTheme).toHaveBeenCalledWith("dark");
  });

  it("自動テーマボタンをクリックした時にsetThemeが呼ばれる", () => {
    render(<ThemeToggle />);
    
    const autoButton = screen.getByTitle("自動テーマに切り替え");
    fireEvent.click(autoButton);
    
    expect(mockSetTheme).toHaveBeenCalledWith("auto");
  });
});
