import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { ThemeToggle } from "../ThemeToggle";

// ThemeContext のモック
const mockThemeContext = {
  theme: "light",
  setTheme: jest.fn(),
  toggleTheme: jest.fn(),
};

jest.mock("../../contexts/ThemeContext", () => ({
  useTheme: () => mockThemeContext,
}));

describe("ThemeToggle", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the theme toggle button", () => {
    render(<ThemeToggle />);
    
    const toggleButton = screen.getByRole("button");
    expect(toggleButton).toBeInTheDocument();
  });

  it("displays current theme", () => {
    render(<ThemeToggle />);
    
    expect(screen.getByText("ライト")).toBeInTheDocument();
  });

  it("calls toggleTheme when clicked", () => {
    render(<ThemeToggle />);
    
    const toggleButton = screen.getByRole("button");
    fireEvent.click(toggleButton);
    
    expect(mockThemeContext.toggleTheme).toHaveBeenCalledTimes(1);
  });

  it("shows dark theme when theme is dark", () => {
    mockThemeContext.theme = "dark";
    
    render(<ThemeToggle />);
    
    expect(screen.getByText("ダーク")).toBeInTheDocument();
  });
});