import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const memo = await request.json();
    
    // メモの保存（IndexedDBを使用）
    const saved = await saveMemoToIndexedDB(memo);
    
    if (saved) {
      return NextResponse.json({
        success: true,
        message: 'メモが保存されました',
        memo
      });
    } else {
      throw new Error('メモの保存に失敗しました');
    }
  } catch (error) {
    console.error('メモ保存エラー:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'メモの保存に失敗しました',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const stockCode = searchParams.get('stockCode');
    
    const memos = await getMemosFromIndexedDB(stockCode);
    
    return NextResponse.json({
      success: true,
      memos,
      count: memos.length
    });
  } catch (error) {
    console.error('メモ取得エラー:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'メモの取得に失敗しました',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

async function saveMemoToIndexedDB(memo: any): Promise<boolean> {
  try {
    // 実際の実装ではIndexedDBを使用
    // ここではlocalStorageを使用したシミュレーション
    const existingMemos = JSON.parse(localStorage.getItem('routine_memos') || '[]');
    existingMemos.push(memo);
    localStorage.setItem('routine_memos', JSON.stringify(existingMemos));
    
    return true;
  } catch (error) {
    console.error('IndexedDB保存エラー:', error);
    return false;
  }
}

async function getMemosFromIndexedDB(stockCode?: string | null): Promise<any[]> {
  try {
    // 実際の実装ではIndexedDBを使用
    // ここではlocalStorageを使用したシミュレーション
    const memos = JSON.parse(localStorage.getItem('routine_memos') || '[]');
    
    if (stockCode) {
      return memos.filter((memo: any) => memo.stockCode === stockCode);
    }
    
    return memos;
  } catch (error) {
    console.error('IndexedDB取得エラー:', error);
    return [];
  }
}
