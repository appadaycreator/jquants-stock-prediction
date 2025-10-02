#!/usr/bin/env python3
"""
デプロイ事前チェックシステム
GitHubデプロイ時のリンターエラー、コンソールエラーを事前に検出
"""

import os
import sys
import subprocess
import json
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """チェックステータス"""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class CheckResult:
    """チェック結果"""
    check_name: str
    status: CheckStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class DeploymentPrecheckSystem:
    """デプロイ事前チェックシステム"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初期化"""
        self.config = config or {}
        self.check_results = []
        self.project_root = self.config.get("project_root", ".")
        self.web_app_root = os.path.join(self.project_root, "web-app")
        
        # チェック設定
        self.enable_python_checks = self.config.get("enable_python_checks", True)
        self.enable_typescript_checks = self.config.get("enable_typescript_checks", True)
        self.enable_build_checks = self.config.get("enable_build_checks", True)
        self.enable_security_checks = self.config.get("enable_security_checks", True)
        
        logger.info("🔍 デプロイ事前チェックシステムを初期化しました")

    def run_all_checks(self) -> Dict[str, Any]:
        """全チェックの実行"""
        logger.info("🚀 デプロイ事前チェックを開始します...")
        
        self.check_results = []
        
        # Python関連チェック
        if self.enable_python_checks:
            self._check_python_linting()
            self._check_python_imports()
            self._check_python_security()
        
        # TypeScript/JavaScript関連チェック
        if self.enable_typescript_checks:
            self._check_typescript_linting()
            self._check_typescript_types()
            self._check_javascript_console_errors()
        
        # ビルド関連チェック
        if self.enable_build_checks:
            self._check_build_process()
            self._check_dependencies()
        
        # セキュリティチェック
        if self.enable_security_checks:
            self._check_security_vulnerabilities()
            self._check_sensitive_data()
        
        # 結果の集計
        return self._generate_summary()

    def _check_python_linting(self):
        """Pythonリンターチェック"""
        try:
            logger.info("🐍 Pythonリンターチェックを実行中...")
            
            # flake8チェック
            result = subprocess.run(
                ["flake8", "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.check_results.append(CheckResult(
                    check_name="Python Linting (flake8)",
                    status=CheckStatus.PASS,
                    message="Pythonリンターチェックに問題はありません"
                ))
            else:
                self.check_results.append(CheckResult(
                    check_name="Python Linting (flake8)",
                    status=CheckStatus.FAIL,
                    message=f"Pythonリンターエラーが検出されました: {result.stdout}",
                    suggestions=["flake8エラーを修正してください", "コードフォーマットを実行してください"]
                ))
            
            # Blackフォーマットチェック
            result = subprocess.run(
                ["black", "--check", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.check_results.append(CheckResult(
                    check_name="Python Formatting (black)",
                    status=CheckStatus.PASS,
                    message="Pythonコードフォーマットは正しいです"
                ))
            else:
                self.check_results.append(CheckResult(
                    check_name="Python Formatting (black)",
                    status=CheckStatus.WARNING,
                    message="Pythonコードフォーマットに問題があります",
                    suggestions=["black . を実行してフォーマットを修正してください"]
                ))
                
        except FileNotFoundError:
            self.check_results.append(CheckResult(
                check_name="Python Linting",
                status=CheckStatus.SKIP,
                message="flake8またはblackが見つかりません"
            ))
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="Python Linting",
                status=CheckStatus.FAIL,
                message=f"Pythonリンターチェック中にエラーが発生: {e}"
            ))

    def _check_python_imports(self):
        """Pythonインポートチェック"""
        try:
            logger.info("📦 Pythonインポートチェックを実行中...")
            
            # 主要ファイルのインポートチェック
            main_files = [
                "unified_system.py",
                # "unified_jquants_system.py",  # 削除済み
                "enhanced_ai_prediction_system.py"
            ]
            
            import_errors = []
            
            for file_name in main_files:
                file_path = os.path.join(self.project_root, file_name)
                if os.path.exists(file_path):
                    result = subprocess.run(
                        ["python", "-m", "py_compile", file_path],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        import_errors.append(f"{file_name}: {result.stderr}")
            
            if not import_errors:
                self.check_results.append(CheckResult(
                    check_name="Python Imports",
                    status=CheckStatus.PASS,
                    message="Pythonインポートに問題はありません"
                ))
            else:
                self.check_results.append(CheckResult(
                    check_name="Python Imports",
                    status=CheckStatus.FAIL,
                    message=f"Pythonインポートエラーが検出されました: {import_errors}",
                    suggestions=["不足している依存関係をインストールしてください", "インポートパスを確認してください"]
                ))
                
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="Python Imports",
                status=CheckStatus.FAIL,
                message=f"Pythonインポートチェック中にエラーが発生: {e}"
            ))

    def _check_python_security(self):
        """Pythonセキュリティチェック"""
        try:
            logger.info("🔒 Pythonセキュリティチェックを実行中...")
            
            # banditセキュリティチェック
            result = subprocess.run(
                ["bandit", "-r", ".", "-f", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.check_results.append(CheckResult(
                    check_name="Python Security (bandit)",
                    status=CheckStatus.PASS,
                    message="Pythonセキュリティチェックに問題はありません"
                ))
            else:
                try:
                    security_data = json.loads(result.stdout)
                    issues = security_data.get("results", [])
                    
                    if issues:
                        self.check_results.append(CheckResult(
                            check_name="Python Security (bandit)",
                            status=CheckStatus.WARNING,
                            message=f"Pythonセキュリティ問題が検出されました: {len(issues)}件",
                            details={"issues": issues},
                            suggestions=["セキュリティ問題を修正してください"]
                        ))
                    else:
                        self.check_results.append(CheckResult(
                            check_name="Python Security (bandit)",
                            status=CheckStatus.PASS,
                            message="Pythonセキュリティチェックに問題はありません"
                        ))
                except json.JSONDecodeError:
                    self.check_results.append(CheckResult(
                        check_name="Python Security (bandit)",
                        status=CheckStatus.WARNING,
                        message="セキュリティチェック結果の解析に失敗しました"
                    ))
                    
        except FileNotFoundError:
            self.check_results.append(CheckResult(
                check_name="Python Security",
                status=CheckStatus.SKIP,
                message="banditが見つかりません"
            ))
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="Python Security",
                status=CheckStatus.FAIL,
                message=f"Pythonセキュリティチェック中にエラーが発生: {e}"
            ))

    def _check_typescript_linting(self):
        """TypeScriptリンターチェック"""
        try:
            logger.info("📝 TypeScriptリンターチェックを実行中...")
            
            if not os.path.exists(self.web_app_root):
                self.check_results.append(CheckResult(
                    check_name="TypeScript Linting",
                    status=CheckStatus.SKIP,
                    message="web-appディレクトリが見つかりません"
                ))
                return
            
            # ESLintチェック
            result = subprocess.run(
                ["npm", "run", "lint"],
                cwd=self.web_app_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.check_results.append(CheckResult(
                    check_name="TypeScript Linting (ESLint)",
                    status=CheckStatus.PASS,
                    message="TypeScriptリンターチェックに問題はありません"
                ))
            else:
                self.check_results.append(CheckResult(
                    check_name="TypeScript Linting (ESLint)",
                    status=CheckStatus.FAIL,
                    message=f"TypeScriptリンターエラーが検出されました: {result.stdout}",
                    suggestions=["ESLintエラーを修正してください", "npm run lint:fix を実行してください"]
                ))
                
        except FileNotFoundError:
            self.check_results.append(CheckResult(
                check_name="TypeScript Linting",
                status=CheckStatus.SKIP,
                message="npmまたはESLintが見つかりません"
            ))
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="TypeScript Linting",
                status=CheckStatus.FAIL,
                message=f"TypeScriptリンターチェック中にエラーが発生: {e}"
            ))

    def _check_typescript_types(self):
        """TypeScript型チェック"""
        try:
            logger.info("🔍 TypeScript型チェックを実行中...")
            
            if not os.path.exists(self.web_app_root):
                self.check_results.append(CheckResult(
                    check_name="TypeScript Types",
                    status=CheckStatus.SKIP,
                    message="web-appディレクトリが見つかりません"
                ))
                return
            
            # TypeScript型チェック
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=self.web_app_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.check_results.append(CheckResult(
                    check_name="TypeScript Types",
                    status=CheckStatus.PASS,
                    message="TypeScript型チェックに問題はありません"
                ))
            else:
                self.check_results.append(CheckResult(
                    check_name="TypeScript Types",
                    status=CheckStatus.FAIL,
                    message=f"TypeScript型エラーが検出されました: {result.stdout}",
                    suggestions=["型エラーを修正してください", "型定義を追加してください"]
                ))
                
        except FileNotFoundError:
            self.check_results.append(CheckResult(
                check_name="TypeScript Types",
                status=CheckStatus.SKIP,
                message="TypeScriptコンパイラが見つかりません"
            ))
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="TypeScript Types",
                status=CheckStatus.FAIL,
                message=f"TypeScript型チェック中にエラーが発生: {e}"
            ))

    def _check_javascript_console_errors(self):
        """JavaScriptコンソールエラーチェック"""
        try:
            logger.info("🖥️ JavaScriptコンソールエラーチェックを実行中...")
            
            if not os.path.exists(self.web_app_root):
                self.check_results.append(CheckResult(
                    check_name="JavaScript Console Errors",
                    status=CheckStatus.SKIP,
                    message="web-appディレクトリが見つかりません"
                ))
                return
            
            # コンソールエラーのパターン
            console_error_patterns = [
                r'console\.error\(',
                r'console\.warn\(',
                r'throw new Error\(',
                r'Error:',
                r'TypeError:',
                r'ReferenceError:',
                r'SyntaxError:'
            ]
            
            error_files = []
            
            # TypeScript/JavaScriptファイルをスキャン
            for root, dirs, files in os.walk(self.web_app_root):
                for file in files:
                    if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                for pattern in console_error_patterns:
                                    if re.search(pattern, content):
                                        error_files.append(file_path)
                                        break
                        except Exception:
                            continue
            
            if not error_files:
                self.check_results.append(CheckResult(
                    check_name="JavaScript Console Errors",
                    status=CheckStatus.PASS,
                    message="JavaScriptコンソールエラーのパターンは検出されませんでした"
                ))
            else:
                self.check_results.append(CheckResult(
                    check_name="JavaScript Console Errors",
                    status=CheckStatus.WARNING,
                    message=f"JavaScriptコンソールエラーのパターンが検出されました: {len(error_files)}ファイル",
                    details={"error_files": error_files},
                    suggestions=["コンソールエラーを修正してください", "エラーハンドリングを追加してください"]
                ))
                
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="JavaScript Console Errors",
                status=CheckStatus.FAIL,
                message=f"JavaScriptコンソールエラーチェック中にエラーが発生: {e}"
            ))

    def _check_build_process(self):
        """ビルドプロセスのチェック"""
        try:
            logger.info("🔨 ビルドプロセスのチェックを実行中...")
            
            if not os.path.exists(self.web_app_root):
                self.check_results.append(CheckResult(
                    check_name="Build Process",
                    status=CheckStatus.SKIP,
                    message="web-appディレクトリが見つかりません"
                ))
                return
            
            # Next.jsビルドチェック
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=self.web_app_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.check_results.append(CheckResult(
                    check_name="Build Process",
                    status=CheckStatus.PASS,
                    message="ビルドプロセスは正常に完了しました"
                ))
            else:
                self.check_results.append(CheckResult(
                    check_name="Build Process",
                    status=CheckStatus.FAIL,
                    message=f"ビルドプロセスでエラーが発生しました: {result.stderr}",
                    suggestions=["ビルドエラーを修正してください", "依存関係を確認してください"]
                ))
                
        except FileNotFoundError:
            self.check_results.append(CheckResult(
                check_name="Build Process",
                status=CheckStatus.SKIP,
                message="npmが見つかりません"
            ))
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="Build Process",
                status=CheckStatus.FAIL,
                message=f"ビルドプロセスのチェック中にエラーが発生: {e}"
            ))

    def _check_dependencies(self):
        """依存関係のチェック"""
        try:
            logger.info("📦 依存関係のチェックを実行中...")
            
            # Python依存関係
            if os.path.exists(os.path.join(self.project_root, "requirements.txt")):
                result = subprocess.run(
                    ["pip", "check"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.check_results.append(CheckResult(
                        check_name="Python Dependencies",
                        status=CheckStatus.PASS,
                        message="Python依存関係に問題はありません"
                    ))
                else:
                    self.check_results.append(CheckResult(
                        check_name="Python Dependencies",
                        status=CheckStatus.WARNING,
                        message=f"Python依存関係に問題があります: {result.stdout}",
                        suggestions=["依存関係の競合を解決してください"]
                    ))
            
            # Node.js依存関係
            if os.path.exists(self.web_app_root):
                result = subprocess.run(
                    ["npm", "audit"],
                    cwd=self.web_app_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.check_results.append(CheckResult(
                        check_name="Node.js Dependencies",
                        status=CheckStatus.PASS,
                        message="Node.js依存関係に問題はありません"
                    ))
                else:
                    self.check_results.append(CheckResult(
                        check_name="Node.js Dependencies",
                        status=CheckStatus.WARNING,
                        message=f"Node.js依存関係に脆弱性があります: {result.stdout}",
                        suggestions=["npm audit fix を実行してください"]
                    ))
                    
        except FileNotFoundError:
            self.check_results.append(CheckResult(
                check_name="Dependencies",
                status=CheckStatus.SKIP,
                message="pipまたはnpmが見つかりません"
            ))
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="Dependencies",
                status=CheckStatus.FAIL,
                message=f"依存関係のチェック中にエラーが発生: {e}"
            ))

    def _check_security_vulnerabilities(self):
        """セキュリティ脆弱性のチェック"""
        try:
            logger.info("🔒 セキュリティ脆弱性のチェックを実行中...")
            
            # Pythonセキュリティチェック
            result = subprocess.run(
                ["safety", "check", "--json"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.check_results.append(CheckResult(
                    check_name="Python Security Vulnerabilities",
                    status=CheckStatus.PASS,
                    message="Pythonセキュリティ脆弱性は検出されませんでした"
                ))
            else:
                try:
                    security_data = json.loads(result.stdout)
                    vulnerabilities = security_data.get("vulnerabilities", [])
                    
                    if vulnerabilities:
                        self.check_results.append(CheckResult(
                            check_name="Python Security Vulnerabilities",
                            status=CheckStatus.FAIL,
                            message=f"Pythonセキュリティ脆弱性が検出されました: {len(vulnerabilities)}件",
                            details={"vulnerabilities": vulnerabilities},
                            suggestions=["脆弱性のあるパッケージを更新してください"]
                        ))
                    else:
                        self.check_results.append(CheckResult(
                            check_name="Python Security Vulnerabilities",
                            status=CheckStatus.PASS,
                            message="Pythonセキュリティ脆弱性は検出されませんでした"
                        ))
                except json.JSONDecodeError:
                    self.check_results.append(CheckResult(
                        check_name="Python Security Vulnerabilities",
                        status=CheckStatus.WARNING,
                        message="セキュリティチェック結果の解析に失敗しました"
                    ))
                    
        except FileNotFoundError:
            self.check_results.append(CheckResult(
                check_name="Security Vulnerabilities",
                status=CheckStatus.SKIP,
                message="safetyが見つかりません"
            ))
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="Security Vulnerabilities",
                status=CheckStatus.FAIL,
                message=f"セキュリティ脆弱性のチェック中にエラーが発生: {e}"
            ))

    def _check_sensitive_data(self):
        """機密データのチェック"""
        try:
            logger.info("🔐 機密データのチェックを実行中...")
            
            # 機密データのパターン
            sensitive_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'private_key\s*=\s*["\'][^"\']+["\']'
            ]
            
            sensitive_files = []
            
            # ファイルをスキャン
            for root, dirs, files in os.walk(self.project_root):
                # .gitディレクトリをスキップ
                dirs[:] = [d for d in dirs if d != '.git']
                
                for file in files:
                    if file.endswith(('.py', '.js', '.ts', '.json', '.yaml', '.yml')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                for pattern in sensitive_patterns:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        sensitive_files.append(file_path)
                                        break
                        except Exception:
                            continue
            
            if not sensitive_files:
                self.check_results.append(CheckResult(
                    check_name="Sensitive Data",
                    status=CheckStatus.PASS,
                    message="機密データのパターンは検出されませんでした"
                ))
            else:
                self.check_results.append(CheckResult(
                    check_name="Sensitive Data",
                    status=CheckStatus.FAIL,
                    message=f"機密データのパターンが検出されました: {len(sensitive_files)}ファイル",
                    details={"sensitive_files": sensitive_files},
                    suggestions=["機密データを環境変数に移動してください", "機密データをマスキングしてください"]
                ))
                
        except Exception as e:
            self.check_results.append(CheckResult(
                check_name="Sensitive Data",
                status=CheckStatus.FAIL,
                message=f"機密データのチェック中にエラーが発生: {e}"
            ))

    def _generate_summary(self) -> Dict[str, Any]:
        """チェック結果のサマリー生成"""
        total_checks = len(self.check_results)
        passed_checks = len([r for r in self.check_results if r.status == CheckStatus.PASS])
        warning_checks = len([r for r in self.check_results if r.status == CheckStatus.WARNING])
        failed_checks = len([r for r in self.check_results if r.status == CheckStatus.FAIL])
        skipped_checks = len([r for r in self.check_results if r.status == CheckStatus.SKIP])
        
        # デプロイ可否の判定
        deployable = failed_checks == 0
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "warning_checks": warning_checks,
            "failed_checks": failed_checks,
            "skipped_checks": skipped_checks,
            "deployable": deployable,
            "results": [
                {
                    "check_name": result.check_name,
                    "status": result.status.value,
                    "message": result.message,
                    "details": result.details,
                    "suggestions": result.suggestions
                }
                for result in self.check_results
            ]
        }
        
        # ログ出力
        if deployable:
            logger.info("✅ デプロイ事前チェック完了: デプロイ可能です")
        else:
            logger.error("❌ デプロイ事前チェック完了: デプロイ不可です")
        
        return summary

    def export_report(self, file_path: str) -> bool:
        """チェックレポートのエクスポート"""
        try:
            summary = self._generate_summary()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📊 デプロイ事前チェックレポートをエクスポートしました: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ レポートのエクスポートに失敗: {e}")
            return False


