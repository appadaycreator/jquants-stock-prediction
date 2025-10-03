import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import StockSearchInput from '@/components/StockSearchInput';

// useStockSuggestionsフックをモック
jest.mock('@/hooks/useStockSuggestions', () => ({
  useStockSuggestions: () => ({
    suggestions: [
      {
        code: '7203',
        name: 'トヨタ自動車',
        sector: '自動車',
        market: 'プライム',
        displayText: 'トヨタ自動車 (7203)'
      },
      {
        code: '6758',
        name: 'ソニーグループ',
        sector: '電気機器',
        market: 'プライム',
        displayText: 'ソニーグループ (6758)'
      }
    ],
    isLoading: false,
    error: null,
    showSuggestions: true,
    handleQueryChange: jest.fn(),
    clearSuggestions: jest.fn(),
    hideSuggestions: jest.fn(),
    fetchSuggestions: jest.fn()
  })
}));

describe('StockSearchInput', () => {
  const defaultProps = {
    value: '',
    onChange: jest.fn(),
    placeholder: '銘柄名またはコードを入力...'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('正しくレンダリングされる', () => {
    render(<StockSearchInput {...defaultProps} />);
    
    const input = screen.getByPlaceholderText('銘柄名またはコードを入力...');
    expect(input).toBeInTheDocument();
  });

  it('入力値が正しく表示される', () => {
    render(<StockSearchInput {...defaultProps} value="テスト" />);
    
    const input = screen.getByDisplayValue('テスト');
    expect(input).toBeInTheDocument();
  });

  it('入力値の変更がonChangeに渡される', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();
    
    render(<StockSearchInput {...defaultProps} onChange={onChange} />);
    
    const input = screen.getByPlaceholderText('銘柄名またはコードを入力...');
    await user.type(input, 'テスト');
    
    expect(onChange).toHaveBeenCalledWith('テスト');
  });

  it('フォーカス時にサジェッションが表示される', async () => {
    const user = userEvent.setup();
    render(<StockSearchInput {...defaultProps} value="トヨタ" />);
    
    const input = screen.getByPlaceholderText('銘柄名またはコードを入力...');
    await user.click(input);
    
    await waitFor(() => {
      expect(screen.getByText('トヨタ自動車 (7203)')).toBeInTheDocument();
    });
  });

  it('サジェッションクリックで値が設定される', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();
    
    render(<StockSearchInput {...defaultProps} onChange={onChange} value="トヨタ" />);
    
    const input = screen.getByPlaceholderText('銘柄名またはコードを入力...');
    await user.click(input);
    
    await waitFor(() => {
      const suggestion = screen.getByText('トヨタ自動車 (7203)');
      expect(suggestion).toBeInTheDocument();
    });
    
    const suggestion = screen.getByText('トヨタ自動車 (7203)');
    await user.click(suggestion);
    
    expect(onChange).toHaveBeenCalledWith('トヨタ自動車 (7203)');
  });

  it('キーボードナビゲーションが動作する', async () => {
    const user = userEvent.setup();
    render(<StockSearchInput {...defaultProps} value="トヨタ" />);
    
    const input = screen.getByPlaceholderText('銘柄名またはコードを入力...');
    await user.click(input);
    
    await waitFor(() => {
      expect(screen.getByText('トヨタ自動車 (7203)')).toBeInTheDocument();
    });
    
    // 下矢印キーで最初のサジェッションを選択
    await user.keyboard('{ArrowDown}');
    
    // 選択されたサジェッションがハイライトされることを確認
    const firstSuggestion = screen.getByText('トヨタ自動車 (7203)');
    expect(firstSuggestion).toHaveClass('bg-blue-100');
  });

  it('Enterキーでサジェッションが選択される', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();
    
    render(<StockSearchInput {...defaultProps} onChange={onChange} value="トヨタ" />);
    
    const input = screen.getByPlaceholderText('銘柄名またはコードを入力...');
    await user.click(input);
    
    await waitFor(() => {
      expect(screen.getByText('トヨタ自動車 (7203)')).toBeInTheDocument();
    });
    
    // 下矢印キーでサジェッションを選択
    await user.keyboard('{ArrowDown}');
    
    // Enterキーでサジェッションを選択
    await user.keyboard('{Enter}');
    
    expect(onChange).toHaveBeenCalledWith('トヨタ自動車 (7203)');
  });

  it('Escapeキーでサジェッションが非表示になる', async () => {
    const user = userEvent.setup();
    render(<StockSearchInput {...defaultProps} value="トヨタ" />);
    
    const input = screen.getByPlaceholderText('銘柄名またはコードを入力...');
    await user.click(input);
    
    await waitFor(() => {
      expect(screen.getByText('トヨタ自動車 (7203)')).toBeInTheDocument();
    });
    
    // Escapeキーでサジェッションを非表示
    await user.keyboard('{Escape}');
    
    // サジェッションが非表示になることを確認
    await waitFor(() => {
      expect(screen.queryByText('トヨタ自動車 (7203)')).not.toBeInTheDocument();
    });
  });

  it('クリアボタンが動作する', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();
    
    render(<StockSearchInput {...defaultProps} onChange={onChange} value="テスト" />);
    
    const clearButton = screen.getByLabelText('検索をクリア');
    await user.click(clearButton);
    
    expect(onChange).toHaveBeenCalledWith('');
  });

  it('disabled状態で正しく動作する', () => {
    render(<StockSearchInput {...defaultProps} disabled={true} />);
    
    const input = screen.getByPlaceholderText('銘柄名またはコードを入力...');
    expect(input).toBeDisabled();
  });

  it('カスタムクラス名が適用される', () => {
    render(<StockSearchInput {...defaultProps} className="custom-class" />);
    
    const container = screen.getByPlaceholderText('銘柄名またはコードを入力...').closest('.relative');
    expect(container).toHaveClass('custom-class');
  });

  it('onSearchが呼ばれる', async () => {
    const user = userEvent.setup();
    const onSearch = jest.fn();
    
    render(<StockSearchInput {...defaultProps} onSearch={onSearch} value="テスト" />);
    
    const input = screen.getByPlaceholderText('銘柄名またはコードを入力...');
    await user.keyboard('{Enter}');
    
    expect(onSearch).toHaveBeenCalledWith('テスト');
  });

  it('ローディング状態が表示される', () => {
    // ローディング状態をモック
    jest.doMock('@/hooks/useStockSuggestions', () => ({
      useStockSuggestions: () => ({
        suggestions: [],
        isLoading: true,
        error: null,
        showSuggestions: true,
        handleQueryChange: jest.fn(),
        clearSuggestions: jest.fn(),
        hideSuggestions: jest.fn(),
        fetchSuggestions: jest.fn()
      })
    }));

    render(<StockSearchInput {...defaultProps} value="テスト" />);
    
    expect(screen.getByText('検索中...')).toBeInTheDocument();
  });

  it('エラー状態が表示される', () => {
    // エラー状態をモック
    jest.doMock('@/hooks/useStockSuggestions', () => ({
      useStockSuggestions: () => ({
        suggestions: [],
        isLoading: false,
        error: 'エラーが発生しました',
        showSuggestions: true,
        handleQueryChange: jest.fn(),
        clearSuggestions: jest.fn(),
        hideSuggestions: jest.fn(),
        fetchSuggestions: jest.fn()
      })
    }));

    render(<StockSearchInput {...defaultProps} value="テスト" />);
    
    expect(screen.getByText('エラーが発生しました')).toBeInTheDocument();
  });
});
