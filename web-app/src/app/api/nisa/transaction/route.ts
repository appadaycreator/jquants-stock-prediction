/**
 * 新NISA取引記録管理API
 * POST /api/nisa/transaction - 取引記録追加
 * PUT /api/nisa/transaction - 取引記録更新
 * DELETE /api/nisa/transaction - 取引記録削除
 */

import { NextRequest, NextResponse } from 'next/server';
import { NisaManager } from '@/lib/nisa';
import { NisaTransaction } from '@/lib/nisa/types';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const nisaManager = new NisaManager();
    await nisaManager.initialize();

    const validation = await nisaManager.addTransaction(body);
    
    if (!validation.isValid) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: '取引データの検証に失敗しました',
          details: validation.errors,
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
        },
      }, { status: 400 });
    }

    return NextResponse.json({
      success: true,
      data: {
        message: '取引記録が正常に追加されました',
        warnings: validation.warnings,
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    });

  } catch (error) {
    console.error('取引記録追加エラー:', error);
    return NextResponse.json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'サーバー内部エラーが発生しました',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    }, { status: 500 });
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { id, ...updates } = body;

    if (!id) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: '取引IDが必要です',
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
        },
      }, { status: 400 });
    }

    const nisaManager = new NisaManager();
    await nisaManager.initialize();

    const validation = await nisaManager.storage.updateTransaction(id, updates);
    
    if (!validation.isValid) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'UPDATE_ERROR',
          message: '取引記録の更新に失敗しました',
          details: validation.errors,
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
        },
      }, { status: 400 });
    }

    return NextResponse.json({
      success: true,
      data: {
        message: '取引記録が正常に更新されました',
        warnings: validation.warnings,
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    });

  } catch (error) {
    console.error('取引記録更新エラー:', error);
    return NextResponse.json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'サーバー内部エラーが発生しました',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: '取引IDが必要です',
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
        },
      }, { status: 400 });
    }

    const nisaManager = new NisaManager();
    await nisaManager.initialize();

    const validation = await nisaManager.storage.deleteTransaction(id);
    
    if (!validation.isValid) {
      return NextResponse.json({
        success: false,
        error: {
          code: 'DELETE_ERROR',
          message: '取引記録の削除に失敗しました',
          details: validation.errors,
        },
        metadata: {
          timestamp: new Date().toISOString(),
          version: '1.0.0',
        },
      }, { status: 400 });
    }

    return NextResponse.json({
      success: true,
      data: {
        message: '取引記録が正常に削除されました',
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    });

  } catch (error) {
    console.error('取引記録削除エラー:', error);
    return NextResponse.json({
      success: false,
      error: {
        code: 'INTERNAL_ERROR',
        message: 'サーバー内部エラーが発生しました',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      metadata: {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
      },
    }, { status: 500 });
  }
}
