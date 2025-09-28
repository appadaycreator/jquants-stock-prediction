import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { TourProvider, useGuide } from '../TourProvider';

// テスト用のコンポーネント
function TestComponent() {
  const { state, startTour, nextStep, prevStep, skipTour, completeTour } = useGuide();
  
  return (
    <div>
      <div data-testid="tour-status">{state.isActive ? 'active' : 'inactive'}</div>
      <div data-testid="current-step">{state.currentStep || 'none'}</div>
      <button onClick={startTour} data-testid="start-tour">Start Tour</button>
      <button onClick={nextStep} data-testid="next-step">Next</button>
      <button onClick={prevStep} data-testid="prev-step">Prev</button>
      <button onClick={skipTour} data-testid="skip-tour">Skip</button>
      <button onClick={completeTour} data-testid="complete-tour">Complete</button>
    </div>
  );
}

// テスト用のステップ
const testSteps = [
  {
    id: 'step1',
    target: '[data-testid="target1"]',
    title: 'Step 1',
    body: 'This is step 1',
    placement: 'auto' as const,
    page: '/' as const,
    next: 'step2'
  },
  {
    id: 'step2',
    target: '[data-testid="target2"]',
    title: 'Step 2',
    body: 'This is step 2',
    placement: 'auto' as const,
    page: '/' as const
  }
];

describe('TourProvider', () => {
  beforeEach(() => {
    // ローカルストレージをクリア
    localStorage.clear();
  });

  it('should initialize with default state', () => {
    render(
      <TourProvider steps={testSteps}>
        <TestComponent />
      </TourProvider>
    );

    expect(screen.getByTestId('tour-status')).toHaveTextContent('inactive');
    expect(screen.getByTestId('current-step')).toHaveTextContent('none');
  });

  it('should start tour when startTour is called', () => {
    render(
      <TourProvider steps={testSteps}>
        <TestComponent />
      </TourProvider>
    );

    fireEvent.click(screen.getByTestId('start-tour'));

    expect(screen.getByTestId('tour-status')).toHaveTextContent('active');
    expect(screen.getByTestId('current-step')).toHaveTextContent('step1');
  });

  it('should move to next step', () => {
    render(
      <TourProvider steps={testSteps}>
        <TestComponent />
      </TourProvider>
    );

    fireEvent.click(screen.getByTestId('start-tour'));
    fireEvent.click(screen.getByTestId('next-step'));

    expect(screen.getByTestId('current-step')).toHaveTextContent('step2');
  });

  it('should move to previous step', () => {
    render(
      <TourProvider steps={testSteps}>
        <TestComponent />
      </TourProvider>
    );

    fireEvent.click(screen.getByTestId('start-tour'));
    fireEvent.click(screen.getByTestId('next-step'));
    fireEvent.click(screen.getByTestId('prev-step'));

    expect(screen.getByTestId('current-step')).toHaveTextContent('step1');
  });

  it('should skip tour', () => {
    render(
      <TourProvider steps={testSteps}>
        <TestComponent />
      </TourProvider>
    );

    fireEvent.click(screen.getByTestId('start-tour'));
    fireEvent.click(screen.getByTestId('skip-tour'));

    expect(screen.getByTestId('tour-status')).toHaveTextContent('inactive');
    expect(screen.getByTestId('current-step')).toHaveTextContent('none');
  });

  it('should complete tour', () => {
    render(
      <TourProvider steps={testSteps}>
        <TestComponent />
      </TourProvider>
    );

    fireEvent.click(screen.getByTestId('start-tour'));
    fireEvent.click(screen.getByTestId('complete-tour'));

    expect(screen.getByTestId('tour-status')).toHaveTextContent('inactive');
    expect(screen.getByTestId('current-step')).toHaveTextContent('none');
  });

  it('should persist state in localStorage', () => {
    render(
      <TourProvider steps={testSteps}>
        <TestComponent />
      </TourProvider>
    );

    fireEvent.click(screen.getByTestId('start-tour'));
    fireEvent.click(screen.getByTestId('next-step'));

    // 状態がローカルストレージに保存されているかチェック
    expect(localStorage.getItem('guide_current_step')).toBe('step2');
  });

  it('should restore state from localStorage', () => {
    // ローカルストレージに状態を設定
    localStorage.setItem('guide_current_step', 'step2');
    localStorage.setItem('guide_completed_steps', JSON.stringify(['step1']));

    render(
      <TourProvider steps={testSteps}>
        <TestComponent />
      </TourProvider>
    );

    expect(screen.getByTestId('current-step')).toHaveTextContent('step2');
  });
});
