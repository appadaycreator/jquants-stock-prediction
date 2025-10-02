/**
 * CORS問題を解消するプロキシサーバー
 * J-Quants APIへのリクエストを中継し、CORSエラーを回避
 */

import { NextRequest, NextResponse } from 'next/server';

const JQUANTS_BASE_URL = 'https://api.jquants.com/v1';
const ALLOWED_ORIGINS = [
  'http://localhost:3000',
  'https://jquants-stock-prediction.vercel.app',
  'https://jquants-stock-prediction.netlify.app',
];

export async function GET(request: NextRequest) {
  return handleRequest(request, 'GET');
}

export async function POST(request: NextRequest) {
  return handleRequest(request, 'POST');
}

export async function PUT(request: NextRequest) {
  return handleRequest(request, 'PUT');
}

export async function DELETE(request: NextRequest) {
  return handleRequest(request, 'DELETE');
}

async function handleRequest(request: NextRequest, method: string) {
  try {
    const origin = request.headers.get('origin');
    
    // CORSヘッダーの設定
    const corsHeaders = {
      'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin || '') ? origin! : '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
      'Access-Control-Max-Age': '86400',
    };

    // OPTIONSリクエストの処理
    if (method === 'OPTIONS') {
      return new NextResponse(null, { status: 200, headers: corsHeaders });
    }

    // リクエストパラメータの取得
    const { searchParams } = new URL(request.url);
    const endpoint = searchParams.get('endpoint');
    
    if (!endpoint) {
      return NextResponse.json(
        { error: 'エンドポイントが指定されていません' },
        { status: 400, headers: corsHeaders }
      );
    }

    // J-Quants APIへのリクエスト構築
    const targetUrl = `${JQUANTS_BASE_URL}/${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // 認証ヘッダーの転送
    const authHeader = request.headers.get('authorization');
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }

    // リクエストボディの取得
    let body: string | undefined;
    if (method !== 'GET' && method !== 'DELETE') {
      try {
        body = await request.text();
      } catch (error) {
        console.warn('リクエストボディの取得に失敗:', error);
      }
    }

    // J-Quants APIへのリクエスト実行
    const response = await fetch(targetUrl, {
      method,
      headers,
      body,
      signal: AbortSignal.timeout(30000), // 30秒タイムアウト
    });

    // レスポンスの処理
    const responseData = await response.text();
    let jsonData;
    
    try {
      jsonData = JSON.parse(responseData);
    } catch {
      jsonData = responseData;
    }

    // エラーハンドリング
    if (!response.ok) {
      console.error('J-Quants API エラー:', {
        status: response.status,
        statusText: response.statusText,
        data: jsonData,
      });

      return NextResponse.json(
        {
          error: 'J-Quants API エラー',
          status: response.status,
          message: response.statusText,
          details: jsonData,
        },
        { 
          status: response.status,
          headers: corsHeaders 
        }
      );
    }

    // 成功レスポンス
    return NextResponse.json(jsonData, {
      status: 200,
      headers: corsHeaders,
    });

  } catch (error) {
    console.error('プロキシサーバーエラー:', error);
    
    return NextResponse.json(
      {
        error: 'プロキシサーバーエラー',
        message: error instanceof Error ? error.message : '不明なエラー',
      },
      { 
        status: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        }
      }
    );
  }
}
