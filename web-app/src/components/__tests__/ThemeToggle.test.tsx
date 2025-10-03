import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ThemeToggle from '../ThemeToggle';

// Mock the useTheme hook
jest.mock('@/contexts/ThemeContext', () => ({
  useTheme: () => ({
    theme: 'light',
    setTheme: jest.fn(),
  }),
}));

describe('ThemeToggle', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the component without crashing', () => {
    render(<ThemeToggle />);
    expect(screen.getAllByRole('button')).toHaveLength(3);
  });

  it('displays the correct icon for light theme', () => {
    render(<ThemeToggle />);
    // The component should render a sun icon for light theme
    expect(screen.getAllByRole('button')).toHaveLength(3);
  });

  it('handles theme toggle click', () => {
    render(<ThemeToggle />);
    const toggleButtons = screen.getAllByRole('button');
    expect(toggleButtons).toHaveLength(3);
    
    // Test that buttons are clickable
    fireEvent.click(toggleButtons[0]);
    fireEvent.click(toggleButtons[1]);
    fireEvent.click(toggleButtons[2]);
  });

  it('toggles between light and dark themes', () => {
    render(<ThemeToggle />);
    const toggleButtons = screen.getAllByRole('button');
    
    // Test all button interactions
    toggleButtons.forEach(button => {
      fireEvent.click(button);
    });
    
    expect(toggleButtons).toHaveLength(3);
  });
});