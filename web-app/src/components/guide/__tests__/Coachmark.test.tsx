import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import Coachmark from "../Coachmark";

const mockStep = {
  id: "test-step",
  target: "[data-testid=\"target\"]",
  title: "Test Step",
  body: "This is a test step",
  placement: "auto" as const,
};

const mockHandlers = {
  onNext: jest.fn(),
  onPrev: jest.fn(),
  onSkip: jest.fn(),
  onComplete: jest.fn(),
};

describe("Coachmark", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should render step title and body", () => {
    render(
      <Coachmark
        step={mockStep}
        onNext={mockHandlers.onNext}
        onPrev={mockHandlers.onPrev}
        onSkip={mockHandlers.onSkip}
        onComplete={mockHandlers.onComplete}
        isFirst={true}
        isLast={false}
        stepNumber={1}
        totalSteps={2}
      />,
    );

    expect(screen.getByText("Test Step")).toBeInTheDocument();
    expect(screen.getByText("This is a test step")).toBeInTheDocument();
  });

  it("should show progress indicator", () => {
    render(
      <Coachmark
        step={mockStep}
        onNext={mockHandlers.onNext}
        onPrev={mockHandlers.onPrev}
        onSkip={mockHandlers.onSkip}
        onComplete={mockHandlers.onComplete}
        isFirst={true}
        isLast={false}
        stepNumber={1}
        totalSteps={2}
      />,
    );

    expect(screen.getByText("1 / 2")).toBeInTheDocument();
  });

  it("should call onNext when next button is clicked", () => {
    render(
      <Coachmark
        step={mockStep}
        onNext={mockHandlers.onNext}
        onPrev={mockHandlers.onPrev}
        onSkip={mockHandlers.onSkip}
        onComplete={mockHandlers.onComplete}
        isFirst={true}
        isLast={false}
        stepNumber={1}
        totalSteps={2}
      />,
    );

    fireEvent.click(screen.getByText("次へ"));
    expect(mockHandlers.onNext).toHaveBeenCalledTimes(1);
  });

  it("should call onPrev when prev button is clicked", () => {
    render(
      <Coachmark
        step={mockStep}
        onNext={mockHandlers.onNext}
        onPrev={mockHandlers.onPrev}
        onSkip={mockHandlers.onSkip}
        onComplete={mockHandlers.onComplete}
        isFirst={false}
        isLast={false}
        stepNumber={2}
        totalSteps={2}
      />,
    );

    fireEvent.click(screen.getByText("戻る"));
    expect(mockHandlers.onPrev).toHaveBeenCalledTimes(1);
  });

  it("should call onSkip when skip button is clicked", () => {
    render(
      <Coachmark
        step={mockStep}
        onNext={mockHandlers.onNext}
        onPrev={mockHandlers.onPrev}
        onSkip={mockHandlers.onSkip}
        onComplete={mockHandlers.onComplete}
        isFirst={true}
        isLast={false}
        stepNumber={1}
        totalSteps={2}
      />,
    );

    fireEvent.click(screen.getByText("スキップ"));
    expect(mockHandlers.onSkip).toHaveBeenCalledTimes(1);
  });

  it("should call onComplete when complete button is clicked", () => {
    render(
      <Coachmark
        step={mockStep}
        onNext={mockHandlers.onNext}
        onPrev={mockHandlers.onPrev}
        onSkip={mockHandlers.onSkip}
        onComplete={mockHandlers.onComplete}
        isFirst={false}
        isLast={true}
        stepNumber={2}
        totalSteps={2}
      />,
    );

    fireEvent.click(screen.getByText("完了"));
    expect(mockHandlers.onComplete).toHaveBeenCalledTimes(1);
  });

  it("should not show prev button on first step", () => {
    render(
      <Coachmark
        step={mockStep}
        onNext={mockHandlers.onNext}
        onPrev={mockHandlers.onPrev}
        onSkip={mockHandlers.onSkip}
        onComplete={mockHandlers.onComplete}
        isFirst={true}
        isLast={false}
        stepNumber={1}
        totalSteps={2}
      />,
    );

    expect(screen.queryByText("戻る")).not.toBeInTheDocument();
  });

  it("should show complete button on last step", () => {
    render(
      <Coachmark
        step={mockStep}
        onNext={mockHandlers.onNext}
        onPrev={mockHandlers.onPrev}
        onSkip={mockHandlers.onSkip}
        onComplete={mockHandlers.onComplete}
        isFirst={false}
        isLast={true}
        stepNumber={2}
        totalSteps={2}
      />,
    );

    expect(screen.getByText("完了")).toBeInTheDocument();
    expect(screen.queryByText("次へ")).not.toBeInTheDocument();
  });

  it("should have proper ARIA attributes", () => {
    render(
      <Coachmark
        step={mockStep}
        onNext={mockHandlers.onNext}
        onPrev={mockHandlers.onPrev}
        onSkip={mockHandlers.onSkip}
        onComplete={mockHandlers.onComplete}
        isFirst={true}
        isLast={false}
        stepNumber={1}
        totalSteps={2}
      />,
    );

    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-labelledby", "coachmark-title");
    expect(dialog).toHaveAttribute("aria-describedby", "coachmark-description");
  });
});
