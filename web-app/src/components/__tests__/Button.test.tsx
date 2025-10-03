/**
 * Buttonコンポーネントのテスト
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../ui/button';

describe('Button', () => {
  it('正しくレンダリングされる', () => {
    render(<Button>テストボタン</Button>);
    expect(screen.getByRole('button', { name: 'テストボタン' })).toBeInTheDocument();
  });

  it('クリックイベントが正しく動作する', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>クリックテスト</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disabled状態が正しく動作する', () => {
    render(<Button disabled>無効ボタン</Button>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('異なるバリアントが正しく適用される', () => {
    const { rerender } = render(<Button variant="default">デフォルト</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-primary');

    rerender(<Button variant="destructive">破壊的</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-destructive');

    rerender(<Button variant="outline">アウトライン</Button>);
    expect(screen.getByRole('button')).toHaveClass('border');

    rerender(<Button variant="secondary">セカンダリ</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-secondary');

    rerender(<Button variant="ghost">ゴースト</Button>);
    expect(screen.getByRole('button')).toHaveClass('hover:bg-accent');

    rerender(<Button variant="link">リンク</Button>);
    expect(screen.getByRole('button')).toHaveClass('text-primary');
  });

  it('異なるサイズが正しく適用される', () => {
    const { rerender } = render(<Button size="default">デフォルトサイズ</Button>);
    expect(screen.getByRole('button')).toHaveClass('h-10');

    rerender(<Button size="sm">小サイズ</Button>);
    expect(screen.getByRole('button')).toHaveClass('h-9');

    rerender(<Button size="lg">大サイズ</Button>);
    expect(screen.getByRole('button')).toHaveClass('h-11');

    rerender(<Button size="icon">アイコンサイズ</Button>);
    expect(screen.getByRole('button')).toHaveClass('h-10', 'w-10');
  });

  it('カスタムクラスが正しく適用される', () => {
    render(<Button className="custom-class">カスタム</Button>);
    expect(screen.getByRole('button')).toHaveClass('custom-class');
  });

  it('asChildプロパティが正しく動作する', () => {
    render(
      <Button asChild>
        <a href="/test">リンクボタン</a>
      </Button>
    );
    expect(screen.getByRole('link')).toBeInTheDocument();
  });
});