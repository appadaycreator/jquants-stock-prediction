import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Checklist, { ChecklistBadge, DEFAULT_CHECKLIST_ITEMS } from '../Checklist';

const mockItems = [
  {
    id: 'item1',
    title: 'Test Item 1',
    description: 'Test description 1',
    completed: false
  },
  {
    id: 'item2',
    title: 'Test Item 2',
    description: 'Test description 2',
    completed: true
  }
];

const mockHandlers = {
  onItemComplete: jest.fn(),
  onItemReset: jest.fn(),
  onComplete: jest.fn()
};

describe('Checklist', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render checklist items', () => {
    render(
      <Checklist
        items={mockItems}
        onItemComplete={mockHandlers.onItemComplete}
        onItemReset={mockHandlers.onItemReset}
        onComplete={mockHandlers.onComplete}
      />
    );

    expect(screen.getByText('Test Item 1')).toBeInTheDocument();
    expect(screen.getByText('Test Item 2')).toBeInTheDocument();
    expect(screen.getByText('Test description 1')).toBeInTheDocument();
    expect(screen.getByText('Test description 2')).toBeInTheDocument();
  });

  it('should show progress indicator', () => {
    render(
      <Checklist
        items={mockItems}
        onItemComplete={mockHandlers.onItemComplete}
        onItemReset={mockHandlers.onItemReset}
        onComplete={mockHandlers.onComplete}
      />
    );

    expect(screen.getByText('1 / 2')).toBeInTheDocument();
  });

  it('should call onItemComplete when incomplete item is clicked', () => {
    render(
      <Checklist
        items={mockItems}
        onItemComplete={mockHandlers.onItemComplete}
        onItemReset={mockHandlers.onItemReset}
        onComplete={mockHandlers.onComplete}
      />
    );

    fireEvent.click(screen.getByText('Test Item 1'));
    expect(mockHandlers.onItemComplete).toHaveBeenCalledWith('item1');
  });

  it('should call onItemReset when completed item is clicked', () => {
    render(
      <Checklist
        items={mockItems}
        onItemComplete={mockHandlers.onItemComplete}
        onItemReset={mockHandlers.onItemReset}
        onComplete={mockHandlers.onComplete}
      />
    );

    fireEvent.click(screen.getByText('Test Item 2'));
    expect(mockHandlers.onItemReset).toHaveBeenCalledWith('item2');
  });

  it('should show completion message when all items are completed', async () => {
    const completedItems = mockItems.map(item => ({ ...item, completed: true }));
    
    render(
      <Checklist
        items={completedItems}
        onItemComplete={mockHandlers.onItemComplete}
        onItemReset={mockHandlers.onItemReset}
        onComplete={mockHandlers.onComplete}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('お疲れ様でした！')).toBeInTheDocument();
    });

    // 自動でonCompleteが呼ばれることを確認
    await waitFor(() => {
      expect(mockHandlers.onComplete).toHaveBeenCalled();
    }, { timeout: 3000 });
  });

  it('should handle keyboard navigation', () => {
    render(
      <Checklist
        items={mockItems}
        onItemComplete={mockHandlers.onItemComplete}
        onItemReset={mockHandlers.onItemReset}
        onComplete={mockHandlers.onComplete}
      />
    );

    const item1 = screen.getByText('Test Item 1').closest('div');
    fireEvent.keyDown(item1!, { key: 'Enter' });
    expect(mockHandlers.onItemComplete).toHaveBeenCalledWith('item1');

    fireEvent.keyDown(item1!, { key: ' ' });
    expect(mockHandlers.onItemComplete).toHaveBeenCalledTimes(2);
  });

  it('should have proper ARIA attributes', () => {
    render(
      <Checklist
        items={mockItems}
        onItemComplete={mockHandlers.onItemComplete}
        onItemReset={mockHandlers.onItemReset}
        onComplete={mockHandlers.onComplete}
      />
    );

    const list = screen.getByRole('list');
    expect(list).toHaveAttribute('aria-label', '初回チェックリスト');

    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveAttribute('aria-checked', 'false');
    expect(items[1]).toHaveAttribute('aria-checked', 'true');
  });
});

describe('ChecklistBadge', () => {
  it('should render progress badge', () => {
    render(
      <ChecklistBadge
        completedCount={1}
        totalCount={3}
        onClick={jest.fn()}
      />
    );

    expect(screen.getByText('1/3')).toBeInTheDocument();
  });

  it('should call onClick when clicked', () => {
    const mockOnClick = jest.fn();
    render(
      <ChecklistBadge
        completedCount={1}
        totalCount={3}
        onClick={mockOnClick}
      />
    );

    fireEvent.click(screen.getByRole('button'));
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('should have proper ARIA label', () => {
    render(
      <ChecklistBadge
        completedCount={1}
        totalCount={3}
        onClick={jest.fn()}
      />
    );

    expect(screen.getByLabelText('チェックリスト: 1/3 完了')).toBeInTheDocument();
  });
});

describe('DEFAULT_CHECKLIST_ITEMS', () => {
  it('should have correct structure', () => {
    expect(DEFAULT_CHECKLIST_ITEMS).toHaveLength(4);
    expect(DEFAULT_CHECKLIST_ITEMS[0]).toHaveProperty('id');
    expect(DEFAULT_CHECKLIST_ITEMS[0]).toHaveProperty('title');
    expect(DEFAULT_CHECKLIST_ITEMS[0]).toHaveProperty('description');
    expect(DEFAULT_CHECKLIST_ITEMS[0]).toHaveProperty('completed');
  });
});
