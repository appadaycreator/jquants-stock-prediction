import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { testType = 'all' } = await request.json();
    
    let command: string;
    switch (testType) {
      case 'coverage':
        command = 'npm run test:coverage';
        break;
      case 'watch':
        command = 'npm run test:watch';
        break;
      default:
        command = 'npm test';
    }

    const { stdout, stderr } = await execAsync(command, {
      cwd: process.cwd(),
      timeout: 300000, // 5分のタイムアウト
    });

    return NextResponse.json({
      success: true,
      output: stdout,
      error: stderr,
      testType,
    });
  } catch (error) {
    console.error('Test execution error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // カバレッジレポートの読み込み
    const fs = await import('fs/promises');
    const path = await import('path');
    
    const coveragePath = path.join(process.cwd(), 'coverage', 'coverage-final.json');
    
    try {
      const coverageData = await fs.readFile(coveragePath, 'utf-8');
      const coverage = JSON.parse(coverageData);
      
      return NextResponse.json({
        success: true,
        coverage,
      });
    } catch (error) {
      return NextResponse.json({
        success: false,
        message: 'Coverage report not found. Run tests with coverage first.',
      });
    }
  } catch (error) {
    console.error('Coverage reading error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
