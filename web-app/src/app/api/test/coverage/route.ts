import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { readFile } from 'fs/promises';
import { join } from 'path';

const execAsync = promisify(exec);

// 動的レンダリングを強制
export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    // カバレッジレポートの生成
    const { stdout, stderr } = await execAsync('npm run test:coverage', {
      cwd: process.cwd(),
      timeout: 300000, // 5分のタイムアウト
    });

    // カバレッジレポートの読み込み
    try {
      const coveragePath = join(process.cwd(), 'coverage', 'coverage-final.json');
      const coverageData = await readFile(coveragePath, 'utf-8');
      const coverage = JSON.parse(coverageData);

      // カバレッジ統計の計算
      const stats = calculateCoverageStats(coverage);

      return NextResponse.json({
        success: true,
        stats,
        raw: coverage,
        output: stdout,
        error: stderr,
      });
    } catch (error) {
      return NextResponse.json({
        success: false,
        message: 'Coverage report not found after generation.',
        output: stdout,
        error: stderr,
      });
    }
  } catch (error) {
    console.error('Coverage generation error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

function calculateCoverageStats(coverage: any) {
  let totalStatements = 0;
  let coveredStatements = 0;
  let totalBranches = 0;
  let coveredBranches = 0;
  let totalFunctions = 0;
  let coveredFunctions = 0;
  let totalLines = 0;
  let coveredLines = 0;

  Object.values(coverage).forEach((file: any) => {
    if (file.s) {
      totalStatements += Object.keys(file.s).length;
      coveredStatements += Object.values(file.s).filter((count: any) => count > 0).length;
    }
    if (file.b) {
      totalBranches += Object.keys(file.b).length;
      coveredBranches += Object.values(file.b).filter((counts: any) => 
        Array.isArray(counts) ? counts.some((count: any) => count > 0) : counts > 0
      ).length;
    }
    if (file.f) {
      totalFunctions += Object.keys(file.f).length;
      coveredFunctions += Object.values(file.f).filter((count: any) => count > 0).length;
    }
    if (file.l) {
      totalLines += Object.keys(file.l).length;
      coveredLines += Object.values(file.l).filter((count: any) => count > 0).length;
    }
  });

  return {
    statements: {
      total: totalStatements,
      covered: coveredStatements,
      percentage: totalStatements > 0 ? (coveredStatements / totalStatements) * 100 : 0,
    },
    branches: {
      total: totalBranches,
      covered: coveredBranches,
      percentage: totalBranches > 0 ? (coveredBranches / totalBranches) * 100 : 0,
    },
    functions: {
      total: totalFunctions,
      covered: coveredFunctions,
      percentage: totalFunctions > 0 ? (coveredFunctions / totalFunctions) * 100 : 0,
    },
    lines: {
      total: totalLines,
      covered: coveredLines,
      percentage: totalLines > 0 ? (coveredLines / totalLines) * 100 : 0,
    },
  };
}