def main():
    """メイン関数"""
    # 設定
    config = {
        "project_root": ".",
        "enable_python_checks": True,
        "enable_typescript_checks": True,
        "enable_build_checks": True,
        "enable_security_checks": True
    }
    
    # チェックシステムの初期化
    checker = DeploymentPrecheckSystem(config)
    
    # 全チェックの実行
    summary = checker.run_all_checks()
    
    # レポートのエクスポート
    checker.export_report("deployment_precheck_report.json")
    
    # 結果の表示
    print(f"\n📊 デプロイ事前チェック結果:")
    print(f"総チェック数: {summary['total_checks']}")
    print(f"成功: {summary['passed_checks']}")
    print(f"警告: {summary['warning_checks']}")
    print(f"失敗: {summary['failed_checks']}")
    print(f"スキップ: {summary['skipped_checks']}")
    print(f"デプロイ可否: {'✅ 可能' if summary['deployable'] else '❌ 不可'}")
    
    # 失敗したチェックの詳細表示
    if summary['failed_checks'] > 0:
        print(f"\n❌ 失敗したチェック:")
        for result in summary['results']:
            if result['status'] == 'fail':
                print(f"  - {result['check_name']}: {result['message']}")
                if result['suggestions']:
                    for suggestion in result['suggestions']:
                        print(f"    💡 {suggestion}")
    
    return summary['deployable']


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
